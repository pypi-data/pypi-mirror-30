========
Overview
========



A tool to wait for services and execute command. Useful for Docker containers that depend on slow to start services
(like almost everything).

* Free software: BSD license

Installation
============

::

    pip install holdup

Documentation
=============

Usage: ``holdup [-h] [-t SECONDS] [-T SECONDS] [-i SECONDS] [-n] service [service ...] [-- command [arg [arg ...]]]``

Wait for services to be ready and optionally exec command.

Positional arguments:
  ``service``
    A service to wait for. Supported protocols:
    "tcp://host:port/", "path:///path/to/something",
    "unix:///path/to/domain.sock", "eval://expr",
    "http://urn", "http://urn" (status 200 expected). Join
    protocols with a comma to make holdup exit at the
    first passing one, eg: tcp://host:1,host:2 or
    tcp://host:1,tcp://host:2 are equivalent and mean "any
    that pass".

  ``command``
    An optional command to exec.

Optional arguments:
  -h, --help            show this help message and exit
  -t SECONDS, --timeout SECONDS
                        Time to wait for services to be ready. Default: 5.0
  -T SECONDS, --check-timeout SECONDS
                        Time to wait for a single check. Default: 1.0
  -i SECONDS, --interval SECONDS
                        How often to check. Default: 0.2
  -n, --no-abort        Ignore failed services. This makes `holdup` return 0
                        exit code regardless of services actually responding.

Suggested use
-------------

Assuming you always want the container to wait add this in your ``Dockerfile``::

    COPY entrypoint.sh /
    ENTRYPOINT ["/entrypoint.sh"]
    CMD ["/bin/bash"] 

Then in ``entrypoint.sh`` you could have::

    #!/bin/sh
    set -eux
    urlstrip() { string=${@##*://}; echo ${string%%[\?/]*}; }
    exec holdup \
         "tcp://$DJANGO_DATABASE_HOST:$DJANGO_DATABASE_PORT" \
         "tcp://$(urlstrip $CELERY_RESULT_BACKEND)" \
         -- "$@"

The only disadvantage is that you might occasionally need to use ``docker run --entrypoint=''`` to avoid running holdup. No biggie.

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox


Changelog
=========


1.6.0 (2018-03-22)
------------------

* Added verbose mode (`-v` or ``--verbose``).
* Changed default timeout to 60s (from 5s).

1.5.0 (2017-06-07)
------------------

* Added an ``eval://expression`` protocol for weird user-defined checks.

1.4.0 (2017-03-27)
------------------

* Added support for HTTP(S) check.

1.3.0 (2017-02-21)
------------------

* Add support for "any" service check (service syntax with comma).

1.2.1 (2016-06-17)
------------------

* Handle situation where internal operations would take more than planned.

1.2.0 (2016-05-25)
------------------

* Added a file check.

1.1.0 (2016-05-06)
------------------

* Removed debug print.
* Added ``--interval`` option for how often to check. No more spinloops.

1.0.0 (2016-04-22)
------------------

* Improved tests.
* Always log to stderr.

0.1.0 (2016-04-21)
------------------

* First release on PyPI.


