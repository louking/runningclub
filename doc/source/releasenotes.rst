=======================================
Planned Enhancements and Release Notes
=======================================
.. toctree::
   :maxdepth: 2
   

*****************
Release Notes
*****************

Running Club Installation
-------------------------

See :doc:`installation`

runningclub 1.4.1
-----------------

* add exportresults to setup.py

runningclub 1.4.0
-----------------

* add exportresults
* initial changes for racedb web app - login stuff mostly

runningclub 0.1
-----------------

* list features

:doc:`importmembers` (new)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Features

* list features for each script


****************************
Planned Enhancements
****************************

:doc:`importmembers`
-------------------------

* etc

****************************
Release Procedure
****************************

release to github
--------------------

* update version.py
* <package>\setup.py install
* commit change "version x.y.z"
* if branch
    * merge branch to master
* sync master to github
* in branch shell
    * git tag x.y.z -m 'version x.y.z'
    * git push --tags
    
py2exe (optional)
-------------------

    * <package>\setup.py py2exe