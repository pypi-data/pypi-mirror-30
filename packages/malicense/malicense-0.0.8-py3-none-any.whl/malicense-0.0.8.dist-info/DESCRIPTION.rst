License integrity checker
==============================

This is a package for verifying that a license file in an open source project has not changed since distribution. Most licenses require inclusion of that license. This checks that it is the case.

Installation
------------
``$ pip install malicense``

Setup
-----
Your project must have a "LICENSE" file in the top directory of the package (not the project). You must take a snapshot of the license with::

    $ malicense LICENSE.txt --snap

Then, git commit to save the snapshot placed in the new file ``.licsnap``.

Usage
-----
1: UNIX command line executable exits with code 2 if validation fails. In the package top directory::

    $ malicense LICENSE.txt

2: from python::

    import malicense
    malicense.main(package, snap=False)
    # or
    malicense.main(licfilename='LICENSE.txt', snap=False)

where ``package`` is the top level directory. A recommended use is putting that code into an "\_\_init\_\_.py" file, as it is done in the malicense package.


