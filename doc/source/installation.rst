Running Club Installation
================================

.. toctree::
   :maxdepth: 2

Administrator Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Considerations
------------------

* determine if you want this to be a single user system, meaning only one user can update membership data in the database, update race results and generate standings, or if you want multiple users to be able to access the system

    * an example of a multiuser system would be if one person is responsible for (say) the grand prix race series, and another person is responsible for (say) the decathlon race series

Requirements
--------------

* windows PC
* python 2.7.x 32 bit
* database installation alternatives
    * sqlite - single user database - downloads can be found at http://www.sqlite.org/download.html
    * mysql workbench - multi user database - downloads and prerequisites found at http://dev.mysql.com/downloads/workbench/

User Installation
^^^^^^^^^^^^^^^^^^^^

Prior to installation of mbmss, the following should be installed on the target machine, in the following order:

* windows PC
* python 2.7.x 32 bit 
    * add C:\Python26;C:\Python26\Scripts;C:\cygwin\bin to PATH environment variable
    * setuptools
    * numpy
    * matplotlib
    
**python 2.6.6** -- downloads for python 2.6 can be found at `<http://www.python.org/download/releases/2.6.6/>`_ .   It is possible that mbmss would work under python 2.7, but that hasn't been tested.  It is unlikely that mbmss would work under python 3.x.

* download the Windows x86 MSI Installer (or the x86-64 MSI Installer, if you have a 64 bit machine)
* run the MSI installer and accept all the defaults.  Note if you put the Python26 directory in the default location, <PYTHONHOME> will be C:\\Python26

**setuptools** -- Documentation on how to install setuptools, along with the package itself, can be found on the Python Package Index at `<http://pypi.python.org/pypi/setuptools>`_.  You should install the setuptools targeted for python 2.6.

* download the latest file similar to setuptools-<version>.win32-py2.6.exe (must be py2.6.exe)
* run the installer and accept all the defaults

**numpy / matplotlib** -- numpy and matplotlib python packages are used by mbmss, and do not seem to get loaded automatically.  These can be found on sharepoint within the Hughes intranet at `<http://hughesweb.hughes.com/sites/eng/msat/globalstar/Shared%20Documents/Script%20Repository>`_ .

* download and unzip numpymatplot.zip
* run the installer for numpy and accept all the defaults
* run the installer for matplotlib and accept all the defaults

**pypi packages** - can be found on the Python Package Index at `<http://pypi.python.org/pypi/setuptools>`_ .  Once setuptools has been installed, assuming internet access, these packages can be installed using easy_install, e.g., easy_install PyDAQmx, or easy_install ooxml

**goccutils** -- goccutils can be found on sharepoint within the Hughes intranet at `<http://hughesweb.hughes.com/sites/eng/msat/globalstar/Shared%20Documents/Script%20Repository>`_.  Download the egg file named mbmss-<ver>-py2.6.egg to <your-directory>, where <ver> is replaced by the goccutils version (use the latest).

**mbmss** -- mbmss can be found on sharepoint within the Hughes intranet at `<http://hughesweb.hughes.com/sites/eng/msat/globalstar/Shared%20Documents/Script%20Repository>`_.  Download the egg file named mbmss-<ver>-py2.6.egg to <your-directory>, where <ver> is replaced by the mbmss version (use the latest).

Assuming the requirements above have been installed, goccutils and mbmss can be installed from any command window using the following (in this case <ver> is '1.1')::

    > cd <your-directory>
    > easy_install mbmss-1.1-py2.6.egg

**script execution**

* After installation, any of the scripts should be runnable from the command line, e.g., ::

    $ runmbmss --version

For convenience, the following packages / programs can be installed as well:

* notepad++
* teamviewer (975548451 - password mbmss123)
* cygwin (all)
* putty
* iPython

Development information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

blah