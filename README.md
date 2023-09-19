# mc-manager-api

A very simple API for managing Minecraft servers that run via docker compose stacks.

## Overview

This API only exposes a few commands:

- /list
- /start
- /stop
- /extendtime

For a description of each command, see [Commands](#Commands)

The API simply runs local commands to interact with docker compose stacks on the same host. It is very primitive. **It doesn't even require authentication** so one must be very careful about network access when running it.

I run this in a docker container (see Dockerfile in this repo) in the same docker network as my [discord-mc-bot]() which is the only client of the API, this means it is not exposed to any network outside of the virtual one on the instance it runs on.

## Commands

```
command: /list
method: GET
```

This command will return a list of Minecraft servers (docker-compose stacks) that are available to manage. Under the hood it just lists out the subdirectories in the provided `SERVERS_DIR`. These subdirectories contain the `docker-compose.yml` files and data for the Minecraft servers.

```
command: /start
method: POST
arguments:
  - server: server to start
```

This command will start the given Minecraft server. Under the hood it will just run `docker-compose up -d` for that stack.

```
command: /stop
method: POST
arguments:
  - server: server to stop
```

This command will stop the given Minecraft server. Under the hood it will just run `docker-compose down` for that stack.

```
command: /extendtime
method: POST
arguments:
  - server: target server
  - days: number of days to extend
```

This command will extend the time that the server stays running. By default, the servers will shut off if no player is online for 30 minutes. This command will keep the server up even with no players online for the given number of days.

Under the hood it will place a `.skip-stop`(referred to as a skipfile) file in the Minecraft server's data directory, and create a corresponding timefile for when that skipfile should be removed. A separate process [mc-skipfile-manager]() handles checking the timefiles and removing skipfiles.

For more info, view the itzg/docker-minecraft-server auto-stop documentation, as well as my [mc-skipfile-manager]() app mentioned.

## TODO

- Automatically build API docs using a library.
- Docker image CI/CD
- Example `docker-compose.yml` file

## Personal reference

I'm using these commands to manually build my image at the moment:

```
docker build -t git.imkumpy.in/kumpy/mc-manager-api:latest .
docker push git.imkumpy.in/kumpy/mc-manager-api:latest
```

