Quick start
===========
Lochness provides a single command line tool (daemon) to periodically poll
and download data from various web services into a local directory. Out of
the box there is support for pulling data from a multitude of 
`data sources <data_sources.html>`_ including REDCap, XNAT, Dropbox, Box,
Mediaflux, RPMS, external hard drives, and more.



Installation
------------
Just use ``pip`` ::

    $ pip install ampscz-lochness

For the most recent AMP-SCZ lochness install and debugging, see `Installation
<../../README.md#installation>`_.


Also, Amazon Web Service (AWS) commandline tool needs be configured ::

    $ sudo apt-get install awscli


and configure ``AWS CLI`` with Pronet or Prescient credentials. ::

    $ aws configure
    
    AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
    AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    Default region name [None]: us-east
    Default output format [None]: json




Setup from a template
---------------------
Follow the steps below to semi-automatically setup lochness environment.

1. Run ``lochness_create_template.py`` to create a template ::

For Pronet network ::

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
        --s3_selective_sync surveys mri phone eeg actigraphy


For Prescient network ::

    $ lochness_create_template.py \
        --outdir /data/prescient/data/sync_prescient \
        --studies PrescientLA PrescientSL PrescientLA \
        --sources rpms upenn mediaflux mindlamp \
        --email kevincho@bwh.harvard.edu \
        --poll_interval 86400 \
        --ssh_host 123.456.789 \
        --ssh_user kc244 \
        --lochness_sync_send \
        --s3 \
        --s3_selective_sync surveys mri phone eeg actigraphy



Running ``lochness_create_template.py`` will create a This will create a
directory which will look like this ::

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


2. Edit credentials in ``lochness.json`` ::

   cd /data/pronet/data_sync_pronet
   vim lochness.json


``lochness.json`` file looks like below. Add information to field labelled with
``*****`` ::

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
          "PronetSL": {
            "redcap.Pronet": [
              "Pronet"
            ],
            "redcap.UPENN": [
              "UPENN"
            ]
          }
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
          "PronetSL": {
            "redcap.Pronet": [
              "Pronet"
            ],
            "redcap.UPENN": [
              "UPENN"
            ]
          }
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



3. Encrypt ``lochness.json`` by running ::

    $ bash 2_sync_command.sh

Then remove ``lochness.json`` for security ::

    $ rm lochness.json



4. Edit ``config.yml``::

    $ vim config.yml


Edit AWS s3 bucket name and root directory ::

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



Run ``sync.py``
---------------

Execute ``sync.py`` script to have lochness to continuously sync data ::

    sync.py -c /data/pronet/data_sync_pronet/config.yml \
        --studies PronetLA PronetOR PronetBI PronetNL PronetNC PronetSD \
                  PronetCA PronetYA PronetSF PronetPA PronetSI PronetPI \
                  PronetNN PronetIR PronetTE PronetGA PronetWU PronetHA \
                  PronetMT PronetKC PronetPV PronetMA PronetCM PronetMU \
                  PronetSH PronetSL \
        --source redcap upenn box xnat mindlamp \
        --lochness_sync_send --s3 \
        --debug --continuous


This will run lochness sync function for each site (``studies``) for all
measures (``source``). It will upload newly downloaded data to the s3 bucket
after each data sweep for all sources. Then, this ``sync.py`` function will
execute these functions again after ``poll_interval`` stated in the
``config.yml``.


``lochness_create_template.py`` creates a template bash script that could be
used. ::

    bash 2_sync_command.sh




Example PHOENIX-BIDS structure
------------------------------

U24 uses ``PHOENIX-BIDS`` structure, which is slightly different from the
``PHOENIX`` structure. ``PHOENIX-BIDS`` was used to have more similarity to the
``BIDS`` structure, while maintaining ``protected`` vs ``general`` and ``raw``
vs ``processed`` concept of the ``PHOENIX``.


**Summary of the structure**

``<protected>/<study>/<processed>/<subject>/<datatypes>`` ::

    PHOENIX/
    ├── PROTECTED
    │   └── PronetAB
    │       ├── raw
    │       │   ├── AB00001
    │       │   │   ├── surveys
    │       │   │   │   └── AB00001.Pronet.json
    │       │   │   └── ...
    │       │   └── ...
    │       └── processed
    │           └── ...
    └── GENERAL
        └── ...


**Different levels of the structure**

Level 1: ``General`` or ``Protected``::
    
    PHOENIX/
    ├── GENERAL
    └── PROTECTED


Level 2: Sites (studies) ::

    PHOENIX/
    ├── GENERAL
    │   ├── PronetAB
    │   ├── ...
    │   └── PronetYA
    └── PROTECTED
        ├── PronetAB
        ├── ...
        └── PronetYA


Level 3: Raw or Processed ::

    PHOENIX/
    ├── GENERAL
    │   ├── PronetAB
    │   │   ├── PronetAB_metadata.csv
    │   │   ├── raw
    │   │   └── processed
    │   ├── ...
    │   └── PronetYA
    │       ├── PronetYA_metadata.csv
    │       ├── raw
    │       └── processed
    └── PROTECTED
        ├── PronetAB
        │   ├── raw
        │   └── processed
        ├── ...
        └── PronetYA
            ├── raw
            └── processed


Level 4: Subject ::

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


Level 5: Data types ::

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


See `Setup from a template
<../..//README.md#Setup-from-a-template>`_.


Manual Setup
------------
Connecting to various external `data sources <data_sources.html>`_
(Beiwe, XNAT, Dropbox, etc.) often requires a myriad of connection details 
e.g., URLs, usernames, passwords, API tokens, etc. Lochness will only read 
these pieces of information from an encrypted JSON file that we refer to as 
the *keyring*. Here's an example of a decrypted keyring file ::

    {
      "lochness": {
        "REDCAP": {
          "example": {
            "redcap.example": [
              "example"
            ]
          }
        },
        "SECRETS": {
          "example": "quick brown fox jumped over lazy dog"
        }
      },

      "redcap.example": {
        "URL": "https://redcap.partners.org/redcap",
        "API_TOKEN": {
          "example": "681BBE7CCA0C879EE5**********"
        }
      },

      "beiwe.example": {
        "URL": "https://beiwe.example.org",
        "ACCESS_KEY": "...",
        "SECRET_KEY": "..."
      },

      "xnat.example": {
        "URL": "https://chpe-xnat.example.harvard.edu",
        "USERNAME": "...",
        "PASSWORD": "..."
      },

      "box.example": {
        "CLIENT_ID": "...",
        "CLIENT_SECRET": "...",
        "API_TOKEN": "..."
      },

      "mediaflux.example": {
        "HOST": "mediaflux.researchsoftware.unimelb.edu.au",
        "PORT": "443",
        "TRANSPORT": "https",
        "TOKEN": "...",
        "DOMAIN": "...",
        "USER": "...",
        "PASSWORD": "..."
      },

      "mindlamp.example": {
        "URL": "...",
        "ACCESS_KEY": "...",
        "SECRET_KEY": "..."
      },

      "daris.example": {
        "URL": "...",
        "TOKEN": "...",
        "PROJECT_CID": "..."
      },

      "rpms.example": {
        "RPMS_PATH": "..."
      }
    }


This file must be encrypted using a passphrase. At the moment, Lochness only
supports encrypting and decrypting files (including the keyring) using the
`cryptease <https://github.com/harvard-nrg/cryptease>`_ library. This library
should be installed automatically when you install Lochness, but you can
install it separately on another machine as well. Here is how you would use
``cryptease`` to encrypt the keyring file ::

    crypt.py --encrypt ~/.lochness.json --output-file ~/.lochness.enc

.. attention::
   I'll leave it up to you to decide on which device you want to encrypt this
   file. I will only recommend discarding the decrypted version as soon as 
   possible.



PHOENIX
~~~~~~~
Lochness will download your data into a directory structure informally known as
PHOENIX. For a detailed overview of PHOENIX, please read through the 
`PHOENIX documentation <phoenix.html>`_. You need to initialize the directory structure 
manually, or by using the provided ``phoenix-generator.py`` command line tool that will 
be installed with Lochness. To use the command line tool, simply provide a study name 
using the ``-s|--study`` argument and a base filesystem location ::

    phoenix-generator.py --study example ./PHOENIX

The above command will generate the following directory tree ::

    PHOENIX/
    ├── GENERAL
    │   └── example
    │       └── example_metadata.csv
    └── PROTECTED
        └── example


Basic usage
-----------
The primary command line utility for Lochness is ``sync.py``. When you invoke this 
tool, you will be prompted for the passphrase that you used to encrypt your 
`keyring <#setup>`_. To sidestep the password prompt, you can use an environment 
variable ``NRG_KEYRING_PASS``.


metadata files
~~~~~~~~~~~~~~
The ``sync.py`` tool is driven largely off the PHOENIX metadata files. For an 
in-depth look at these metadata files, please read the 
`metadata files section <phoenix.html#metadata-files>`_ from the PHOENIX documentation.


configuration file
~~~~~~~~~~~~~~~~~~
Before you can successfully run ``sync.py``, you need to provide the location 
to a configuration file using ``-c|--config`` ::

    sync.py -c /path/to/config.yaml

There is an example configuration file within the Lochness repository under 
``etc/config.yaml``. To learn more about what each configuration option 
means, please read the `configuration file documentation <configuration_file.html>`_.


data sources
~~~~~~~~~~~~
By default, Lochness will download data from *all* supported data sources. If 
you want to restrict Lochness to only download specific data sources, you can 
provide the ``--source`` argument ::

    sync.py -c config.yml --source beiwe
    sync.py -c config.yml --source xnat box


additional help
~~~~~~~~~~~~~~~
To see all of the command line arguments available, use the ``--help`` argument ::

    sync.py --help

