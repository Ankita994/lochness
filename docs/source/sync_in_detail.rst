Lochness ``sync.py`` function in detail
=======================================

Lochness provides a single command line tool (daemon) to periodically poll
and download data from various web services into a local directory. Out of
the box there is support for pulling data from a multitude of 
`data sources <data_sources.html>`_ including REDCap, XNAT, Dropbox, Box,
Mediaflux, RPMS, external hard drives, and more.


Loads configuration file
------------------------
``Lochness`` loads and sets up configurations based on the information
contained in the ``config.yml``.



Create and update metadata for each site
----------------------------------------
``Lochness`` connects to either ``REDCap`` or ``RPMS`` to download list of
subjects registered for each site (``study``) and creates ::

    PHOENIX
    └── GENERAL
        ├── PronetAB
        │   └── PronetAB_metadata.csv
        └── PronetCD
            └── PronetCD_metadata.csv


eg) ``PronetAB_metadata.csv``

.. csv-table:: 
   :header: "Active", "Consent", "Subject ID", "REDCap", "Box", "XNAT", "Mindlamp"

    1,1900-01-01,AB00001,redcap.Pronet:AB00001;redcap.UPENN:AB00001,box.PronetAB:AB00001,xnat.PronetAB:`*`:AB00001,mindlamp.PronetAB:108230
    1,1900-01-01,AB00002,redcap.Pronet:AB00002;redcap.UPENN:AB00002,box.PronetAB:AB00002,xnat.PronetAB:`*`:AB00002,mindlamp.PronetAB:801230
    1,1900-01-01,AB00003,redcap.Pronet:AB00003;redcap.UPENN:AB00003,box.PronetAB:AB00003,xnat.PronetAB:`*`:AB00003,mindlamp.PronetAB:208103


These metadata files are automatically created and updated by ``lochness``, so
users should not manually update them.


Pull data for each subject in ``metadata.csv``
----------------------------------------------
``Lochness`` goes over each source, checking and pulling data for each subject.

.. warning ::

   Since this step depends on the ``metadata.csv`` file, any data from subjects
   who are not included in the ``metadata.csv`` will not be downloaded by
   Lochness. In another words, any data that belong to a subject who are
   missing from ``REDCap`` or ``RPMS`` will not be downloaded by Lochness.


Transfer selected data to s3 bucket
------------------------------------
With ``--s3`` option, ``Lochness`` will transfer file to AWS S3 bucket using
AWS CLI ``rsync`` function.

