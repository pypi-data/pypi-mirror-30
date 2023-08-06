DoBuild
=======

Docker Container Builder
------------------------

`dobuild` builds your project's containers specified by a compose-like yaml file.
`dotempl` templates files (eg. Dockerfiles, docker-stack.yaml's) based on the environment.


Installing
----------

    git clone <this repo>
    pipsi install ./dostack


Features
--------

- Build multiple containers with one command
- Control order of builds with inter-container dependencies
- Templating Dockerfiles, e.g.  so that one container can FROM another without having to edit Dockerfile each build


Getting Started
---------------

Create a `dobuild.yaml` file in your project root, with a structure like this:

	containers:
	  pinger:
	    context: ./docker/pinger
	    dockerfile: ./docker/pinger/Dockerfile.t

	  hello:
	    context: .
	    dockerfile: ./docker/hello/Dockerfile.t

	  hello2:
	    context: ./docker/hello2
	    dockerfile: ./docker/hello2/Dockerfile.t
	    depends_on:
	      - hello

This example defines three containers to be built, *pinger*, *hello* and *hello2*. Here we have declared that *hello2* depends on *hello*, so *hello* will always be built before *hello2*.

Now to build your containers, run

    dobuild

And watch it happen! `dobuild` runs `docker build` under the hood for you, so the output will be familiar.

If for example, you only want to a build specific container (and it's dependencies), you can use:

    dobuild hello2

which will build *hello2* (and *hello* as it's a dependency), but not *pinger*.

Templates
---------

`dobuild` templates your Dockerfiles using [moustache](https://mustache.github.io/mustache.5.html) templates. 

For example, the Dockerfile for *hello2* above:

    FROM {{ containers.hello }} 
    RUN echo "Building {{ containers.hello2 }}"
    ENTRYPOINT echo Hello, World, 2!

You can use `{{ containers.<name> }}` to refer to the uri of any container in the project in the current build. Other available tags:

- `{{ docker.registry }}` The docker registry added to container URIs, if defined.
- `{{ docker.prefix }}` The prefix added to container URIs, if defined.

Container URIs (Tags)
---------------------

After building your containers, `dobuild` will tag them with meaningful names composed of a registry, prefix and the container name.

For example, running:

    dobuild hello \
    --registry registry.example.com \
    --prefix owner/helloworld

Will build and tag the image with URI `registry.example.com/owner/helloworld/hello`.

Pushing to a Registry
---------------------

If you add the `--push` flag, and all containers built successfully, `dobuild` will push the containers to the specified registry.

Environment Variables
---------------------

Options can also be specified in environment variables. Note that options on the command line override the environment.

    DOBUILD_FILE=./dobuild.yaml           # Path to dobuild.yaml
    DOBUILD_REGISTRY=registry.example.com # Docker registry
    DOBUILD_PREFIX=owner/helloworld       # Container URI prefix
    DOBUILD_PUSH=True                     # Push containers after building
    
