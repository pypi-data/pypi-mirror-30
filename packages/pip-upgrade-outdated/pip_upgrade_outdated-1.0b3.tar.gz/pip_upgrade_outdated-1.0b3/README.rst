pip_upgrade_outdated
====================

Run ``pip install --upgrade`` for all outdated packages
(``pip list --outdated``).

Allow specifying which version of ``pip`` to run, and parallel or serial
execution of the upgrade step.

Command line usage
~~~~~~~~~~~~~~~~~~

::

    usage: pip_upgrade_outdated [-h] [-3 | -2 | --pip_cmd PIP_CMD] [--verbose]
                                [--dry_run] [--serial] [--version]

    Upgrade outdated python packages with pip.

    optional arguments:
      -h, --help         show this help message and exit
      -3                 use pip3
      -2                 use pip2
      --pip_cmd PIP_CMD  use PIP_CMD (default pip)
      --verbose, -v      may be specified multiple times
      --dry_run, -n      get list, but don't upgrade
      --serial, -s       upgrade in serial rather than parallel
      --version          show program's version number and exit

TODO
~~~~

-  does it work with environment variables?
-  need better error handling?
-  have it run with ``--format columns`` when using ``--dry_run`` and
   ``--verbose``?
-  Should the script explicitly return a value to the shell?

Sources
~~~~~~~

-  code based on
   https://gist.github.com/serafeimgr/b4ca5d0de63950cc5349d4802d22f3f0
-  project structure based on
   https://gehrcke.de/2014/02/distributing-a-python-command-line-application/

AUTHOR
~~~~~~

-  `Andrew H. Jaffe <mailto:a.h.jaffe@gmail.com>`__
-  `web <https://andrewjaffe.net>`__
-  twitter [@defjaf](https://twitter.com/defjaf)
-  github `defjaf <https://github.com/defjaf>`__
