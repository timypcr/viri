===============
Getting started
===============

What is Viri?
=============

The aim of the Viri project is to provide an efficient way to run Python
in several hosts.

Viri consists of a daemon which needs to be installed in every host of the
infrastructure, and a command line utility to send and remotely execute Python
scripts in the target hosts.

What can be Viri useful for?
============================

Imagine you are the administrator of 10, 100, or even 1000 hosts. Imagine you
want to perform a single action to all or some of these hosts (like restart a
service, upgrade installed software, or check how much available free space
you have in the root partition). To do so, you can log in to every host, and
do what you want to do. Also, there are some tools like rsh which can execute
bash commands.

But what if you want to perform a more complex talk. Let's say you want to
check the available disk first. If it's less than 2 GB, you want to go to
/var/log directory, and see if there is a rotated log file older than three
months, and delete it.

With Viri you can perform this as easily as you can write a Python script
which does it. Then, Viri takes care of deploying and executing it in as
many hosts as you want, with a single command.

Also, Viri can be integrated with external applications to automate tasks in
your hosts. Imagine you have all hosts in your company in a database. Also
you have all the system administrators. Then, you assign which sysadmin can
access which host. With a simple integration of Viri and your corporate
application you can automatically synchronize host users with the ones in the
database. So, every time you add a new sysadmin to your application, and you
assign him to some hosts, the users on those hosts are automatically created.

And these are just a couple of examples. Viri is a powerful and flexible
platform, where you can automate whatever you are able to code in Python.

Installation
============

Viri consists of two different components. A daemon which should be installed
in every host you want to integrate in your Viri infrastructure, and a command
line utility which should be installed on sysadmin's workstation. Also, the
command line utility can be installed and used as a library if you want to
integrate your Viri infrastructure with an application.

