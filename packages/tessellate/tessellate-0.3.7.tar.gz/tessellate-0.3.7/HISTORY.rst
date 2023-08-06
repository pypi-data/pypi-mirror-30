=======
History
=======

0.3.7 (2018-03-29)
------------------
* Pandas! 
* Pandas dataframe output in json and csv is the default
* make Pandas default
* how to use a library example in the README
* biopython and pytest have different signatures beneath a certain version. Fixed this in setup.py
* removed hardcoded python interpreter, in some cases machine point to python2.7 with python3 pointing to 3. Remove in *.py files. Removed in Makefile. To use another python in the make file, modify the pythonexe variable
* Tested with --user flag. --user flag seems to work for me - e.g. pip3 install --user tessellate

0.3.6 (2017-12-18)
------------------
* Zenodo DOI
* empty list bug resolved 
* feature order json output

0.3.5 (2017-11-30)
------------------
* Includes tcl script for VMD and example data

0.3.4 (2017-11-29)
------------------
* Documentation update. Ring finder update

0.3.1 0.3.2 0.3.3  (2017-11-24)
------------------
* Usecase, documentation update. Update requirements for PyPi

0.3.0 (2017-11-23)
------------------
* First release on PyPi

0.2.0 (2017-11-23)
------------------
* Alpha version that can read PDBlists and builtin, can write json
* Include examples and much verbose logging

0.1.0 (2017-11-21)
------------------

* Alpha version. Basic function
