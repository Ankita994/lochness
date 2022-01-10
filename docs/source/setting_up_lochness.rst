Setting up Lochness
===================

The following items below are the step by step instructions to
semi-automatically setup the lochness environment. It is specific for
AMP-SCZ project, but it could also work for any other projects, if their main
subject database is maintained with a ``REDCap`` or ``RPMS`` system.

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

**For Pronet network** ::

   $ lochness_create_template.py \
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
       --s3_selective_sync surveys mri phone eeg actigraphy \
       --enter_password


**For Prescient network** ::

    $ lochness_create_template.py \
        --outdir /data/prescient/data_sync_prescient \
        --studies PrescientLA PrescientSL PrescientLA \
        --sources rpms upenn mediaflux mindlamp \
        --email kevincho@bwh.harvard.edu \
        --poll_interval 86400 \
        --ssh_host 123.456.789 \
        --ssh_user kc244 \
        --lochness_sync_send \
        --s3 \
        --s3_selective_sync surveys mri phone eeg actigraphy \
        --enter_password


.. note ::
    
   You remove ``--enter_password`` if you want to manually add your credentials
   to the template keyring file.
   


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

   To see detailed options of `lochness_create_template.py` ::

        $ lochness_create_template.py -h


Step 1 completed.


2. Edit credentials to the template keyring file
------------------------------------------------

Connecting to various external `data sources <data_sources.html>`_
(REDCap, XNAT, Box, etc.) often requires a myriad of connection details 
e.g., URLs, usernames, passwords, API tokens, etc. Lochness will only read 
these pieces of information from an encrypted JSON file that we refer to as 
the *keyring*.

These information needs be added to the ``lochness.json`` template::

   $ cd /data/pronet/data_sync_pronet  # the template directory created above
   $ vim lochness.json


``lochness.json`` file looks like below. Add credentials to the fields markedp
with ``*****`` ::

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
    
Example of completed ``lochness.json`` ::

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


3. Encrypt ``lochness.json`` to make a keyring file
---------------------------------------------------

Once required credentials are added to the template ``lochness.json`` keyring
file, it must be encrypted using a passphrase. At the moment, Lochness only
supports encrypting and decrypting files (including the keyring) using the
`cryptease <https://github.com/harvard-nrg/cryptease>`_ library. This library
should be installed automatically when you install Lochness, but you can
install it separately on another machine as well.

Encrypt the temporary keyring file by running ::

    $ crypt.py --encrypt lochness.json -o .lochness.enc

Or you could run `2_sync_command.sh`, which contains the same command ::

    $ bash 1_encrypt_command.sh


.. attention::
   I'll leave it up to you to decide on which device you want to encrypt this
   file. I will only recommend discarding the decrypted version as soon as 
   possible.


.. _edit_config ::

4. Edit ``config.yml``
----------------------
`config.yml` file contains details of options to be used in Lochness. ::

    $ vim config.yml


REDCap or RPMS database column names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update names of the ``REDCap`` or ``RPMS`` columns that contain unique subject
ID and consent date of each stubject.

For RPMS ::

    RPMS_PATH: /mnt/prescient/RPMS_incoming
    RPMS_id_colname: subjectkey
    RPMS_consent_colname: Consent

.. note ::

   ``RPMS_PATH`` is the directory where ``RPMS`` exports database as multiple
   csv files.


For REDCap ::

    redcap_id_colname: chric_record_id
    redcap_consent_colname: chric_consent_date


Amazon Web Services S3 bucket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update AWS s3 bucket name to your s3 bucket name and root directory ::

    AWS_BUCKET_NAME: pronet-test
    AWS_BUCKET_ROOT: TEST_PHOENIX_ROOT_PRONET


Box
~~~

Planned data structure on Box account (the source itself) looks like below ::

    ProNET
    ├── PronetAB
    │   ├── PronetAB_Interviews
    │   │   ├── OPEN
    │   │   │   └── AB00001
    │   │   │       └── 2021-12-10 16.01.56 Kevin Cho's Zoom Meeting
    │   │   │           ├── video2515225130.mp4
    │   │   │           ├── video1515225130.mp4
    │   │   │           ├── audio2515225130.mp4
    │   │   │           ├── audio1515225130.mp4
    │   │   │           └── Audio Record
    │   │   │               └── Audio Record
    │   │   │                   ├── audioKevinCho42515225130.m4a
    │   │   │                   ├── audioKevinCho21515225130.m4a
    │   │   │                   ├── audioAnotherPerson11515225130.m4a
    │   │   │                   └── audioAnotherPerson32515225130.m4a
    │   │   ├── PSYCHS
    │   │   │   ├── AB00001
    │   │   │   └── ...
    │   │   └── transcripts
    │   │       ├── Approved
    │   │       │   ├── AB00001
    │   │       │   │   ├── PronetAB_AB00001_interviewAudioTranscript_open_day00001_session001.txt
    │   │       │   │   └── PronetAB_AB00001_interviewAudioTranscript_open_day00001_session002.txt
    │   │       │   └── ...
    │   │       └── For_review
    │   │           ├── AB00001
    │   │           │   ├── PronetAB_AB00001_interviewAudioTranscript_open_day00001_session001.txt
    │   │           │   └── PronetAB_AB00001_interviewAudioTranscript_open_day00001_session002.txt
    │   │           └── ...
    │   ├── PronetAB_EEG
    │   │       └── AB00001
    │   │           └── AB00001_eeg_20220101.zip
    │   └── PronetAB_Actigraphy
    │   │       └── AB00001
    │   │           └── ...
    └── ...


Then, configure box part as below ::

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



Now, your Lochness configuration is complete and ready to run!

