from datetime import timedelta
from glob import glob
import os
from urlparse import urlparse, parse_qs
from munch import munchify
from twisted.web.xmlrpc import Proxy
from twisted.internet import defer
try:
    from configparser import SafeConfigParser
    import xmlrpc
except ImportError:
    from ConfigParser import SafeConfigParser
    import xmlrpclib as xmlrpc
from txkoji.query_factory import KojiQueryFactory
from txkoji.task import Task
from txkoji.build import Build
from txkoji.package import Package


__version__ = '0.1.0'


PROFILES = '/etc/koji.conf.d/*.conf'


class Call(object):
    """ Callable abstract class representing a Koji RPC, eg "getTag". """
    def __init__(self, connection, name):
        self.connection = connection
        self.name = name

    def __call__(self, *args, **kwargs):
        return self.connection.call(self.name, *args, **kwargs)


class Connection(object):

    def __init__(self, profile):
        self.url = self.lookup(profile, 'server')
        self.weburl = self.lookup(profile, 'weburl')
        if not self.url:
            msg = 'no server configured at %s for %s' % (PROFILES, profile)
            raise ValueError(msg)
        self.proxy = Proxy(self.url.encode(), allowNone=True)
        self.proxy.queryFactory = KojiQueryFactory

    def lookup(self, profile, setting):
        """ Check koji.conf.d files for this profile's setting.

        :param setting: ``str`` like "server" (for kojihub) or "weburl"
        :returns: ``str``, value for this setting
        """
        for path in glob(PROFILES):
            cfg = SafeConfigParser()
            cfg.read(path)
            if profile not in cfg.sections():
                continue
            if not cfg.has_option(profile, setting):
                continue
            return cfg.get(profile, setting)

    @classmethod
    def connect_from_web(klass, url):
        """
        Find a connection that matches this kojiweb URL.

        Check all koji.conf.d files' kojiweb URLs and load the profile that
        matches the url we pass in here.

        For example, if a user pastes a kojiweb URL into chat, we want to
        discover the corresponding Koji instance hub automatically.

        :param url: ``str``, for example
                    "http://cbs.centos.org/koji/buildinfo?buildID=21155"
        :returns: A "Connection" instance
        """
        for path in glob(PROFILES):
            cfg = SafeConfigParser()
            cfg.read(path)
            for profile in cfg.sections():
                if not cfg.has_option(profile, 'weburl'):
                    continue
                weburl = cfg.get(profile, 'weburl')
                if weburl in url:
                    return klass(profile)

    @defer.inlineCallbacks
    def from_web(self, url):
        """
        Reverse-engineer a kojiweb URL into an equivalent API response.

        Only a few kojiweb URL endpoints work here.

        See also connect_from_web().

        :param url: ``str``, for example
                    "http://cbs.centos.org/koji/buildinfo?buildID=21155"
        :returns: deferred that when fired returns a Munch (dict-like) object
                  with data about this resource, or None if we could not parse
                  the url.
        """
        o = urlparse(url)
        endpoint = os.path.basename(o.path)
        if o.query:
            query = parse_qs(o.query)
        result = None
        # Known Kojiweb endpoints:
        endpoints = {
            'buildinfo': ('buildID', self.getBuild),
            'packageinfo': ('packageID', self.getPackage),
            'taskinfo': ('taskID', self.getTaskInfo),
            'taginfo': ('tagID', self.getTag),
            'targetinfo': ('targetID', self.getTarget),
            'userinfo': ('userID', self.getUser),
        }
        try:
            (param, method) = endpoints[endpoint]
            id_ = int(query[param][0])
            result = yield method(id_)
        except KeyError:
            pass
        defer.returnValue(result)

    def call(self, method, *args, **kwargs):
        """
        Make an XML-RPC call to the server. This method does not auth to the
        server (TODO).

        Koji has its own custom implementation of XML-RPC that supports named
        args (kwargs). For example, to use the "queryOpts" kwarg:

          d = client.call('listBuilds', package_id,
                          queryOpts={'order': 'creation_ts'})

        In this example, the server will order the list of builds according to
        the "creation_ts" database column. Many of Koji's XML-RPC methods have
        optional kwargs that you can set as needed.

        :returns: deferred that when fired returns a dict with data from this
                  XML-RPC call.
        """
        if kwargs:
            kwargs['__starstar'] = True
            args = args + (kwargs,)
        d = self.proxy.callRemote(method, *args)
        d.addCallback(self._munchify_callback)
        d.addErrback(self._parse_errback)
        return d

    def __getattr__(self, name):
        return Call(self, name)

    @defer.inlineCallbacks
    def getAverageBuildDuration(self, package, **kwargs):
        """
        Return a timedelta that Koji considers to be average for this package.

        Calls "getAverageBuildDuration" XML-RPC.

        :param package: ``str``, for example "ceph"
        :returns: deferred that when fired returns a datetime object for the
                  estimated duration.
        """
        seconds = yield self.call('getAverageBuildDuration', package, **kwargs)
        defer.returnValue(timedelta(seconds=seconds))

    @defer.inlineCallbacks
    def getBuild(self, build_id, **kwargs):
        """
        Load all information about a build and return a custom Build class.

        Calls "getBuild" XML-RPC.

        :param build_id: ``int``, for example 12345
        :returns: deferred that when fired returns a Build (Munch, dict-like)
                  object representing this Koji build, or None if no build was
                  found.
        """
        buildinfo = yield self.call('getBuild', build_id, **kwargs)
        build = Build.fromDict(buildinfo)
        if build:
            build.connection = self
        defer.returnValue(build)

    @defer.inlineCallbacks
    def getPackage(self, name, **kwargs):
        """
        Load information about a package and return a custom Package class.

        Calls "getPackage" XML-RPC.

        :param package_id: ``int``, for example 12345
        :returns: deferred that when fired returns a Package (Munch, dict-like)
                  object representing this Koji package, or None if no build
                  was found.
        """
        packageinfo = yield self.call('getPackage', name, **kwargs)
        package = Package.fromDict(packageinfo)
        if package:
            package.connection = self
        defer.returnValue(package)

    @defer.inlineCallbacks
    def getTaskDescendents(self, task_id, **kwargs):
        """
        Load all information about a task's descendents into Task classes.

        Calls "getTaskDescendents" XML-RPC (with request=True to get the full
        information.)

        :param task_id: ``int``, for example 12345, parent task ID
        :returns: deferred that when fired returns a list of Task (Munch,
                  dict-like) objects representing Koji tasks.
        """
        kwargs['request'] = True
        data = yield self.call('getTaskDescendents', task_id, **kwargs)
        tasks = []
        for tdata in data[str(task_id)]:
            task = Task.fromDict(tdata)
            task.connection = self
            tasks.append(task)
        defer.returnValue(tasks)

    @defer.inlineCallbacks
    def getTaskInfo(self, task_id, **kwargs):
        """
        Load all information about a task and return a custom Task class.

        Calls "getTaskInfo" XML-RPC (with request=True to get the full
        information.)

        :param task_id: ``int``, for example 12345
        :returns: deferred that when fired returns a Task (Munch, dict-like)
                  object representing this Koji task, or none if no task was
                  found.
        """
        kwargs['request'] = True
        taskinfo = yield self.call('getTaskInfo', task_id, **kwargs)
        task = Task.fromDict(taskinfo)
        if task:
            task.connection = self
        defer.returnValue(task)

    @defer.inlineCallbacks
    def listBuilds(self, package, **kwargs):
        """
        Get information about all builds of a package.

        Calls "listBuilds" XML-RPC, with an enhancement: you can also pass a
        string here for the package name instead of the package ID number.

        :param package: ``int`` (packageID) or ``str`` (package name).
        :returns: deferred that when fired returns a list of Build objects
                  for this package.
        """
        if isinstance(package, int):
            package_id = package
        else:
            package_data = yield self.getPackage(package)
            if package_data is None:
                defer.returnValue([])
            package_id = package_data.id
        data = yield self.call('listBuilds', package_id, **kwargs)
        builds = []
        for bdata in data:
            build = Build.fromDict(bdata)
            build.connection = self
            builds.append(build)
        defer.returnValue(builds)

    def _munchify_callback(self, value):
        """
        Fires when we get user information back from the XML-RPC server.

        This is a generic callback for when we do not want to post-process the
        XML-RPC server's data further.

        :param value: dict of data from XML-RPC server.
        :returns: ``Munch`` (dict-like) object
        """
        return munchify(value)

    def _parse_errback(self, error):
        """
        Parse an error from an XML-RPC call.

        raises: ``IOError`` when the Twisted XML-RPC connection times out.
        raises: ``KojiException`` if we got a response from the XML-RPC
                server but it is not one of the ``xmlrpc.Fault``s that
                we know about.
        raises: ``Exception`` if it is not one of the above.
        """
        if isinstance(error.value, IOError):
            raise error.value
        if isinstance(error.value, xmlrpc.Fault):
            # TODO: specific errors here, see koji/__init__.py
            if error.value.faultCode >= 1000 and error.value.faultCode <= 1022:
                raise KojiException(error.value.faultString)
            raise KojiException(error.value)
        # We don't know what this is, so just raise it.
        raise error


class KojiException(Exception):
    pass
