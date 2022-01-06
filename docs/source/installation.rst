Installation
============


AMP-SCZ Lochness
----------------

Install ``AMP-SCZ Lochness`` using ``pip`` ::

    $ pip install ampscz-lochness

.. note ::
   For the most recent AMP-SCZ lochness verion for debugging,  it might be
   better off to pull most recent commits directly from github ::

      $ git clone https://github.com/AMP-SCZ/lochness
      $ echo "export PATH=${PATH}:lochness/scripts" >> ~/.bashrc
      $ source ~/.bashrc


The scripts below should be available from your shell environment ::

    $ sync.py -h
    $ lochness_create_template.py -h
    $ crypt.py -h


Amazon Web Service (AWS) commandline tool
-----------------------------------------

AMP-SCZ can also push the downloaded data to Amazon Web Service (AWS) s3
bukcet. To use this functionality, AWS commandline tool needs be installed and 
configured. Install ``awscli`` using ``apt-get`` ::

   $ sudo apt-get install awscli

.. note ::
   If you do not have sudo privileges, you can also download awscli excutables
   `here <https://docs.aws.amazon.com/cli/v1/userguide/install-linux.html>`_.


Then configure ``AWS CLI`` with your AWS credentials for the s3 bucket. ::

   $ aws configure
   
   AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
   AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   Default region name [None]: us-east
   Default output format [None]: json


Your s3 bucket should be available from your shell environment ::

    $ aws s3 ls YourBucketName



Installation complete!
