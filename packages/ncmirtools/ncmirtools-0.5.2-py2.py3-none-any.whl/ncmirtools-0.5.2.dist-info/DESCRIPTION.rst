===============================
ncmirtools
===============================

.. image:: https://img.shields.io/pypi/v/ncmirtools.svg
     :target: https://pypi.python.org/pypi/ncmirtools
     :alt: Pypi 
.. image:: https://pyup.io/repos/github/crbs/ncmirtools/shield.svg
     :target: https://pyup.io/repos/github/crbs/ncmirtools/
     :alt: Updates

.. image:: https://travis-ci.org/CRBS/ncmirtools.svg?branch=master
       :target: https://travis-ci.org/CRBS/ncmirtools

.. image:: https://coveralls.io/repos/github/CRBS/ncmirtools/badge.svg?branch=master
       :target: https://coveralls.io/github/CRBS/ncmirtools?branch=master

.. image:: https://www.quantifiedcode.com/api/v1/project/1de1625cc49e4488b0fbd719cbfa0901/badge.svg
       :target: https://www.quantifiedcode.com/app/project/1de1625cc49e4488b0fbd719cbfa0901
       :alt: Code issues

Set of commandline tools for interaction with data hosted internally at NCMIR_.

For more information please visit our wiki page: 

https://github.com/CRBS/ncmirtools/wiki


Tools
-----

* **mpidir.py** -- Given a Microscopy product id, this script finds the path on the filesystem

* **projectdir.py** -- Given a project id, this script finds the path on the filesystem

* **projectsearch.py** -- Allows caller to search database for projects

* **mpidinfo.py** -- Queries database and returns information on specific Microscopy Product

* **imagetokiosk.py** -- Transfers second youngest image file to remote server via scp

* **ncmirtool.py** -- New tool that will soon be the main entry point for all commands above. Currently offers prototype uploading of data to Cell Image Library (CIL)

Dependencies
------------

* `argparse <https://pypi.python.org/pypi/argparse>`_

* `configparser <https://pypi.python.org/pypi/configparser>`_

* `pg8000 <https://pypi.python.org/pypi/pg8000>`_

* `ftpretty <https://pypi.python.org/pypi/ftpretty>`_

* `paramiko <https://pypi.python.org/pypi/paramiko>`_

Compatibility
-------------

* Should work on Python 2.7, 3.3, 3.4, & 3.5 on Linux distributions


Installation
------------

Try one of these:

::

  pip install ncmirtools

  python setup.py install


License
-------

See LICENSE.txt_


Bugs
-----

Please report them `here <https://github.com/CRBS/ncmirtools/issues>`_


Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _NCMIR: https://ncmir.ucsd.edu/
.. _LICENSE.txt: https://github.com/CRBS/ncmirtools/blob/master/LICENSE.txt
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage



=======
History
=======

0.5.2 (2018-04-02)
------------------

* Another fix for Issue #18 where the path output to standard
  out had incorrect path delimiter output.

0.5.1 (2018-04-02)
------------------

* Set delimiter for uploads to / to deal with problem uploading
  files from windows machine. 
  `Issue #18 <https://github.com/CRBS/ncmirtools/issues/18>`_

0.5.0 (2018-03-28)
------------------

* Created prototype cilupload tool. 
  Accessible via ncmirtool.py cilupload 
  `Issue #17 <https://github.com/CRBS/ncmirtools/issues/17>`_

* Created ncmirtool.py to prototype a single command line 
  script entry point. 
  `Issue #13 <https://github.com/CRBS/ncmirtools/issues/13>`_

* Dropped support for Python 2.6

0.4.0 (2017-06-28)
------------------

* Added imagetokiosk.py which transfers second youngest image
  file to remote server via scp.
  `Issue #16 <https://github.com/CRBS/ncmirtools/issues/16>`_

* Fixed a couple minor issues so this tool will work on 
  Windows. 
  `Issue #14 <https://github.com/CRBS/ncmirtools/issues/14>`_

0.3.0 (2017-01-13)
------------------

* Added mpidinfo.py script to provide information about 
  Microscopy Product from database. `Issue #6 <https://github.com/CRBS/ncmirtools/issues/6>`_

* Fixed bug in mpidinfo.py where passing id greater then 2^31 -1
  resulted in uncaught ProgrammingException `Issue #9 <https://github.com/CRBS/ncmirtools/issues/9>`_

* Consolidated all _setup_logging() calls into one function in config.py.
  `Issue #8 <https://github.com/CRBS/ncmirtools/issues/8>`_

* Modified NcmirToolsConfig to look for configuration file in /etc/ncmirtools.conf
  as well as the users home directory `Issue #7 <https://github.com/CRBS/ncmirtools/issues/7>`_


0.2.0 (2016-11-8)
------------------

* Added projectdir.py script which finds directories for a given
  project id. Issue #3

* Added projectsearch.py script which given a string will search
  a postgres database for projects with that string in the name
  or description. 


0.1.1 (2016-10-14)
------------------

* Minor improvements to README.rst for better presentation on pypi

0.1.0 (2016-10-04)
------------------

* Initial release with single script mpidir.py


