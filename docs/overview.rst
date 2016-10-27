Overview
========

RailStatus consists of two components.

The RSCP server
---------------

First, once started, ``server.py`` will spawn a multi-threaded :doc:`RSCP <rscp>` (RailStatus Command Protocol) server. This allow both
clients and the server to communicate to each other.

The server can then gather data from (and store it in a database) and send commands to the clients.

The HTTP server
---------------

``server.py`` will also run an HTTP server listening on the same interface as the one specified by the ``ip`` argument. The
port used will be the one defined by the ``port`` argument, plus ``5``.

Its goal is to provide a web-based control interface to display data and send commands. It communicate with the RSCP server
above.

.. _RSCP: _rscp-spec