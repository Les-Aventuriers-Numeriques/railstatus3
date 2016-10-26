# RailStatus 3

       ___              _       _      ___     _               _                    
      | _ \   __ _     (_)     | |    / __|   | |_    __ _    | |_    _  _     ___  
      |   /  / _` |    | |     | |    \__ \   |  _|  / _` |   |  _|  | +| |   (_-<  
      |_|_\  \__,_|   _|_|_   _|_|_   |___/   _\__|  \__,_|   _\__|   \_,_|   /__/_  
    _|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|
    "`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'

## Prerequisites

  - Python 3
  - A modded Minecraft server with Railcraft and OpenComputers

## Installation

Clone this repo, and then the usual `pip install -r requirements.txt`.

## Configuration

None ATM.

## Usage

    python server.py --ip=127.0.0.1 --port=8888 --clients=10

  - `ip` The network interface to attach with (use `--ip="0.0.0.0"` to listen to all interfaces)
  - `port` The port to listen to (use `--port=0` to choose a random unused port)
  - `clients` The maximum simultaneous clients allowed to connect to the server

## How it works

RailStatus consists of two components.

### The RSCP server

First, once started, `server.py` will spawn a multi-threaded RSCP (RailStatus Command Protocol) server. This allow both
clients and the server to communicate to each other. The server can then gather data from (and store it in a database)
and send commands to the clients.

The RSCP protocol used between clients and the server is detailed in the section below.

### The HTTP server

`server.py` will also run an HTTP server listening on the same interface as the one specified by the `ip` argument. The
port used will be the one defined by the `port` argument, plus `5`.

Its goal is to provide a web-based control interface to display data and send commands. It communicate with the RSCP server
above.

## RSCP specifications

### Introduction

RSCP (acronym of RailStatus Command Protocol) is a custom network protocol built on top of TCP, used by OpenComputers
devices inside a Minecraft world (known as "the clients") to communicate with a real-life RSCP server (known as "the server").

Communication between clients and the server is full-duplex (bi-directional), which means that:

  - Clients can send commands to the server, then gets a response
  - The server can send commands to the clients and getting responses as well, even if clients didn't requested them

### Acknowledgements

  - Messages separator is `\n`
  - Encoding is UTF-8
  - A client can connect to only one server at a time

### Messages format

Messages are formatted exactly like a CSV line: the data is separated by commas (`,`), enclosed by double-quotes (`"`),
and terminated by a `\n` character.

As RSCP can be used in a bi-directional manner, the server and the clients have to know what kind of message is incomming
in the socket: this can be either a command or a response. So the first "column" of the messages always have to indicate
this information: it can be either `C` for commands or `R` for responses. Details below.

#### Commands

    C,<name>,"<parameter1>","<parameter2>","<parameterN>"\n

Examples:

    TODO

#### Responses

    R,<response code>,"<data1>","<data2>","<dataN>"\n

Examples:

    TODO

`<response code>` can be:

  - `OK` - If all is good
  - `BAD_FORMAT` - The previously sent command wasn't well-formatted
  - `UNKNOWN_COMMAND` - Unknown command `<name>`
  - `INVALID_PARAMETERS_NUMBER` - The number of parameters doesn't match the ones required by the command

### Handshake

Every clients, once successfully connected to the server, must firstly send the following command to perform the handshake:

    C,RSCP_SET_VERSION,<version number>\n

Where `<version number>` is the RSCP version used (`1` at this moment of writing).

The server will then acknowledge with the `ACK\n` response. You are now ready to send and receive commands.

Failing to follow this workflow will result by a `NOT_A_RSCP_CLIENT\n` response from the server followed by an immediate connexion
closing.