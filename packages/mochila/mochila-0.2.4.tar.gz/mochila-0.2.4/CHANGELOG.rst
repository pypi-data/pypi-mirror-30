Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

[Unreleased]
------------

Added
~~~~~

Changed
~~~~~~~
- Fixes

[0.2.4] - 2017-11-04
--------------------

Changed
~~~~~~~
- Fixes MCH-10

[0.2.3] - 2017-11-04
--------------------
Changed
~~~~~~~
- Fixes MCH-9

[0.2.2] - 2017-10-31
--------------------

Changed
~~~~~~~
- Fixes some issues with excluding/including operations

[0.2.1] - 2017-10-26
--------------------

Changed
~~~~~~~
- Changed __init__ methods so they invoke the correct add/insert methods the init will also be checked by any
   constraints added by subclasses.
- Fixed the implementation of the __iadd__ of the Bag

[0.2.0] - 2017-09-|6
--------------------

Added
~~~~~
- Additional examples to the documentation

Changed
~~~~~~~
- Fixed some of the method implementation to reduce the number of methods that modify the underlying collections.
- Changed the the name of the changelog file and defined it's format and contents


[0.1.0] - 2017-08-27
--------------------
Initial release. Includes the first API implementation, tests and documentation.

.. Added
   ~~~~~
   Changed
   ~~~~~~~
   Fixed
   ~~~~~
   Removed
   ~~~~~~~
