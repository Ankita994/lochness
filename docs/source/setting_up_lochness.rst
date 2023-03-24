Setting up Lochness
===================

The following items below are the step by step instructions to
semi-automatically setup the lochness environment. It is specific for
AMP-SCZ project, but it could also work for any other projects, if their main
subject database is maintained with ``REDCap`` or ``RPMS`` system.

If you would like to set up your environment from scratch, please see the pages
for 

* :doc:`configuration file<configuration_file>`
* :doc:`keyring file<keyring_file>`
* :doc:`setting up data sources<data_sources>`


1. Create a template directory
------------------------------
``lochness_create_template.py`` will help you create a starting point for your
lochness. ``config.yml``, ``PHOENIX``, and keyring files, as well as two bash
scripts for encrypting the keyring file and running the sync, will be created.

**For Pronet network**

.. code-block:: shell

   lochness_create_template.py \
       --outdir /data/pronet/data_sync_pronet \
       --studies PronetLA PronetOR PronetBI PronetNL PronetNC PronetSD \
                 PronetCA PronetYA PronetSF PronetPA PronetSI PronetPI \
                 PronetNN PronetIR PronetTE PronetGA PronetWU PronetHA \
                 PronetMT PronetKC PronetPV PronetMA PronetCM PronetMU \
                 PronetSH PronetSL \
       --sources redcap upenn box xnat mindlamp \
       --email kevincho@bwh.harvard.edu \
       --poll_interval 86400 \
       --ssh_host 123.456.789 \
       --ssh_user kc244 \
       --lochness_sync_send \
       --s3 \
       --s3_selective_sync surveys mri phone eeg actigraphy


**For Prescient network**

.. code-block:: shell

    lochness_create_template.py \
        --outdir /data/prescient/data_sync_prescient \
        --studies PrescientME PrescientSG PrescientAD PrescientAM PrescientBM \
                  PrescientCL PrescientCP PrescientHC PrescientJE PrescientGW \
                  PrescientLS \
        --sources rpms upenn mediaflux mindlamp \
        --email kevincho@bwh.harvard.edu \
        --poll_interval 86400 \
        --ssh_host 123.456.789 \
        --ssh_user kc244 \
        --lochness_sync_send \
        --s3 \
        --s3_selective_sync surveys mri phone eeg actigraphy


.. note ::
    
   Add ``--enter_password`` option if you want ``lochness_create_template.py``
   to add your credentials to the template keyring file.
   


Running the command above will create a directory which will look like this ::

    /data/pronet/data_sync_pronet
    ├── 1_encrypt_command.sh
    ├── 2_sync_command.sh
    ├── PHOENIX
    │   ├── GENERAL
    │   │   ├── PronetAB
    │   │   │   └── PronetAB_metadata.csv
    │   │   ├── ...
    │   │   └── PronetYA
    │   │       └── PronetYA_metadata.csv
    │   └── PROTECTED
    │       ├── PronetAB
    │       ├── ...
    │       └── PronetYA
    ├── config.yml
    ├── lochness.json
    └── pii_convert.csv


.. note ::

   To see detailed options of `lochness_create_template.py`

   .. code-block:: shell

        lochness_create_template.py -h


Step 1 completed.



2. Edit credentials in the template keyring file
------------------------------------------------

Connecting to various external `data sources <data_sources.html>`_
(REDCap, XNAT, Box, etc.) often requires a myriad of connection details 
e.g., URLs, usernames, passwords, API tokens, etc. Lochness will only read 
these pieces of information from an encrypted JSON file that we refer to as 
the *keyring*.


These information needs be added to the ``lochness.json`` template


.. code-block:: shell

   cd /data/pronet/data_sync_pronet  # the template directory created above
   vim lochness.json


``lochness.json`` file looks like below. Add credentials to the fields marked
with ``*****``

.. code-block:: json

    {
      "lochness": {
        "REDCAP": {
          "PronetLA": {
            "redcap.Pronet": [
              "Pronet"
            ],
            "redcap.UPENN": [
              "UPENN"
            ]
          },
          ...,
        },
        "SECRETS": {
          "PronetLA": "LOCHNESS_SECRETS",
          ...,
        }
      },
      "redcap.UPENN": {
        "URL": "*****",
        "API_TOKEN": {
          "UPENN": "*****"
        }
      },
      "redcap.Pronet": {
        "URL": "*****",
        "API_TOKEN": {
          "Pronet": "*****"
        }
      },
      "xnat.PronetLA": {
        "URL": "*****",
        "USERNAME": "*****",
        "PASSWORD": "*****"
      },
      ...,
      "box.PronetLA": {
        "CLIENT_ID": "*****",
        "CLIENT_SECRET": "*****",
        "ENTERPRISE_ID": "*****"
      },
      ...,
      "mindlamp.PronetLA": {
        "URL": "*****",
        "ACCESS_KEY": "*****",
        "SECRET_KEY": "*****"
      },
      ...,
    }


.. note ::

   If you have used ``--enter_password`` option when creating the template
   files, just check through your credentials if they are correctly entered to
   the ``keyring.json`` file.

    
Example of completed ``lochness.json``

.. code-block:: json

    {
      "lochness": {
        "REDCAP": {
          "PronetLA": {
            "redcap.Pronet": [
              "Pronet"
            ],
            "redcap.UPENN": [
              "UPENN"
            ]
          },
          ...,
        },
        "SECRETS": {
          "PronetLA": "LOCHNESS_SECRETS",
          ...,
        }
      },
      "redcap.UPENN": {
        "URL": "https://redcap.med.upenn.edu",
        "API_TOKEN": {
          "UPENN": "BC6BEF2D2369BC8FE1233CAAAB20378D"
        }
      },
      "redcap.Pronet": {
        "URL": "https://redcapynh-p11.ynhh.org"
        "API_TOKEN": {
          "Pronet": "AFBDCCD55934EE947A388541EED6A216"
        }
      },
      "xnat.PronetLA": {
        "URL": "https://xnat.med.yale.edu",
        "USERNAME": "kcho",
        "PASSWORD": "whrkddlr8*90"
      },
      ...,
      "box.PronetLA": {
        "CLIENT_ID": "e19fltqp9f9ftv4dydqjius4w20072cr",
        "CLIENT_SECRET": "LrkDwYZvA49Q4dXVGv3g4aaSy4SQRobz",
        "ENTERPRISE_ID": "756591"
      },
      ...,
      "mindlamp.PronetLA": {
        "URL": "mindlamp.orygen.org.au",
        "ACCESS_KEY": "kcho",
        "SECRET_KEY": "0c5b0a5af972b2a1b2d6cd299dc37703c22e8ddd5dfd15f0d83ca7a1cb8bcce7"
      },
      ...,
    }



.. note::

   If you're using Google SMTP in sending out email, you need to add
   ``"email_sender_pw": "PasswordForYourGoogleAccount"``

   For an example,

   .. code:: json

        "SECRETS": {
          "PronetLA": "LOCHNESS_SECRETS",
          ...,
        }
        "email_sender_pw": "aaoiweytyEfhag189e7"



3. Encrypt ``lochness.json`` to make a keyring file
---------------------------------------------------

Once required credentials are added to the template ``lochness.json`` keyring
file, it must be encrypted using a passphrase. At the moment, Lochness only
supports encrypting and decrypting files (including the keyring) using the
`cryptease <https://github.com/harvard-nrg/cryptease>`_ library. This library
should be installed automatically when you install Lochness, but you can
install it separately on another machine as well.

Encrypt the temporary keyring file by running

.. code-block:: shell

    crypt.py --encrypt lochness.json -o .lochness.enc


.. note ::
    Or you could run `2_sync_command.sh`, which contains the same command

    .. code-block:: shell

        bash 1_encrypt_command.sh


.. attention::
   I'll leave it up to you to decide on which device you want to encrypt this
   file. I will only recommend discarding the decrypted version as soon as 
   possible.


.. _edit_config ::

4. Edit configuration file
--------------------------
``config.yml`` file contains details of options to be used in Lochness.

.. code-block:: console

    vim config.yml


Project name
~~~~~~~~~~~~~
Name of the project. This string will be included in the daily email summary.

.. code-block:: shell

    project_name: ProNET
    or
    project_name: Prescient



REDCap or RPMS database column names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update names of the ``REDCap`` or ``RPMS`` columns that contain unique subject
ID and consent date of each stubject.

For REDCap ::

    redcap_id_colname: chric_record_id
    redcap_consent_colname: chric_consent_date


For RPMS ::

    RPMS_PATH: /mnt/prescient/RPMS_incoming
    RPMS_id_colname: subjectkey
    RPMS_consent_colname: Consent

.. note ::

   ``RPMS_PATH`` is the directory where ``RPMS`` exports database as multiple
   csv files.

If there is a limit on how much data you can download in a given time on your
REDCap server, please see :doc:`data entry trigger<data_entry_trigger>`.




Amazon Web Services S3 bucket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update AWS s3 bucket name to your s3 bucket name and root directory ::

    AWS_BUCKET_NAME: pronet-test
    AWS_BUCKET_ROOT: TEST_PHOENIX_ROOT_PRONET



Remove old & already s3-transferred files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lochness will read the following information from the configuration file to
remove already transferred files from the local PHOENIX directory. ::

    days_to_keep: 100
    removed_df_loc: /mnt/prescient/Prescient_data/PHOENIX/removed_files.csv
    removed_phoenix_root: prescient/Prescient_data/track_removed_files_PHOENIX


Box
~~~
See :doc:`here<box_source_structure>` for how to configure Box source. Then,
the configure file should have a ``box`` session that states which file
patterns to look for in each study. 

``base`` is the root of the data directory for the study under ``Box``. If your
data for ``PronetAB`` is saved under ``ProNET/PronetAB`` under the root of Box
source, the base for this study should be ``ProNET/PronetAB``.

``delete_on_success`` is an option for removing the source files on the Box
once lochness successfully downloads them. ``True`` or ``False``

``file_patterns`` takes list of different datatypes to be captured in from the
Box. ``data_dir`` of each datatype is the name of the root directory that has
subject directories for this datatype. And each datatype can have more than one
product of files to look for. For an example, for ``interviews`` datatype,
``open``, ``psychs``, and ``transcripts`` products are searched for each
individual.  ``out_dir`` can be specified if the files need to be saved under
a specific subdirectory for a product.


.. code-block:: shell

    box:
        PronetAB:
            base: ProNET/PronetAB
            delete_on_success: False
            file_patterns:
                actigraphy:
                       - vendor: Activinsights
                         product: GENEActiv
                         data_dir: PronetAB_Actigraphy
                         pattern: '*.*'
                eeg:
                       - product: eeg
                         data_dir: PronetAB_EEG
                         pattern: '*.*'
                interviews:
                       - product: open
                         data_dir: PronetAB_Interviews/OPEN
                         out_dir: open
                         pattern: '*.*'
                       - product: psychs
                         data_dir: PronetAB_Interviews/PSYCHS
                         out_dir: psychs
                         pattern: '*.*'
                       - product: transcripts
                         data_dir: PronetAB_Interviews/transcripts/Approved
                         out_dir: transcripts
                         pattern: '*.*'

See :doc:`here<box_source_structure>` for an example of output PHOENIX
structure from this configuration.


Mediaflux
~~~~~~~~~

See :doc:`here<mediaflux_source_structure>` for how to configure Box. Then, the 
configure file should have a ``box`` session that states which file patterns
to look for in each study. 


.. code-block:: shell

    box:
        PrescientAB:
            base: ProNET/PrescientAB
            delete_on_success: False
            file_patterns:
                actigraphy:
                       - vendor: Activinsights
                         product: GENEActiv
                         data_dir: PrescientAB_Actigraphy
                         pattern: '*.*'
                eeg:
                       - product: eeg
                         data_dir: PrescientAB_EEG
                         pattern: '*.*'
                mri:
                       - product: mri
                         data_dir: PrescientAB_MRI
                         pattern: '*.*'
                interviews:
                       - product: open
                         data_dir: PrescientAB_Interviews/OPEN
                         out_dir: open
                         pattern: '*.*'
                       - product: psychs
                         data_dir: PrescientAB_Interviews/PSYCHS
                         out_dir: psychs
                         pattern: '*.*'
                       - product: transcripts
                         data_dir: PrescientAB_Interviews/transcripts/Approved
                         out_dir: transcripts
                         pattern: '*.*'

See :doc:`here<mediaflux_source_structure>` for an example of output PHOENIX
structure from this configuration.


Email function
~~~~~~~~~~~~~~

Update ``sender`` and ``notify`` fields. ``sender`` should be the google email
configured for sending emails with its relevant credentials in the keyring
file. List of emails, to which lochness should send the email should be added
under ``__global__`` field with ``-`` marking each email. ::


    sender: kevincho.lochness@gmail.com
    notify:
        __global__:
            - kevincho@bwh.harvard.edu
            - another.person.to.receive.email.1@u24.com
            - another.person.to.receive.email.2@u24.com


Now, your Lochness configuration is complete and ready to run!

