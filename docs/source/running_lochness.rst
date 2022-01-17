Running lochness
================

Run ``sync.py``
---------------

Execute ``sync.py`` script to have lochness sync data

**For Pronet network**

.. code-block:: shell

    sync.py \
        --config /data/pronet/data_sync_pronet/config.yml \
        --studies PronetLA PronetOR PronetBI PronetNL PronetNC PronetSD \
                  PronetCA PronetYA PronetSF PronetPA PronetSI PronetPI \
                  PronetNN PronetIR PronetTE PronetGA PronetWU PronetHA \
                  PronetMT PronetKC PronetPV PronetMA PronetCM PronetMU \
                  PronetSH PronetSL \
        --source redcap upenn box xnat mindlamp \
        --lochness_sync_send --s3 \
        --log-file /data/pronet/data_sync_pronet/log.txt \
        --daily_summary \
        --debug --continuous 


**For Prescient network**

.. code-block:: shell

    sync.py \
        --config /data/prescient/data_sync_prescient/config.yml \
        --studies PronetLA PronetOR PronetBI PronetNL PronetNC PronetSD \
                  PronetCA PronetYA PronetSF PronetPA PronetSI PronetPI \
                  PronetNN PronetIR PronetTE PronetGA PronetWU PronetHA \
                  PronetMT PronetKC PronetPV PronetMA PronetCM PronetMU \
                  PronetSH PronetSL \
        --source rpms upenn mediaflux mindlamp \
        --lochness_sync_send --s3 \
        --log-file /data/prescient/data_sync_prescient/log.txt \
        --daily_summary \
        --debug --continuous


When you execute this command, you will be prompted for the passphrase that
you used to encrypt your `keyring <#setup>`_. 

This will run lochness sync function for each site (``studies``) for all
measures (``source``) given to ``--source`` argument. The downloaded data will
be saved under the PHOENIX directory defined in the ``config.yml`` file.
``--lochness_sync_send`` with ``--s3`` argument, will make lochness upload
the newly downloaded data to the s3 bucket after each data sweep for all
sources and sites. Then, this ``sync.py`` function will execute these functions
again after the ``poll_interval`` stated in the ``config.yml``.


.. note ::

    ``lochness_create_template.py`` creates a template bash script that could be
    used.

    .. code-block:: shell

        bash 2_sync_command.sh


Good luck!
