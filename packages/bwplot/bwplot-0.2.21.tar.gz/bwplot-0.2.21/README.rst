[![Build Status](https://travis-ci.org/eng-tools/bwplot.svg?branch=master)](https://travis-ci.org/eng-tools/bwplot)
[![PyPi version](https://img.shields.io/pypi/v/bwplot.svg)](https://img.shields.io/pypi/v/bwplot.svg)

******
bwplot
******

This python project contains a simple command to select colours that are distinctly different in both colour and black and white.

How do I get set up?
====================

1. Run ``pip install -r requirements.txt``

Testing
=======

Tests are run with pytest

* Locally run: ``pytest`` on the command line.

* Tests are run on every push using travis, see the ``.travis.yml`` file


Deployment
==========

To deploy the package to pypi.com you need to:

 1. Push to the *pypi* branch. This executes the tests on circleci.com [not setup anymore]

 2. Create a git tag and push to github, run: ``trigger_deploy.py`` or manually:

 .. code:: bash
    git tag 0.5.2 -m "version 0.5.2"
    git push --tags origin pypi
