#!/usr/bin/env python
# dodeploy.py
from doutils import DockerConfig, container_uri
import os
import sys
import click
import jinja2
import tempfile
import shutil

@click.command()
@click.option('--registry',         default=None,            type=click.STRING,    envvar='DOSTACK_REGISTRY')
@click.option('--prefix',           default=None,            type=click.STRING,    envvar='DOSTACK_PREFIX')
@click.option('--tag',              default='latest',        type=click.STRING,    envvar='DOSTACK_TAG')
@click.option('--infile',           default=sys.stdin,       type=click.File('r'), envvar='DOTEMPL_INFILE')
@click.option('--outfile',          default=sys.stdout,      type=click.File('w'), envvar='DOTEMPL_OUTFILE')
@click.option('--searchpath',       default='.',             type=click.Path(exists=True, file_okay=False, dir_okay=True), envvar='DOTEMPL_SEARCHPATH')
def dotempl(registry, prefix, tag, infile, outfile, searchpath):
    # Docker config
    config = DockerConfig(registry, prefix, tag)
    
    outfile.write( template(config, infile.read(), searchpath=searchpath) )


class ContainerImageNames:
    def __init__(self, config):
        self.config = config

    def __getitem__(self, name):
        return container_uri(self.config, name, self.config.tag)

class EnvExceptionWrapper:
    def __getitem__(self, name):
        if name in os.environ:
            return os.environ[name]
        else:
            raise Exception("Environment variable {} not set.".format(name))

def template(config, body, searchpath='.'):
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(searchpath),
        autoescape=False
    )

    # Template context
    context = {
        'containers': ContainerImageNames(config),
        'env': EnvExceptionWrapper(),
    }
    
    return env.from_string(body).render(context)

class TemplatedFilePath(object):
    def __init__(self, dockerconf, filetotemplate, searchpath, keep=False, filename='docker-stack.yaml'):
        self.config = dockerconf
        self.searchpath = searchpath
        self.filetotemplate = filetotemplate
        self.keep = keep
        self.filename = filename

    def __enter__(self):
        self.tmpdir = tempfile.mkdtemp(prefix='dostack-')
        self.tmpstack = os.path.join(self.tmpdir, self.filename)
        with open(self.tmpstack, 'w') as f:
            f.write(
                template(self.config, self.filetotemplate.read(), searchpath=self.searchpath)
            )

        return self.tmpstack
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.keep:
            shutil.rmtree(self.tmpdir)
    
