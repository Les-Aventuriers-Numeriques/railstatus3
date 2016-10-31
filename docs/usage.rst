Usage
=====

A single command line will run RailStatus. ``cd`` to its root directory and run:

::

    $ python server.py

Available command line options are:

--ip       The network interface to attach with (use ``--ip="0.0.0.0"`` to listen to all interfaces), default to ``127.0.0.1``
--port     The port to listen to (use ``--port=0`` to choose a random unused port), default to ``8888``
--clients  The maximum simultaneous clients allowed to connect to the server, default to ``10``

When succeffully started, you'll see something like this:

::

    31/10/2016 10:06:57 - INFO - Running RSCP server
    31/10/2016 10:06:57 - INFO - Bind successful
    31/10/2016 10:06:57 - INFO - Listening to 127.0.0.1:8888 with a clients limit of 10

To kill the server, simply use ``CTRL+C``.