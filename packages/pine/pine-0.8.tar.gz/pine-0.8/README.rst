.. image:: https://readthedocs.org/projects/pine/badge/?version=latest
   :target: http://pine.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://travis-ci.org/briancurtin/pine.svg?branch=master
   :target: https://travis-ci.org/briancurtin/pine
   :alt: Test Status

pine
====

A benchmark utility to make requests to a REST API.

Pine makes requests to URLs a bunch of times and computes some statistics
about how those requests were responded to. This is ideally useful to run
on every change to your codebase so you can identify changes early.

Pine isn't a load testing tool. If you're trying to solve C10K, this won't
help you. Pine (currently) runs requests serially.

Documentation
=============

Documentation is available at http://pine.readthedocs.io/en/latest/

Installation
============

On Python 3.6, ``pip install pine`` will do it.

On Python 3.7, there is an additional step required before running the
same command. Until PyYAML supports Python 3.7 in a released version,
you will need to install PyYAML from GitHub::

    pip install git+https://github.com/yaml/pyyaml.git
    pip install pine

https://github.com/briancurtin/pine/issues/1 and
https://github.com/yaml/pyyaml/issues/126 are tracking this issue.

Usage
=====

``pine -c myconfig.yaml`` is the simplest way to begin. This will run your
configuration and output the results to stdout. If you'd like to write
the output to a file, ``-o myoutputfile.json`` will do it. If you'd like
to specify a particular run ID, other than the default of the current
timestamp, ``-i 32a63ab`` will do it. That's useful for tracking the
commit hash of what you're testing.

Run ``pine -h`` for complete details.

Configuration
=============

Pine uses YAML for configuration. See
`conf/example.yaml <https://github.com/briancurtin/pine/blob/master/conf/example.yaml>`_
for an example.

Output
======

Pine writes its results in JSON, either to stdout or the path you specified
in ``-o``. It looks like the following::

    {"results": [
        {"times": [1.580882219500005, 1.8884545513215, 1.52546876846],
         "timeouts": 0, "failures": [], "name": "get_all_things",
         "description": "Get all of the things",
         "mean": 1.668359371049998,
         "median": 1.580882219500005,
         "stdev": 0.0969358463985873},
        {"times": [0.4894684654656654, 0.508042131499991, 1.054654684684],
         "timeouts": 0, "failures": [], "name": "get_one_thing",
         "description": "Get one thing",
         "mean": 0.856881387399993,
         "median": 0.508042131499991,
         "stdev": 0.0646515285845596},
     ],
     "name": "Testing the things",
     "version": "1.0",
     "id": "7155eb"}

Thanks
======

Thanks to Francis Horsman for the ``pine`` package name.
