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

```
python server.py --ip=127.0.0.1 --port=8888 --clients=10
```

  - `ip` The network interface to attach with (use `--ip=""` to listen to all interfaces)
  - `port` The port to listen to. Use `--port=0` to choose a random free port
  - `clients` The maximum simultaneous clients allowed to connect to the server

## How it works

Once started, `server.py` will first spawn a thread containing the server itself, with the clients connection handling
logic. It will then listen to the specified interface/port for incoming connections. It will spawn one thread for
each clients connecting, thus allowing the server to be multi-threaded and non-blocking for all clients. The protocol
used between the clients and the server, named RSCP, is detailed in the section below.

### RSCP documentation

RSCP (acronym of **RailStatus Command Protocol**) is a custom network protocol used by OpenComputers devices inside a
Minecraft world (known as "the clients") to communicate with a real-life RSCP server (known as "the server").

#### Acknowledgements

  - RSCP is built on top of TCP
  - RSCP isn't encrypted
  - Escape character is `\n`
  - Communication between the clients and the server is full-duplex (which means that the server may send data to the clients without the client makes the request)