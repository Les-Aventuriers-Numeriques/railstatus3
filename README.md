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
  - Railways, switches, etc

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

First, once started, `server.py` will spawn a multi-threaded RSCP server. The RSCP protocol used between clients
and the server is detailed in the section below.

### The HTTP server

`server.py` will also run an HTTP server listening on the same interface as the one specified by the `ip` argument. The
port used will be the one defined by the `port` argument, plus `5`.

## RSCP specifications

### Introduction

RSCP (acronym of **RailStatus Command Protocol**) is a custom network protocol built on top of TCP, used by OpenComputers
devices inside a Minecraft world (known as "the clients") to communicate with a real-life RSCP server (known as "the server").

Communication between clients and the server is full-duplex (bidirectional), which means that:

  - Clients can send commands to the server
  - The server can send commands to the clients as well, even if these latter didn't requested them

### Acknowledgements

  - All commands and responses separator is `\n`
  - Encoding is UTF-8
 
### Command format

A command consists of strings separated by spaces:

    <object> <action> <parameter1> <parameter2> [...] <parameterN>\n

Example:

    POSITION UPDATE -455,252\n

### Possible errors

Errors that can be returned are:

  - `BAD_FORMAT\n` - The sent command line isn't well-formed
  - `UNKNOWN_OBJECT\n` - Unknown `<object>`
  - `UNKNOWN_ACTION\n` - `<action>` isn't valid for this `<object>`
  - `INVALID_PARAMETERS_NUMBER\n` - The number of parameters doesn't match the ones required by the sent command

### Handshake

Every clients, once successfully connected to the server, must firstly send the following command to perform the handshake:

    RSCP VERSION <version number>\n

Where `<version number>` is the RSCP version used (`1` at this moment of writing).

The server will then acknowledge with the `ACK\n` response. You are now ready to send and receive commands.

Failing to follow this workflow will result by a `NOT_A_RSCP_CLIENT\n` response from the server followed by an immediate connexion
closing.