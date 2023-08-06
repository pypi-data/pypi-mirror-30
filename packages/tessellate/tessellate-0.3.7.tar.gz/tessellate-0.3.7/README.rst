==========
Tessellate
==========


.. image:: https://img.shields.io/pypi/v/tessellate.svg
        :target: https://pypi.python.org/pypi/tessellate

.. image:: https://readthedocs.org/projects/tessellate/badge/?version=latest
        :target: https://tessellate.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.1068656.svg
   :target: https://doi.org/10.5281/zenodo.1068656
   
A package for quantifying cyclic molecule conformations.


* Free software: Apache Software License 2.0
* Documentation: https://tessellate.readthedocs.io.

Using
-----

.. code:: bash

    make install; tessellate  data/example-builtin --input-format=builtin --output-format=json
    make install; tessellate  data/*DNA --input-format=pdblist --output-format=json

Installing
----------
- Use Python3. For example, Anaconda Python https://www.anaconda.com/download/ https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
- Use a virtual environment or conda environment.
- Install with pip or compile the source code

.. code:: bash

    # installing with pip
    pip install tessellate

    # Alternatively: compile from source
    make install


Usecase 1 - timeseries data
---------------------------

.. code:: bash

    tessellate  data/usecase-timeseries --input-format=builtin --output-format=json --output-dir=output-usecase-timeseries

This data is from an in vacuo ribose simulation stored in data/timeseries-from-VMD
To recreate data use the run.sh script. This calls VMD and runs pucker-bigdcd.tcl.

Usecase 2 - RNA and DNA
-----------------------

.. code:: bash

    tessellate  data/usecase-*DNA --input-format=pdblist --output-format=json --output-dir=output-usecase-rnadna

Usecase 3 - Alpha Cyclodextrin
------------------------------

.. code:: bash

    tessellate  data/usecase-*CD --input-format=pdblist --output-format=json --output-dir=output-usecase-cyclodextrin

Run All Usecases
----------------

.. code:: bash

    tessellate  data/usecase-timeseries --input-format=builtin --output-format=json --output-dir=output-usecase-timeseries
    tessellate  data/usecase-*DNA --input-format=pdblist --output-format=json --output-dir=output-usecase-rnadna
    tessellate  data/usecase-*CD --input-format=pdblist --output-format=json --output-dir=output-usecase-cyclodextrin

Additional UseCases
-------------------

- `Pandas Dataframes`_  Supported with --output-format=pandas
- `Using Tessellate as a library`_


Viewing Data
------------

Try out Montage to create reports for these datasets.
For example:

.. code:: bash
    USECASE_DATA=output-usecase-cyclodextrin
    multiqc $USECASE_DATA -m comp_tessellate -f  # -f to overwrite existing reports
    google-chrome multiqc_report.html

Compare all outputs:

.. code:: bash
    multiqc output* -m comp_tessellate -f  # -f to overwrite existing reports
    google-chrome multiqc_report.html


Development
-----------
Bump version numbers using bumpversion
X=thecurrentversion
`bumpversion  --current-version X minor`

To bump from x.y.z to x.y.a use patch as the part:
`bumpversion  --current-version X patch`

Features to include:
--------------------

* Improve testing and documentation. Port existing tests over. 
* Tables
* include more RAD functionality

Uploading to PyPi
-----------------
Use twine

.. code:: bash
    conda install -c conda-forge twine
    make install
    make dist
    twine upload dist/*

Issues
------
Report Issues at https://github.com/scientificomputing/tessellate/issues 
Known issue - only relative paths supported



Read the Docs
-------------
Docs are here. RTD is authorised to access GitHub repos. The RTD service hook builds doc on push.


Pandas Dataframes
-----------------
.. code:: bash

    tessellate  data/usecase-timeseries --input-format=builtin --output-format=pandas --output-dir=output-usecase-timeseries

.. code:: python 
    python
    import pandas as pd
    df = pd.read_json('output-usecase-timeseries/tessellate_report_usecase-timeseries.pandas.json')
    df.head()
    df.groupby('conformer').count()
    df.groupby(['ringsize','conformer']).count()

Using Tessellate as a library
-----------------------------

.. code:: python
    import tessellate as t
    import tessellate.utils.pucker as p
    import collections
    ordered_ringatoms=['C3','C4','C5','O5','C1','C2']
    frame={'C1': (-5.799, -5.308, 4.847), 'C2': (-5.383, -5.328, 3.394), 'C3': (-3.904, -4.906, 3.181),'C4': (-3.576, -3.54, 3.944), 'C5': (-4.115, -3.556, 5.339), 'O5': (-5.551, -3.941, 5.38)}
    def return_pucker(atomids,frame):
     import tessellate as t
     import tessellate.utils.pucker as p
     import itertools
     a=[frame[i] for i in atomids]
     pobj=p.Pucker(tuple(itertools.chain.from_iterable(a)))
     return pobj.calculate_triangular_tessellation(), pobj.deduce_canonical_conformation()[0],pobj.deduce_canonical_conformation()[-1],pobj.deduce_canonical_conformation(nextguess=True)[0]
    
    result=collections.OrderedDict()
    result["pucker"],result["pucker_conformer"],result["pucker_distance_to_canonical"],result["pucker_next_guess"] = return_pucker(ordered_ringatoms, frame)
    import pprint
    pprint.pprint(result)

Credits
---------

This package incorporates work from existing packages (all originally developed by Chris B. Barnett.)
* https://bitbucket.org/scientificomputing/triangular-tessellation-class http://git.cem.uct.ac.za/analysis-pucker/triangular-tessellation-class
* https://bitbucket.org/scientificomputing/ring-analytics-webserver https://bitbucket.org/rxncor/rad-dev http://git.cem.uct.ac.za/analysis-pucker/ring-analytics-dash
* https://bitbucket.org/scientificomputing/triangular-tessellation-in-vmd http://git.cem.uct.ac.za/analysis-pucker/triangular-decomposition-timeseries-in-VMD

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

