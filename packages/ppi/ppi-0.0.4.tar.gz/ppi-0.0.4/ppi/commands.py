# coding=utf-8

import click
import os

from ppi import console
from ppi.core import Project, Publisher
from .version import __version__

os.environ.setdefault('LC_ALL', 'zh_CN.UTF-8')
os.environ.setdefault('LANG', 'zh_CN.UTF-8')


@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug=False):
    console.DEBUG = debug


@cli.command()
@click.option('--force/--no-force', default=False)
@click.option('--version', default=None)
def init(force=False, version=None):
    """ Initialize a ppi.json file"""
    Project.init(force=force, v=version)


@cli.command()
def config():
    """ Config ppi.json"""
    pass


@cli.command()
@click.option('--major/--no-major', default=False)
@click.option('--minor/--no-minor', default=False)
@click.option('--build/--no-build', default=True)
def update(major=True, minor=True, build=True):
    """ Update a new version"""
    project = Project.parse()
    publisher = Publisher(project)
    publisher.update(major=major, minor=minor, build=build)


@cli.command()
def build():
    project = Project.parse()
    publisher = Publisher(project)
    publisher.build()


@cli.command()
def publish():
    """ Publish to pypi"""
    project = Project.parse()
    publisher = Publisher(project)
    publisher.publish()


@cli.command()
def version():
    """ Show ppi version"""
    click.echo(__version__)


@cli.command()
def gen(file_type):
    """ Generate some files like setup.py"""
    pass


if __name__ == '__main__':
    cli()
