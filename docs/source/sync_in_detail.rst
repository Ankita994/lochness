Lochness ``sync.py`` function in detail
=======================================

``sync.py`` is the main commandline shell script, which executes the data
sync pipelines of Lochness. This page goes through what the ``sync.py`` does
in more detail, so user can have a deeper understanding of the mechanims.


Loads configuration file, then keyring file
-------------------------------------------

Location of a configuration yaml file is one of the required input to the 
``sync.py``. As briefly explained in the
:doc:`Setting up lochness <setting_up_lochness>`, unique information for
the server, various data sources, and etc. are included in the yaml file and
this file is loaded first, when ``sync.py`` is executed.

Please see the configuration file section for more information.

The encrypted keyring file, location of should have been included in
the configuration file, is also loaded by ``sync.py``.

Please see the keyring file section for more information.

Now Lochness is ready to pull the files.


Creates and updates metadata for each site
------------------------------------------
``Lochness`` first needs to pull information from ``REDCap`` or ``RPMS`` to
get the list of subject IDs registered for each site (``study``). Using the
information loaded from the configuration and keyring files, ``Lochness`` looks
for unique subject IDs, consent date, and their unique mindlamp ID registered
in the ``REDCap`` or ``RPMS`` database. This step will create a
``{site}_metadata.csv`` file under each GENERAL site directory.


.. code-block:: shell

    PHOENIX
    └── GENERAL
        ├── PronetAB
        │   └── PronetAB_metadata.csv
        └── PronetCD
            └── PronetCD_metadata.csv


Here is an example of the ``metadata.csv``, created by Lochness.

eg) ``PronetAB_metadata.csv``

.. csv-table:: 
   :header: "Active", "Consent", "Subject ID", "REDCap", "Box", "XNAT", "Mindlamp"

    1,1900-01-01,AB00001,redcap.Pronet:AB00001;redcap.UPENN:AB00001,box.PronetAB:AB00001,xnat.PronetAB:`*`:AB00001,mindlamp.PronetAB:108230
    1,1900-01-01,AB00002,redcap.Pronet:AB00002;redcap.UPENN:AB00002,box.PronetAB:AB00002,xnat.PronetAB:`*`:AB00002,mindlamp.PronetAB:801230
    1,1900-01-01,AB00003,redcap.Pronet:AB00003;redcap.UPENN:AB00003,box.PronetAB:AB00003,xnat.PronetAB:`*`:AB00003,mindlamp.PronetAB:208103


The columns for each data source get populated with the unique strings, which
are the combination of site (study) and subject ID, in the format that is
readable by Lochness. And this ``metadata.csv`` files are updated at every
sync circulation, therefore any new subjects added to the ``REDCap`` or 
``RPMS`` will be populated into the ``metadata.csv``.


.. note ::

    These metadata files are automatically created and updated by ``lochness``,
    so users should not manually update them.



Pull data for each subject in ``metadata.csv``
----------------------------------------------
Then, ``Lochness`` goes over the list of data sources given to the ``sync.py``
through ``--sources`` argument, checking for any available data that matches
unique subject ID patterns in the ``metadata.csv`` file.


List of data sources focused in AMP-SCZ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**For Pronet**

* REDCap
* UPENN REDCap
* XNAT
* Box
* Mindlamp


**For Prescient**

* RPMS
* UPENN REDCap
* Mediaflux
* Mindlamp


.. warning ::

   Since this step depends on the ``metadata.csv`` file, any data from subjects
   who are not included in the ``metadata.csv`` will not be downloaded by
   Lochness. In another words, any data that belong to a subject who are
   missing from ``REDCap`` or ``RPMS`` will not be downloaded by Lochness.

.. _transfer_selected_data_to_s3_bucket:

Transfer selected data to s3 bucket
------------------------------------
With ``--s3`` option, ``Lochness`` can also transfer file to AWS s3 bucket
using AWS CLI ``rsync`` function. With this argument, at the end of every sync
citculation, the files data under ``PHOENIX/GENERAL`` directory will be
transferred to the s3 bucket.

If any raw data types is okay to be be transferred, as they were downloaded
from their data source, ``--selective_sync`` option can be used to select these
data types. Then all the data under both ``GENERAL`` and ``PROTECTED`` will be
transferred to s3 bucket.
