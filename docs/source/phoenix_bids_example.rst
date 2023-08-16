Example PHOENIX-BIDS structure
==============================

U24 uses ``PHOENIX-BIDS`` structure, which is slightly different from the
``PHOENIX`` structure. ``PHOENIX-BIDS`` was used to have more similarity to the
``BIDS`` structure, while maintaining ``protected`` vs ``general`` and ``raw``
vs ``processed`` concept of the ``PHOENIX``.


Summary of the structure
------------------------

``<protected>/<study>/<processed>/<subject>/<datatypes>`` ::

    PHOENIX/
    ├── PROTECTED
    │   └── PronetAB
    │       ├── raw
    │       │   ├── AB00001
    │       │   │   ├── mri
    │       │   │   ├── eeg
    │       │   │   ├── interviews
    │       │   │   └── ...
    │       │   └── ...
    │       └── processed
    │           └── AB00001
    │               └── ...
    └── GENERAL
            ├── raw
            │   ├── AB00001
            │   │   ├── surveys
            │   │   │   └── AB00001.Pronet.json
            │   │   └── ...
            │   └── ...
            └── processed
                └── AB00001


Different levels of the structure
---------------------------------

**Level 1**: ``GENERAL`` or ``PROTECTED``::
    
    PHOENIX/
    ├── GENERAL
    └── PROTECTED


**Level 2**: Sites (studies) ::

    PHOENIX/
    ├── GENERAL
    │   ├── PronetAB
    │   ├── ...
    │   └── PronetCD
    └── PROTECTED
        ├── PronetAB
        ├── ...
        └── PronetCD


**Level 3**: ``raw`` or ``processed`` 

metadata files are also saved in this level.

::

    PHOENIX/
    ├── GENERAL
    │   ├── PronetAB
    │   │   ├── PronetAB_metadata.csv
    │   │   ├── raw
    │   │   └── processed
    │   ├── ...
    │   └── PronetCD
    │       ├── PronetCD_metadata.csv
    │       ├── raw
    │       └── processed
    └── PROTECTED
        ├── PronetAB
        │   ├── raw
        │   └── processed
        ├── ...
        └── PronetCD
            ├── raw
            └── processed


**Level 4**: Subject ::

    PHOENIX/
    ├── GENERAL
    │   └── PronetAB
    │       ├── raw
    │       │   ├── AB00001
    │       │   ├── AB00002
    │       │   └── AB00003
    │       └── processed
    │           ├── AB00001
    │           ├── AB00002
    │           └── AB00003
    └── PROTECTED
        └── ...


**Level 5**: Data types

``surveys``, ``mri``, ``eeg``, ``interviews``, ``actigraphy`` etc. ::

    PHOENIX/
    ├── PROTECTED
    │   └── PronetAB
    │       ├── raw
    │       │   ├── AB00001
    │       │   │   ├── surveys
    │       │   │   │   └── AB00001.Pronet.json
    │       │   │   ├── mri
    │       │   │   │   ├── AB00001.Pronet.Run_sheet_mri.csv
    │       │   │   │   └── AB00001_MR_2022_01_01_1
    │       │   │   ├── eeg
    │       │   │   │   ├── AB00001.Pronet.Run_sheet_eeg.csv
    │       │   │   │   └── AB00001_eeg_20220101.zip
    │       │   │   ├── interviews
    │       │   │   │   ├── open
    │       │   │   │   ├── psychs
    │       │   │   │   └── transcripts
    │       │   │   └── actigraphy
    │       │   └── ...
    │       └── processed
    │           └── ...
    └── GENERAL
        └── ...



