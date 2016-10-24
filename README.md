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

```
python server.py --ip=127.0.0.1 --port=8888 --clients=10
```

  - `ip` The network interface to attach with (use `--ip="0.0.0.0"` to listen to all interfaces)
  - `port` The port to listen to (use `--port=0` to choose a random unused port)
  - `clients` The maximum simultaneous clients allowed to connect to the server

## How it works

RailStatus consists of two components.

### The RSCP server

First, once started, `server.py` will spawn a thread containing the RSCP server itself, with the clients connection handling
logic. It will then listen to the specified interface/port for incoming connections. For each clients connecting, it
will spawn one thread, thus allowing the server to be multi-threaded and non-blocking.

The RSCP protocol used between clients and the server is detailed in the section below.

### The HTTP server

`server.py` will also run an HTTP server listening on the same interface as the one specified by the `ip` argument. The
port used will be the one defined by the `port` argument, plus `5`.

## RSCP specifications

### Introduction

RSCP (acronym of **RailStatus Command Protocol**) is a custom network protocol built on top of TCP, used by OpenComputers
devices inside a Minecraft world (known as "the clients") to communicate with a real-life RSCP server (known as "the server").

Communication between clients and the server is full-duplex, which means that:

  - Clients can send commands to the server to perform specific actions like setting/retrieving values, start a specific task, etc
  - The server can send commands to the clients even if these latter didn't requested them (kind of server push)

### Acknowledgements

  - Command separator is `\n`
 
### Command format

```
<object> <action> <parameter1> <parameter2> [...] <parameterN>\n
```
  
### Typical workflow

The client, once successfully connected through a TCP socket to the server's one, must send the following command