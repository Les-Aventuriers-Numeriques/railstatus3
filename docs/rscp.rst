RSCP specifications
===================

Introduction
------------

RSCP (acronym of RailStatus Command Protocol) is a custom network protocol built on top of TCP, used by OpenComputers
devices inside a Minecraft world (known as "the clients") to communicate with a real-life RSCP server (known as "the server").

Communication between clients and the server is full-duplex (bi-directional), which means that:

  - Clients can send commands to the server, then gets a response
  - The server can send commands to the clients and getting responses as well, even if clients didn't requested them

Message format
--------------

Messages are UTF-8 encoded, formatted exactly like a CSV line with several columns:

  - Column (data) separator is comma (``,``)
  - Data may be enclosed by double-quotes (``"``)
  - Message (line) is terminated by a ``\n`` character

As RSCP can be used in a bi-directional manner, the server and the clients have to know what kind of message is incomming
in the socket: this can be either a command or a response. So the first "column" of the messages always have to indicate
this information: it can be either ``C`` for commands or ``R`` for responses. The content of the next columns differs
according to this information, which is detailed below.

Command
```````

A command is textual order which always have to be replied. It contain the command name and may also contain several parameters.

.. code-block:: text

    C,<name>,"<parameter1>","<parameter2>","<parameterN>"\n

Examples:

.. code-block:: text

    C,RSCP_SET_VERSION,1\n
    C,TANK_UPDATE_FILL,f156jt4hb5dhv2e9df56dhf1r1eh54re,56000\n

See :ref:`available-commands` for a complete list.

Response
````````

Response is sent back after a command was handled. It contain the response code (which indicates if the command execution was
successful or not). It may also contain additional data.

.. code-block:: text

    R,<response code>,"<data1>","<data2>","<dataN>"\n

Examples:

.. code-block:: text

    R,NOT_A_RSCP_CLIENT\n
    R,OK,21100\n

``<response code>`` can be one of:

  - ``OK`` - The command was executed successfuly
  - ``BAD_FORMAT`` - The previously sent command wasn't well-formed
  - ``UNKNOWN_COMMAND`` - Unknown command ``<name>``
  - ``INVALID_PARAMETERS`` - The number of parameters doesn't match the ones required by the command
  - ``NOT_A_RSCP_CLIENT`` - Handshake failure (see :ref:`command-rscp-set-version`)
  - ``ACK`` - Handshake success (see :ref:`command-rscp-set-version`)

.. _available-commands:

Available commands
------------------

The following is a list of all available RSCP commands. For each commands you'll find, in parenthesis, which side (the client
or the server) can use them.

.. _command-rscp-set-version:

RSCP_SET_VERSION (client)
`````````````````````````

.. code-block:: text

    C,RSCP_SET_VERSION,<version number>\n

Handshake command. Must be sent prior any other commands. This allow the RSCP server to reject any incoming TCP connection
that aren't a RSCP client.

Parameters:

  - ``<version number>`` - The RSCP version used (``1`` at this moment of writing)

Return:

.. code-block:: text

    R,ACK\n

Handshake success. You are now ready to send and receive commands.

.. code-block:: text

    R,NOT_A_RSCP_CLIENT\n

Invalid handshake workflow. The connexion will immediately be closed after this response is sent.
