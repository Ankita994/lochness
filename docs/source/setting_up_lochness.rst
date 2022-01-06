Setting up Lochness
===================

Follow the steps below to semi-automatically setup the lochness environment.

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



4. Edit ``config.yml``
----------------------
`config.yml` file contains details of options to be used in Lochness. ::

    $ vim config.yml


Update AWS s3 bucket name to your s3 bucket name and root directory ::

    AWS_BUCKET_NAME: pronet-test
    AWS_BUCKET_ROOT: TEST_PHOENIX_ROOT_PRONET


Edit ``base`` field for Box structure ::

    box:
        PronetLA:
            base: ProNET/PronetLA
            delete_on_success: False
            file_patterns:
                actigraphy:
                       - vendor: Activinsights
                         product: GENEActiv
                         data_dir: PronetLA_Actigraphy
                         pattern: '*.*'
                eeg:
                       - product: eeg
                         data_dir: PronetLA_EEG
                         pattern: '*.*'
                interviews:
                       - product: open
                         data_dir: PronetLA_Interviews/OPEN
                         out_dir: open
                         pattern: '*.*'
                       - product: psychs
                         data_dir: PronetLA_Interviews/PSYCHS
                         out_dir: psychs
                         pattern: '*.*'
                       - product: transcripts
                         data_dir: PronetLA_Interviews/transcripts/Approved
                         out_dir: transcripts
                         pattern: '*.*'


Now, configuration step is complete!

