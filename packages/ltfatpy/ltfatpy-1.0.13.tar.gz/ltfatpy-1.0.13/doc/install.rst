Installation
############

.. toctree::


Prerequisites
=============

Before installing **ltfatpy** you must check that the following software are installed on your system.

CMake
-----
A version of `cmake <https://cmake.org/>`_ >= 2.6 is required to install **ltfatpy**.
To install **CMake** follow the instructions given `here <https://cmake.org/install/>`__.

Python
------

* Make sure you have **python** >= 2.7 installed. If not follow the instructions from `here <https://wiki.python.org/moin/BeginnersGuide/Download>`__.
* According to your python version, make sure you have **pip** installed. If not follow the instructions from `here <https://pip.pypa.io/en/stable/installing/>`__.

For developpers only:

* If you need to recompile the whole ltfatpy C kernel interface you have to install **cython** >= 0.21.
* It can be installed by following the instructions given `here <http://docs.cython.org/src/quickstart/install.html>`__.

Scientific Python libraries
---------------------------

* You need to have **libfftw3**, development version, installed. 
    * For debian based linux systems use: ``$apt install libfftw3-dev``.
    * For MACOS X based systems, you may use: ``sudo port install fftw-3 fftw-3-single``.
    * For other systems, please read the documentation of `fftw <http://www.fftw.org/>`_.
* **ltfatpy** is using **numpy** >= 1.9, **scipy** >= 0.15 and **matplotlib** >= 1.4. For installing those packages read the instructions `here <http://www.scipy.org/install.html>`__.

Downloading **ltfatpy**
========================

* The last stable release of **ltfatpy** is available on `PyPI <https://pypi.python.org/pypi/ltfatpy>`_.
* You can clone the git repository of **ltfatpy** from `here <https://gitlab.lis-lab.fr/dev/ltfatpy>`__.

Installing **ltfatpy**
========================

From sources
------------

From ltfatpy-x.x.x/ directory use ``pip install .``

From PyPI
---------

Just use : ``pip install ltfatpy``

Building documentation with Sphinx
==================================

Make sure you have Sphinx installed as described `here <http://sphinx-doc.org/tutorial.html#install-sphinx>`__.

Before building documentation you have to install **sphinxcontrib-bibtex** :
``pip install sphinxcontrib-bibtex``

Then you have to use the setup.py build_sphinx command :
``python setup.py build_sphinx``

If errors occur, make sure you installed ltfatpy before building the sphinx documentation.
