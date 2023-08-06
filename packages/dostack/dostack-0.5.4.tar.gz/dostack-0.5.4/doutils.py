# dockerutils.py
from __future__ import print_function
import sys
import sh

def try_docker(*args, **kwargs):
    try:
        sh.docker(*args, **kwargs)
    except sh.ErrorReturnCode as e:
        print("FAILED: \n{}".format(str(e.full_cmd)), file=sys.stderr)
        exit(1)


class DockerConfig(object):
    def __init__(self, registry, prefix, tag):
        self.registry = registry
        self.prefix = prefix
        self.tag = tag


def container_uri(config, container_name, tag='latest'):
    url = "{}:{}".format(container_name, tag)

    if config.prefix is not None:
        url = config.prefix + "/" + url
    else:
        url = "local/" + url

    if config.registry is not None:
        url = config.registry + "/" + url

    return url
