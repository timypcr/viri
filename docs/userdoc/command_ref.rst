=======================
Viri commands reference
=======================

.. contents::
   :local:
   :class: toctree-wrapper

version
-------

Returns the version of the Viri daemon running on the remote host.

Usage
~~~~~

.. code-block:: none

   viric version

exec
----

Executes a command or a program in the remote host.

Usage
~~~~~

.. code-block:: none

   viric exec program [argument_list] [-s]

Arguments
~~~~~~~~~

**program**

The name of the program, the command or the script to execute. The name can be
just the name of the file if it is located on the system path, but it should
be the full path if it is not.

**argument_list**

List of arguments the program will get, when executed in the remote host. The
list must be quoted if it has more than one element, or if it starts with a
dash (otherwise, Viri would get it as a local option).

**--send (-s)**

By default, Viri assumes that the program (or command) to execute exists in
the remote host. To execute a binary or a script that only exists locally, the
option *--send* can be specified, and Viri will send the file before executing
it.

Examples
~~~~~~~~

.. code-block:: none

   viric exec tail "-n20 /var/log/syslog"

   viric exec myscript.py -s

get
---

Downloads a file from the remote host.

Usage
~~~~~

.. code-block:: none

   viric get remote_file

Arguments
~~~~~~~~~

**remote_file**

Path to the file it will be downloaded from the remote host.

put
---

Uploads a file to the remote host.

Usage
~~~~~

.. code-block:: none

   viric put local_file remote_path [-f]

Arguments
~~~~~~~~~

**local_file**

Local path of the file to be sent.

**remote_path**

Destination path where the file will be copied.

**--force (-f)**

Force overwriting if the file already exists in the remote host.

