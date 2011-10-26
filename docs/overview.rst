========
Overview
========

.. contents::
   :local:
   :class: toctree-wrapper

What is Viri?
=============

Viri is an application to automate tasks, making easy to execute commands
in several hosts like if they were executed in a single one.

Any tasks can be automated, but Viri focuses on system administration tasks.

What you will be able to do with Viri?
======================================

Basic examples
--------------

To start understanding Viri, let us start with some examples.

.. code-block:: none

   viric exec which sendmail --hosts=209.85.169.121
   /usr/sbin/sendmail

This example shows how to use Viri to check the path of the *sendmail* binary,
if installed in the specified host.

In this case, we could also write:

.. code-block:: none

   viric exec which sendmail --hosts=209.85.169.122 || echo "Not installed"
   Not installed

and see the text *Not installed* if *sendmail* is not installed. This is
possible because the *which* command returns a non-zero value when a program
is not found, and Viri captures this value, and makes it available in the
local host, as the return code of the viric command itself. Obviously, this is
only possible when executing commands in a single host.


Working with multiple hosts
---------------------------

Now, let us see how to deal with more than one host.

.. code-block:: none

   viric exec hostname --hosts=209.85.169.106,72.30.2.43,65.55.175.254
   209.85.169.106 (SUCCESS) >>>
   google.com
   72.30.2.43 (SUCCESS) >>>
   yahoo.com
   65.55.175.254 (SUCCESS) >>>
   bing.com

In this example, we execute the command *hostname* on three hosts, and we get
the host name of each as the output of of the viric command. Note that Viri
adds the IP address before the result, as well as the keyword SUCCESS, to show
that the command could be executed successfully in the remote host.

This is fine, but what if you want to execute a command using Viri in hundreds
of remote hosts? Instead of specifying the IP addresses in the command line,
you will probably prefer to set some host groups.

To set a host group, just create a file on ``~/.viri/hostgroups/``, with the
IP addresses. Then you can use the name of the file instead of the list of
addresses.

For example, let us create the file ``~/.viri/hostgroups/production`` with
next content:

.. code-block:: none

   209.85.169.121
   209.85.169.122
   209.85.169.123
   209.85.169.128
   172.16.254.1

Then, you can just execute:

.. code-block:: none

   viric exec runlevel --hosts=production
   209.85.169.121 (SUCCESS) >>>
   N 3
   209.85.169.122 (SUCCESS) >>>
   N 3
   209.85.169.123 (SUCCESS) >>>
   N 3
   209.85.169.128 (SUCCESS) >>>
   N 3
   172.16.254.1 (SUCCESS) >>>
   N 3

and see how the command is executed in all hosts defined previously.


Viri in Windows
---------------

Previous examples are based on UNIX systems. But Viri works on Windows systems too.

See this example:

.. code-block:: none

   viric exec ver --hosts=209.85.169.128
   Microsoft Windows [Versoin 5.2.3790]

