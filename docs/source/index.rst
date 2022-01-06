.. Lochness documentation master file, created by
   sphinx-quickstart on Thu Sep  5 17:46:33 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to AMP-SCZ Lochness's documentation!
====================================

.. image:: images/amp_scz_logo.png
   :width: 150


Introduction
------------

Lochness is a data management tool designed to periodically pull and download
data from various data archives into a local directory. This is often referred
to as building a "data lake" (hence the name). This repository is a fork from
`harvard-nrg lochness <https://github.com/harvard-nrg/lochness>`_, updated and
maintained by DPACC for U24 project.


AMP-SCZ Lochness has a number of extra functions, many of which are specific
to PRONET and PRESCIENT research networks within the U24 study. However, extra
data sources such as `Box <https://box.com/>`_, `Mediaflux
<https://www.arcitecta.com/mediaflux/features/>`_,
`RPMS <https://data.orygen.org.au/>`_, and
`Mindlamp <https://www.digitalpsych.org/lamp.html>`_ could be useful for other
studies as well.


The main difference of the AMP-SCZ Lochness, from the original harvard-nrg 
Lochness, is that AMP-SCZ requies database of unique subject IDs in one of
``REDCap`` or ``RPMS`` to make a list of subject IDs to be used with Lochness
(``metadata.csv``), which will be used in searching for any data to download. 
So, as long as your projects also have ``REDCap`` or ``RPMS`` linked, AMP-SCZ
Lochness could also be used for your project!



Therefore, required and supported data sources are

    - Required
        - REDCap or
        - RPMS

    - Supported
        - XNAT
        - Box
        - Mediaflux
        - Mindlamp

.. note ::

   Currently, REDCap or RPMS data sources are the requirements for using
   lochness, but future update will allow AMP-SCZ Lochness to pull data without
   them, by manually creating ``metadata.csv`` files.


Please report any bug or issue to our 
`github repository <https://github.com/AMP-SCZ/lochness/issues>`_. Thanks!

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   setting_up_lochness
   running_lochness
   phoenix_bids_example
   sync_in_detail
   data_sources
   ..phoenix
   configuration_file


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
