import re
import subprocess
from contextlib import contextmanager

import jsonpickle
import os

from ppi import console
from ppi.local_cmds import BUILD, PUBLISH_TO_PYPI
from .version import __version__

logger = console


def update_local_version_file_version(version):
    """ Update version in version.py named version"""
    if os.path.exists('version.py'):
        version = Version(version)
        file_content = open('version.py').read()
        reg = re.compile('(VERSION|__version__)*=*\'(.*?)\'')
        file_content, number = reg.subn("'{}'".format(version.view), file_content)
        open('version.py', 'w').write(file_content)


def update_local_setup_file_version(version):
    """ Update setup.py option version"""
    if os.path.exists('setup.py'):
        version = Version(version)
        file_content = open('setup.py').read()
        reg = re.compile('version=\'(.*?)\'')
        file_content, number = reg.subn("version='{}'".format(version.view), file_content)
        open('setup.py', 'w').write(file_content)


jsonpickle.set_encoder_options('json', sort_keys=True, indent=2)
jsonpickle.set_preferred_backend('json')


def update_int(value, MAX=10):
    return (value + 1) / MAX == 1, (value + 1) % MAX


class Version(object):
    """ Represent a version with major, minor, build parts"""

    def __init__(self, value):
        console.debug('[Version] [init] value: {}'.format(value))
        if isinstance(value, str):
            value = tuple(value.split('.'))
            value = tuple([int(x) for x in value])

        if isinstance(value, Version):
            value = value.value

        if isinstance(value, tuple):
            if not len(value) == 3:
                raise AssertionError('value must be tuple and length must be 3')

        self.value = value

    @property
    def major(self):
        return self.value[0]

    @major.setter
    def major(self, value):
        self.value = (value, self.build, self.build)

    @property
    def minor(self):
        return self.value[1]

    @minor.setter
    def minor(self, value):
        self.value = (self.major, value, self.build)

    @property
    def build(self):
        return self.value[2]

    @build.setter
    def build(self, value):
        self.value = (self.major, self.minor, value)

    @property
    def view(self):
        return '.'.join([str(x) for x in self.value])

    def __eq__(self, other):
        if isinstance(other, str):
            return self.view == other
        if isinstance(other, tuple):
            return Version(other).view == self.view
        if isinstance(other, Version):
            return self.view == other.view
        raise TypeError('not support type')

    def __str__(self):
        return self.view

    def update_major(self):
        self.build = 0
        self.minor = 0
        self.major = self.major + 1

    def update_minor(self):
        self.build = 0
        u_major, self.minor = update_int(self.minor)
        if u_major:
            self.major = self.major + 1

    def update_build(self):
        major, minor, build = self.value
        new_major, new_minor, new_build = None, None, None

        u_minor, new_build = update_int(build)
        if u_minor:
            u_major, new_minor = update_int(minor)
            if u_major:
                u_max, new_major = update_int(major)
                if u_max:
                    new_major = new_major + 1

        self.major = new_major if new_major is not None else major
        self.minor = new_minor if new_minor is not None else minor
        self.build = new_build

    @staticmethod
    def from_version_file():
        """ Parse version from version.py"""
        if not os.path.exists('version.py'):
            return None

        reg = re.compile('__version__ = \'(.*?)\'')
        match = reg.match(open('version.py', 'r').read())

        if match:
            _value = match.group(1)
            return Version(_value)
        return None

    @staticmethod
    def from_setup_file():
        """ Parse version from setup.py"""
        if not os.path.exists('setup.py'):
            return None

        reg = re.compile('version=\'(.*?)\'')
        match = reg.match(open('setup.py', 'r').read())
        if match:
            _value = match.group(1)
            return Version(_value)
        return None


class Project(object):
    filename = '.ppi.json'

    def __init__(self,
                 name,
                 version=None,
                 publisher_version=None):
        self.name = name
        self.version = version or self.version()
        self.publisher_version = publisher_version or self._publisher_version()

    def _publisher_version(self):
        return Version(__version__)

    def version(self):
        return Version.from_setup_file() or Version.from_version_file()

    @staticmethod
    def _project_path():
        return os.path.join(os.path.abspath(os.curdir), Project.filename)

    @staticmethod
    def init(force=False, version=None):
        project_name = os.path.split(os.path.abspath(os.curdir))[-1]
        project = Project(project_name, version=version)
        if project.version is None:
            version = input('Input your project version (default: 0.0.1): ')
            if version is None or version == "":
                version = '0.0.1'
            project.version = Version(version)

        project.save(force)
        return project

    def save(self, force=False):
        if os.path.exists(Project._project_path()) and not force:
            console.error('project has been initialized !')
            return
        return open(Project._project_path(), 'w').write(jsonpickle.encode(self))

    @staticmethod
    def parse() -> 'Project':
        if not os.path.exists(Project._project_path()):
            raise FileNotFoundError("You have to init first")
        js = open(Project._project_path(), 'r').read()
        return jsonpickle.decode(js, classes=[Project, Version])


class LocalCommandExecutor(object):
    """ Local Command Executor"""

    def __init__(self):
        self._cmds = {}
        self._is_in_together = False

    @property
    def ok(self):
        s = set(self._cmds.values())
        return len(s) == 1 and list(s)[0] is True

    @contextmanager
    def together(self, abort=True, clean=False):
        """ Provide a context to execute some commands together"""
        self._is_in_together = True

        yield

        self._is_in_together = False

        for key, val in self._cmds.items():
            r = self._run(key)
            self._cmds[key] = r
            if r is False and abort:
                console.error('[CMD] error when execute : {}'.format(key))
                return
        if not clean:
            self._save_session()
        else:
            self._cmds.clear()

    def go_continue(self):
        """ Continue to execute last abort commands"""
        # TODO:
        pass

    def _save_session(self):
        # TODO:
        pass

    def run(self, cmd):
        if self._is_in_together:
            self._cmds[cmd] = None
        else:
            return self._run(cmd)

    def _run(self, cmd):
        console.debug('[CMD] {}'.format(cmd))
        if isinstance(cmd, str):
            cmd = cmd.split(' ')
        result = subprocess.Popen(cmd).wait()
        console.debug("[CMD] [RESULT] {}".format(result))
        return True if result == 0 else False


class Publisher(object):
    """ Represent then main operator"""

    def __init__(self, project: Project = None, cmder: LocalCommandExecutor = None):
        self.project = project or Project.parse()
        self.cmder = cmder or LocalCommandExecutor()

    def update(self, major=False, minor=False, build=True):
        if major:
            self.project.version.update_major()
        if minor:
            self.project.version.update_minor()
        if build:
            self.project.version.update_build()

        self._update_local_version(self.project.version)

    def build(self):
        self.cmder.run(BUILD)

    def publish(self):
        """
        Publish a version to pypi
        """
        self.publish_to_pypi()

    def _update_local_version(self, v):
        """ Update local file version"""
        self._update_ppi_file(v)
        update_local_version_file_version(v)
        update_local_setup_file_version(v)

    def _update_ppi_file(self, v):
        self.project.version = v
        self.project.save(force=True)

    def publish_to_pypi(self):
        self.cmder.run(PUBLISH_TO_PYPI.format(project_name=self.project.name, version=self.project.version))
