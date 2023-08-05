# coding=utf-8

import click
import os

from ppi import console
from ppi.core import Project, Publisher

os.environ.setdefault('LC_ALL', 'zh_CN.UTF-8')
os.environ.setdefault('LANG', 'zh_CN.UTF-8')


@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
def cli(debug=False):
    console.DEBUG = debug


@cli.command()
@click.option('--force/--no-force', default=False)
@click.option('--version', default=None)
@click.option('--github', prompt=True)
def init(force=False, version=None, github=None):
    """ Initialize a ppi.json file"""
    Project.init(force=force, version=version, github=github)


@cli.command()
@click.option('--github', default=None)
def config(github=None):
    """ Config ppi.json"""
    project = Project.parse()

    if github:
        project.github = github


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
@click.option('--github/--no-github', default=False)
@click.option('--pypi/--no-pypi', default=False)
def publish(github=False, pypi=False):
    """ Publish to github, pypi"""
    project = Project.parse()
    publisher = Publisher(project)
    if github is False and pypi is False:
        github = pypi = True
    publisher.publish(github=github, pypi=pypi)


if __name__ == '__main__':
    cli()
