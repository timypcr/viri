========
Security
========

Introduction
============


How do I create the keys?
=========================

Viri doesn't come with any helper for generating RSA required keys, but these
can be easily created using openssl.

First we have to generate the private key. Assuming we want a 2048 bits key
(choose any length you feel comfortable with) you can create the private key
with the following command:

    openssl genrsa -out private.key 2048

This will create a file named private.key in the current directory with a
random private key.

Next, you need to create the associated public key for this private key. To
generate it, just run the next command:

    openssl rsa -in private.key -pubout > public.key

