import re
import subprocess

import jsonpickle
import os
import logging

from . import version

from ppi import console

logger = logging.getLogger('ppi')


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



class Version(object):

    def __init__(self, value):
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
                 publisher_version=None,
                 github=None):
        self.name = name
        self.version = version or self._version()
        self.publisher_version = publisher_version or self._publisher_version()
        self.github = github

    def _publisher_version(self):
        return Version(version.__version__)

    def _version(self):
        return Version.from_setup_file() or Version.from_version_file()

    @staticmethod
    def _project_path():
        return os.path.join(os.path.abspath(os.curdir), Project.filename)

    @staticmethod
    def init(force=False, version=None, github=None):
        project_name = os.path.split(os.path.abspath(os.curdir))[-1]
        project = Project(project_name, version=version, github=github)
        if project.version is None:
            version = input('Input your project version')
            project.version = Version(version)
        if not project.github:
            github = input('Input your project github address')
            project.github = github

        project.save(force)
        return project

    def save(self, force=False):
        if os.path.exists(Project._project_path()) and not force:
            raise FileExistsError()
        return open(Project._project_path(), 'w').write(jsonpickle.encode(self))

    @staticmethod
    def parse() -> 'Project':
        if not os.path.exists(Project._project_path()):
            raise FileNotFoundError("You have to init first")
        js = open(Project._project_path(), 'r').read()
        return jsonpickle.decode(js, classes=[Project, Version])


BUILD = 'python setup.py sdist'
TAG_GIT = "git tag {version}"
PUSH_TO_GIT = 'git push --follow-tags'
PUBLISH_TO_PYPI = 'twine upload dist/{project_name}-{version}.tar.gz'


class Publisher(object):

    def __init__(self, project: Project = None):
        self.project = project or Project.parse()

    def _execute_cmd(self, cmd):
        console.debug('[CMD] {}'.format(cmd))
        if isinstance(cmd, str):
            cmd = cmd.split(' ')
        subprocess.Popen(cmd).wait()

    def update(self, major=False, minor=False, build=True):
        if major:
            self.project.version.update_major()
        if minor:
            self.project.version.update_minor()
        if build:
            self.project.version.update_build()

        self._update_local_version(self.project.version)

    def build(self):
        self._execute_cmd(BUILD)

    def publish(self, github=True, pypi=True):
        if github:
            self._tag_git(self.project.version)
            self.push_to_github()
        if pypi:
            self.publish_to_pypi()

    def _tag_git(self, v):
        self._execute_cmd(TAG_GIT.format(version=v))

    def push_to_github(self):
        self._execute_cmd(PUSH_TO_GIT)

    def _update_local_version(self, version):
        """ Update local file version"""
        self._update_ppi_file(version)
        update_local_version_file_version(version)
        update_local_setup_file_version(version)

    def _update_ppi_file(self, version):
        self.project.version = version
        self.project.save(force=True)

    def publish_to_pypi(self):
        self._execute_cmd(PUBLISH_TO_PYPI.format(project_name=self.project.name, version=self.project.version))


def update_int(value):
    return (value + 1) / 10 == 1, (value + 1) % 10
