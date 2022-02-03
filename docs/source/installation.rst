Installation
============


Requirement
-----------

Install ``python3`` and ``pip`` using ``Miniconda``

.. note ::

   Below is an example for Ubuntu 20.04

    .. code-block:: shell

       apt-get update
       apt-get install wget locales git -y

       echo "export LC_ALL=C" >> ~/.bashrc
       echo 'export LANGUAGE="en_US.UTF-8"' >> ~/.bashrc

       cd ~/Downloads
       wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Linux-x86_64.sh
       bash Miniconda3-py38_4.10.3-Linux-x86_64.sh

       source ~/.bashrc


AMP-SCZ Lochness
----------------

Install ``AMP-SCZ Lochness`` and ``AMP-SCZ Yaxil`` using ``pip``.

.. code-block:: shell

    pip install ampscz-lochness


.. note ::
   For the most recent AMP-SCZ lochness verion for debugging,  it might be
   better off to pull most recent commits directly from github.

   .. code-block:: shell

      git clone https://github.com/AMP-SCZ/lochness
      cd lochness
      pip install -r requirements.txt

      echo "export PYTHONPATH=${PYTHONPATH}:lochness" >> ~/.bashrc  # add path
      echo "export PATH=${PATH}:lochness/scripts" >> ~/.bashrc  # add path
      source ~/.bashrc


After ``pip`` installation, the scripts below should be available from your
console.

.. code-block:: shell

    sync.py -h
    lochness_create_template.py -h
    crypt.py -h



Amazon Web Service (AWS) commandline tool
-----------------------------------------

AMP-SCZ can also push the downloaded data to Amazon Web Service (AWS) s3
bukcet. To use this functionality, AWS commandline tool needs be installed and 
configured. Install ``awscli`` using ``apt-get`` ::

   sudo apt-get install awscli

.. note ::
   If you do not have sudo privileges, you can also download awscli excutables
   `here <https://docs.aws.amazon.com/cli/v1/userguide/install-linux.html>`_.


Then configure ``AWS CLI`` with your AWS credentials for the s3 bucket.

.. code-block:: shell

   aws configure
   
   AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
   AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   Default region name [None]: us-east
   Default output format [None]: json


Your s3 bucket should be available from your shell environment.

.. code-block:: shell

    $ aws s3 ls YourBucketName



``mailx`` for sending out emails
------------------------------

Lochness can send out email updates. This requires ``mailx`` installed in the
data aggregation server. In the current version ``sync.py`` is configured to
use ``mailx`` as the default mechanism, but Google SMTP server can also be used
when ``sync.py`` is slightly tweaked.


.. note::

   To use Google SMTP server, change the two lines 
   ``send_out_daily_updates(Lochness)`` to
   ``send_out_daily_updates(Lochness, mailx=False)``


   In order to use Google SMTP in sending out the emails, you need to create
   a google account and set the ``Less secure app access`` under the "Account
   settings" to "ON". 


Installation complete!
