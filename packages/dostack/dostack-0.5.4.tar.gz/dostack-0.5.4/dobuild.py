#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import sh
import click
import yaml
import dotempl
from doutils import DockerConfig, try_docker, container_uri

def docker_build(context, dockerfile_path, uri=None, pull=False, cache=True, cache_from_uri=None):
    # Optional docker build arguments
    buildargs = []

    if uri is not None:
        buildargs.extend(['--tag', uri])

    if pull:
        buildargs.extend(['--pull'])

    if not cache:
        buildargs.extend(['--no-cache'])
        
    if cache and cache_from_uri is not None:
        buildargs.extend(['--cache-from', cache_from_uri])

    buildargs.append(context)

    
    # Run docker build
    try_docker('build', '--file', dockerfile_path, *buildargs, _fg=True, _tty_out=True)
    
def docker_tag(uri, extra_uri):
    print("Tagging {} => {}".format(uri, extra_uri))
    try_docker('tag', uri, extra_uri, _fg=True, _tty_out=True)


def docker_push(uri):
    try_docker('push', uri, _fg=True, _tty_in=True, _tty_out=True)


class ContainerBuildConfig(object):
    def __init__(self, name, dockerfile, context, depends_on):
        if dockerfile is None:
            dockerfile = os.path.join(context, 'Dockerfile')

        self.name = name
        self.dockerfile = dockerfile
        self.context = context
        self.depends_on = depends_on
        self.built = False
        self.pushed = False

    def __repr__(self):
        return '<ContainerBuildConfig name={} dockerfile={} context={} built={} pushed={}>'.format(
            repr(self.name), repr(self.dockerfile), repr(self.context), repr(self.built), repr(self.pushed)
        )


def parse_containers(dobuildfile):
    obj = yaml.load(dobuildfile)
    containers = dict(obj['containers'])

    return {
        name: ContainerBuildConfig(
            name=name,
            context=containers[name]['context'], # Required
            dockerfile=containers[name].get('dockerfile', None),
            depends_on=containers[name].get('depends_on', None),
        ) for name in containers.keys()
    }


class Builder(object):
    def __init__(self, config, containers, extra_tags, push, pull, cache, cache_from_tag, keepDockerfiles=False):
        self.config = config
        self.containers = containers
        self.extra_tags = extra_tags
        self.push = push
        self.pull = pull
        self.cache = cache
        self.cache_from_tag = cache_from_tag
        self.keepDockerfiles = keepDockerfiles

    def ensure_container_built(self, container_name):
        container = self._get_container(container_name)
        if not container.built:
            self._build_container(container)

    def ensure_all_built(self):
        for container_name in self.containers.keys():
            self.ensure_container_built(container_name)

    def _get_container(self, container_name):
        if container_name in self.containers.keys():
            return self.containers[container_name]
        else:
            raise Exception('No such container {}.'.format(container_name))

    def _build_container(self, container):
        if container.depends_on is not None:
            for dep_name in container.depends_on:
                self.ensure_container_built(dep_name)

        cache_from_uri=container_uri(self.config, container.name, self.cache_from_tag) if self.cache_from_tag is not None else None
        if cache_from_uri is not None:
            try:
                sh.docker('pull', cache_from_uri, _fg=True, _tty_out=True)
            except sh.ErrorReturnCode as e:
                pass
        
        # Create the dockerfile
        with open(container.dockerfile, 'r') as dockerfile:
            with dotempl.TemplatedFilePath(dockerconf=self.config,
                                           filetotemplate=dockerfile,
                                           searchpath=os.path.dirname(container.dockerfile),
                                           filename=(os.path.basename(container.dockerfile) or 'Dockerfile'),
                                           keep=self.keepDockerfiles) as dockerfile_path:

                print("Building container {}:".format(container.name))

                docker_build(
                    uri=container_uri(self.config, container.name, self.config.tag),
                    dockerfile_path=dockerfile_path,
                    context=container.context,
                    pull=self.pull,
                    cache=self.cache,
                    cache_from_uri=cache_from_uri
                )

                for extra_tag in self.extra_tags:
                    docker_tag(
                        container_uri(self.config, container.name, self.config.tag),
                        container_uri(self.config, container.name, extra_tag),
                    )

                if self.push:
                    self._push_container(container)

                container.built = True

    def _push_container(self, container):
        if self.config.registry is None:
            raise Exception("Pushing containers requires a registry.")

        print("Pushing container {}:".format(container.name))
        docker_push(container_uri(self.config, container.name, self.config.tag))
        for extra_tag in self.extra_tags:
            docker_push(container_uri(self.config, container.name, extra_tag))
        container.pushed = True


@click.command()
@click.option('--dobuildfile',      default='dobuild.yaml', type=click.File('r'), envvar='DOBUILD_FILE')
@click.option('--registry',         default=None,           type=click.STRING,    envvar='DOSTACK_REGISTRY')
@click.option('--prefix',           default=None,           type=click.STRING,    envvar='DOSTACK_PREFIX')
@click.option('--tag',              default='latest',       type=click.STRING,    envvar='DOSTACK_TAG')
@click.option('--extra-tag',        multiple=True,          type=click.STRING,    envvar='DOBUILD_EXTRA_TAGS')
@click.option('--push/--no-push',   default=False,                                envvar='DOBUILD_PUSH')
@click.option('--pull/--no-pull',   default=False,                                envvar='DOBUILD_PULL')
@click.option('--cache/--no-cache', default=True,                                 envvar='DOBUILD_CACHE')
@click.option('--cache-from-tag',   default=None,           type=click.STRING,    envvar='DOBUILD_CACHE_FROM_TAG')
@click.option('--keep-dockerfiles/--no-keep-dockerfiles', default=False,          envvar='DOBUILD_KEEP_DOCKERFILES')
@click.argument('containers',       nargs=-1,                                     envvar='DOBUILD_CONTAINERS')
def dobuild(dobuildfile, registry, prefix, tag, extra_tag, push, pull, cache, cache_from_tag, keep_dockerfiles, containers):
    # Load config
    config = DockerConfig(registry, prefix, tag)

    # Load dobuild.yaml
    container_definitions = parse_containers(dobuildfile)

    # Build (& Push)
    builder = Builder(config, container_definitions, extra_tag, push, pull, cache, cache_from_tag, keep_dockerfiles)

    if len(containers) == 0:
        builder.ensure_all_built()
    else:
        for container in containers:
            builder.ensure_container_built(container)


def main():
    dobuild(auto_envvar_prefix='DOBUILD')

if __name__ == '__main__':
    main()
