#!/usr/bin/env python
# dostack.py
from doutils import DockerConfig, container_uri, try_docker
from dotempl import TemplatedFilePath 
import click

@click.group()
def dostack():
    pass

@dostack.command()
@click.option('--registry',         default=None,            type=click.STRING,    envvar='DOSTACK_REGISTRY')
@click.option('--prefix',           default=None,            type=click.STRING,    envvar='DOSTACK_PREFIX')
@click.option('--tag',              default='latest',        type=click.STRING,    envvar='DOSTACK_TAG')
@click.option('--searchpath',       default='./stacks/',     type=click.Path(file_okay=False, dir_okay=True), envvar='DOSTACK_SEARCHPATH')
@click.argument('stackname',                                 type=click.STRING,    envvar='DOSTACK_STACKNAME')
@click.argument('stackfile',                                 type=click.File('r'), envvar='DOSTACK_STACKFILE')
def up(registry, prefix, tag, searchpath, stackname, stackfile):
    # Docker config
    config = DockerConfig(registry, prefix, tag)

    with TemplatedFilePath(config, stackfile, searchpath) as stackpath:
        try_docker('stack', 'deploy', '--with-registry-auth', '-c', stackpath, stackname, _fg=True, _tty_out=True)


@dostack.command()
@click.argument('stackname', type=click.STRING, envvar='DOSTACK_STACKNAME')
def down(stackname):
    try_docker('stack', 'rm', stackname, _fg=True, _tty_out=True)
