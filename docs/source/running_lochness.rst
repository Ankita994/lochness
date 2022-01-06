Running lochness
================

Run ``sync.py``
---------------

Execute ``sync.py`` script to have lochness sync data

**For Pronet network** ::

    sync.py \
        --config /data/pronet/data_sync_pronet/config.yml \
        --studies PronetLA PronetOR PronetBI PronetNL PronetNC PronetSD \
                  PronetCA PronetYA PronetSF PronetPA PronetSI PronetPI \
                  PronetNN PronetIR PronetTE PronetGA PronetWU PronetHA \
                  PronetMT PronetKC PronetPV PronetMA PronetCM PronetMU \
                  PronetSH PronetSL \
        --source redcap upenn box xnat mindlamp \
        --lochness_sync_send --s3 \
        --debug --continuous


**For Prescient network** ::

    sync.py \
        --config /data/prescient/data_sync_prescient/config.yml \
        --studies PronetLA PronetOR PronetBI PronetNL PronetNC PronetSD \
                  PronetCA PronetYA PronetSF PronetPA PronetSI PronetPI \
                  PronetNN PronetIR PronetTE PronetGA PronetWU PronetHA \
                  PronetMT PronetKC PronetPV PronetMA PronetCM PronetMU \
                  PronetSH PronetSL \
        --source rpms upenn mediaflux mindlamp \
        --lochness_sync_send --s3 \
        --debug --continuous


When you invoke this command, you will be prompted for the passphrase that
you used to encrypt your `keyring <#setup>`_. To sidestep the password prompt,
you can use an environment variable ``NRG_KEYRING_PASS``.

This will run lochness sync function for each site (``studies``) for all
measures (``source``). It will upload newly downloaded data to the s3 bucket
after each data sweep for all sources. Then, this ``sync.py`` function will
execute these functions again after ``poll_interval`` stated in the
``config.yml``.


``lochness_create_template.py`` creates a template bash script that could be
used. ::

    bash 2_sync_command.sh


The downloaded data will be saved under the PHOENIX directory defined in the
``config.yml`` file.

Good luck!
