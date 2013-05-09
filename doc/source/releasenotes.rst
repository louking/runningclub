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