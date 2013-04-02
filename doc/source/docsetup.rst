==========================================
Work Instruction for Documentation Setup
==========================================

This section describes how to set up the documentation itself

.. toctree::
   :maxdepth: 2

Needed to build documentation
----------------------------------

The following is needed for html or pdf creation

* python 2.7
    * downloads for python 2.7 can be found at `<http://www.python.org/download/releases/2.7.3/>`_ .
* python packages
    * setuptools
        * Documentation on how to install setuptools, along with the package itself, can be found on the Python Package Index at `<http://pypi.python.org/pypi/setuptools>`_. You should install the setuptools targeted for python 2.7
        * You will need to add 'C:\\Python27\\Scripts' to your PATH environment variable if it is not already there
    * Sphinx
        * Once python and setuptools are installed, Sphinx can be installed by typing the following at the windows command line::
        
            easy_install Sphinx

Setting up the documentation sources
------------------------------------

(copied from `<http://sphinx.pocoo.org/tutorial.html>`_)

The root directory of a documentation collection is called the `source
directory <http://sphinx.pocoo.org/glossary.html#term-source-directory>`_.  This directory also contains the Sphinx configuration file
:file:`conf.py`, where you can configure all aspects of how Sphinx reads your
sources and builds your documentation.  

Sphinx comes with a script called :program:`sphinx-quickstart` that sets up a
source directory and creates a default :file:`conf.py` with the most useful
configuration values from a few questions it asks you.  Just run ::

   $ sphinx-quickstart

and answer its questions.  (Be sure to say yes to the "autodoc" extension.)


Creating html documentation
------------------------------------

Once the documentation source directory is set up, with appropriate .rst files, the documentation is created by running the following from the documentation directory::

    $ make html
    
Occasionally, Sphinx gets confused and doesn't update the html correctly.  If this happens, simply run::

    $ make clean
    $ make html

which builds all the documents from scratch.
