Configuration file
==================

The folling page will go over all of the configuration file sections, fields, 
and what each one does.

Example configuration file:

.. code-block :: text

    keyring_file: /Users/kc244/data_sync/.lochness.enc
    phoenix_root: /Users/kc244/data_sync/PHOENIX
    pid: /Users/kc244/data_sync/lochness.pid
    stderr: /Users/kc244/data_sync/lochness.stderr
    stdout: /Users/kc244/data_sync/lochness.stdout
    poll_interval: 86400
    ssh_user: kc244
    ssh_host: rgs09.research.partners.org
    sender: kevincho@bwh.harvard.edu
    mindlamp_days_to_pull: 100
    pii_table: /Users/kc244/data_sync/pii_table.csv
    lochness_sync_history_csv: /Users/kc244/data_sync/sync_history.csv

    # REDCap
    redcap_id_colname: chric_record_id
    redcap_consent_colname: chric_consent_date

    # RPMS
    RPMS_PATH: /Users/kc244/RPMS_incoming
    RPMS_id_colname: subjectkey
    RPMS_consent_colname: Consent

    AWS_BUCKET_NAME: prescient-test
    AWS_BUCKET_ROOT: TEST_PHOENIX_ROOT_PRESCIENT
    s3_selective_sync: mri,surveys,actigraphy

    redcap:
        {study}:
            deidentify: True
            data_entry_trigger_csv: {args.det_csv}
            update_metadata: True'''
    box:
        {study}:
            base: ProNET/{study}
            delete_on_success: False
            file_patterns:
                actigraphy:
                       - vendor: Activinsights
                         product: GENEActiv
                         data_dir: {study}_Actigraphy
                         pattern: '*.*'
                eeg:
                       - product: eeg
                         data_dir: {study}_EEG
                         pattern: '*.*'
                interviews:
                       - product: open
                         data_dir: {study}_Interviews/OPEN
                         out_dir: open
                         pattern: '*.*'
                       - product: psychs
                         data_dir: {study}_Interviews/PSYCHS
                         out_dir: psychs
                         pattern: '*.*'
                       - product: transcripts
                         data_dir: {study}_Interviews/transcripts/Approved
                         out_dir: transcripts
                         pattern: '*.*'
    admins:
        - kevincho@bwh.harvard.edu
    notify:
        __global__:
            - kevincho@bwh.harvard.edu



keyring_file
------------
This field specifies the location of your ``keyring`` file. This should be 
a simple filesystem location ::

    keyring_file: ~/.keyring.enc


phoenix_root
------------
This field determines the root location of your PHOENIX filesystem. This 
should be a simple filesystem location ::

    phoenix_root: /data/PHOENIX


stdout
------
This field determines the location of the Lochness process standard output ::

    stdout: /logs/lochness.out


stderr
------
This field determines the location of the Lochness process standard error ::

    stderr: /logs/lochness.err


poll_interval
-------------
This field determines the frequency at which Lochness will poll external data
sources for incoming data (in seconds) ::

    poll_interval: 43200


ssh_user
--------
Occasionally, you may receive data on an external hard drive or flash drive.
If you want to use Lochness to transfer this data to your PHOENIX filesystem,
you can do this over ``rsync+ssh``. The ``ssh_user`` field determines the
username that will be used for this ::

    ssh_user: example


ssh_host
--------
Occasionally, you may receive data on an external hard drive or flash drive.
If you want to use Lochness to transfer this data to your PHOENIXfilesystem,
you can do this over ``rsync+ssh``. The ``ssh_host`` field determines the
destination host you will connect to for this ::

    ssh_host: host.example.org


sender
------
Whenever an email is sent by Lochness, use this field to determine the sender
address ::

    sender: lochness@host.example.org


mindlamp_days_to_pull
---------------------
Mindlamp data can have a large size, which may require a long time to check the
database on the Mindlamp server. This field determines how many days, from the
day of running sync, to check the Mindlamp database for. ::

    mindlamp_days_to_pull: 100


pii_table
---------
This field determines the location of the csv file that has the mappings for
each personally identifiable information (PII) to how to process them. It is
used to process the PII field values in both REDCap and RPMS sources. ::

    poll_interval: ~/pii_convert_table.csv


lochness_sync_history_csv
--------------------------
This field determines the location of the csv file that has the history of
lochness to lochness data transfer timestamp. If the csv file is missing, the
timestamp of the next lochness to lochness will be stored to a csv file in the
given location.

    lochness_sync_history_csv: /data/lochness_sync_history.csv


redcap_id_colname and redcap_consent_colname
--------------------------------------------
These fields determine the name of records on the REDCap database for the
unique subject ID and consent date. ::

    redcap_id_colname: chric_record_id
    redcap_consent_colname: chric_consent_date
 

RPMS_PATH, RPMS_id_colname, and RPMS_consent_colname
----------------------------------------------------
``RPMS_PATH`` determines the root path of RPMS database export directory, which
must be on the same server as Lochness. ``RPMS_id_colname`` and
``RPMS_consent_colname`` fields determine the name of records on the RPMS
database for the unique subject ID and consent date. ::

    RPMS_PATH: /Users/kc244/RPMS_incoming
    RPMS_id_colname: subjectkey
    RPMS_consent_colname: Consent


AWS_BUCKET_NAME and AWS_BUCKET_ROOT
-----------------------------------
These fields determine the name of AWS s3 bucket, and the path of the root to
transfer the data to. ::

    AWS_BUCKET_NAME: prescient-test
    AWS_BUCKET_ROOT: TEST_PHOENIX_ROOT_PRESCIENT


s3_selective_sync
-----------------
This field determines the list of data types, that Lochness could transfer
the raw data without any processing, as they were downloaded from their data
sources. All the data, even the data under ``PROTECTED`` for these selected
datatypes will be transferred to s3 bucket. ::

    s3_selective_sync: mri,surveys,actigraphy


redcap
------
This field determines the list of data types, that Lochness could transfer
the raw data without any processing, as they were downloaded from their data
sources. All the data, even the data under ``PROTECTED`` for these selected
datatypes will be transferred to s3 bucket. ::

    s3_selective_sync: mri,surveys,actigraphy


beiwe
-----
The ``beiwe`` section is used to configure how Lochness will behave while downloading
data from the `Beiwe <https://beiwe.org>`_.


backfill_start
~~~~~~~~~~~~~~
The ``backfill_start`` field should be an ISO 8601 formatted timestamp.  If you do not 
add a ``backfill_start`` date, the start date will fall back to the date that Beiwe 
was initially released ::

    2015-10-01T00:00:00

If you set the ``backfill_start`` field to the string ``consent``, Lochness will use 
the subject ``Consent Date`` from the PHOENIX `metadata file <phoenix.html#metadata-files>`_
as the backfill starting point.

A valid ``backfill_start`` field should look like this ::

    beiwe:
      backfill_start: consent

or like this ::

    beiwe:
      backfill_start: 2020-01-01

dropbox
-------
The ``dropbox`` section is used to configure how Lochness will behave when 
downloading data from `Dropbox <https://dropbox.com>`_.

delete on success
~~~~~~~~~~~~~~~~~
You can add a ``delete_on_success: True`` field to indicate that any data successfully
downloaded from a specific Dropbox account should be subsequently deleted from Dropbox 
to save space. You can configure ``delete_on_success`` for each Dropbox account defined 
in your ``keyring``. 

The resulting section should look as follows ::

    dropbox:
      example:
        delete_on_success: True

dropbox base
~~~~~~~~~~~~
For each Dropbox account, you may add a ``base`` field to the configuration file to 
indicate that Lochness should begin searching Dropbox starting at that location. 

The resulting section should look as follows ::

    dropbox:
      example:
        base: /PHOENIX

box
---
The ``box`` section is used to configure how Lochness will behave when 
downloading data from `Box <https://box.com>`_.


delete on success
~~~~~~~~~~~~~~~~~
You can add a ``delete_on_success: True`` field to indicate that any data successfully
downloaded from a specific Box account should be subsequently deleted from Box 
to save space. You can configure ``delete_on_success`` for each Box account defined 
in your ``config.yml``. 

The resulting section should look as follows ::

    box:
      xxxxx:
        delete_on_success: True

box base
~~~~~~~~
For each Box account, you may add a ``base`` field to the configuration file to 
indicate that Lochness should begin searching Box starting at that location. 
``file_patterns`` field will have the name of directory under the `base`
directory, with subfields. 

The subfields are 
- ``vendor``, ``product``: currently not used by `lochness`.
- ``pattern``: string pattern of the files in interest. The files with matching
               names will be pulled.
- ``compress``: if True, the matching files will be downloaded and compressed.
- ``protect``: if True, the files are downloaded under the `PROTECTED` directory.

The resulting section should look as follows ::

    box:
        xxxxx: 
            base: xxxxx_dir
            delete_on_success: False
            file_patterns:                 
                actigraphy:
                       - vendor: Philips
                         product: Actiwatch 2
                         pattern: '.*\.csv'
                       - vendor: Activinsights
                         product: GENEActiv
                         pattern: 'GENEActiv/.*(\.csv|\.bin)'
                         compress: True
                mri_eye:
                       - vendor: SR Research
                         product: EyeLink 1000
                         pattern: '.*\.mov'


mediaflux
---------
A standalone documentation for the interaction between Mediaflux and lochness is available `here <./mediaflux.md>`_.
Specifically, you can take a look at `mediaflux#configuration-file <./mediaflux.md#configuration-file>`_.

redcap
------
For each PHOENIX study, you may add an entry to the ``redcap`` section indicating 
that data should be de-identified before being downloaded and saved to PHOENIX.

``data_entry_trigger_csv`` determines the location of the database created
by the `listen_to_recap.py` by storying the **Data Entry Trigger** post signals
from REDCap.

Assuming your PHOENIX study is named ``StudyA`` this field would look like so ::

    redcap:
      data_entry_trigger_csv: ~/data_entry_trigger_database.csv
      StudyA:
        deidentify: True



admins
------
All email addresses defined in the ``admins`` section will be notified on all emails 
sent out by Lochness ::

    admins:
     username@email.com

notify
------
The ``notify`` section allows you to configure more detailed notification behavior. 
You can use this section to set different groups of email addresses to be notified 
in the event of an error downloading files on a per study basis ::

     notify:
      StudyA:
        - username1@email.com
        - username2@email.com
      StudyB:
        - username3@email.com

You can also use a ``__global__`` field to add email addresses that should be 
notified on any error for any study, similar to the `admins <#admins>`_ 
section ::

    notify:
      __global__:
        - admin1@email.com

