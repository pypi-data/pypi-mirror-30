
============
python-chirp
============

Message-passing for everyone

BETA-RELEASE: 1.1.2
===================

https://github.com/concretecloud/python-chirp

Features
========

* Fully automatic connection setup

* TLS support

  * Connections to 127.0.0.1 and ::1 aren't encrypted

* Easy message routing

* Robust

  * No message can be lost without an error (in sync mode)

* Very thin API

* Minimal code-base, all additional features will be implemented as modules in
  an upper layer

* Fast

Install
=======

Dependencies
------------

.. code-block:: bash

   Alpine:       apk add python3-dev libffi-dev libressl-dev libuv-dev
   Debian-based: apt install python3-dev libffi-dev libssl-dev libuv1-dev
   Redhat-based: yum install python3-devel libffi-devel openssl-devel
                 libuv-devel
   Arch:         pacman -S libffi openssl libuv
   OSX:          brew install libffi openssl libuv

pip
---

If we have wheels for your platform, you don't need to install any
dependencies.

.. code-block:: bash

   pip install libchirp

setup.py
--------

.. code-block:: bash

   pip install cffi
   python setup.py install


