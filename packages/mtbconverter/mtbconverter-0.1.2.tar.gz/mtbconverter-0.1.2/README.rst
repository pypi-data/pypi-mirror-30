mtbconverter
==============

|language| |travis| |codecov| |ghtag| |pypi| |license| 

A Python command line tool that parses and converts diagnostic variant data for the Molecular Tumor Board at UKT Tübingen.

.. |language| image:: https://img.shields.io/github/languages/top/qbicsoftware/qbic.mtbconverter.svg

.. |travis| image:: https://travis-ci.org/qbicsoftware/qbic.mtbconverter.svg?branch=master
    :target: https://travis-ci.org/qbicsoftware/qbic.mtbconverter
.. |codecov| image:: https://codecov.io/gh/qbicsoftware/qbic.mtbconverter/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/qbicsoftware/qbic.mtbconverter
.. |ghtag| image:: https://img.shields.io/github/release/qbicsoftware/qbic.mtbconverter/all.svg
    :target: https://github.com/qbicsoftware/qbic.mtbconverter/releases
.. |pypi| image:: https://img.shields.io/pypi/v/mtbconverter.svg
    :target: https://pypi.python.org/pypi/mtbconverter
.. |license| image:: https://img.shields.io/github/license/qbicsoftware/qbic.mtbconverter.svg


.. contents:: Table of Contents
   :depth: 2


Commands
---------

If you provide the ``-h`` argument, you get the command overview:

.. code-block:: bash
  
  Mtbconverter version 0.1
  Usage: mtbconverter.py [-h] [command]

  command:
          convert         Converts variant information into CentraXX XML.
          push            Pushes one ore more XML files to CentraXX.
          catalogue       Builds CentraXX catalogue XML files.

The mtbconverter currently supports three commands: ``convert, push`` and ``catalogue``.

convert
~~~~~~~
The ``convert`` command tells the mtbconverter to parse the necessary MTB information from a given zip archive. The archive needs to contain several TSV files. which follow the format specification_ and naming convention described in the ``mtbparser`` module, which is implemented in mtbconverter.

.. _specification: https://github.com/qbicsoftware/qbic.mtbparser/blob/master/README.md

.. code-block:: bash

  Mtbconverter version 0.1.
  usage: convert [-h] archive patientID

  Conversion of variant information into CentraXX schema conform XML.

  positional arguments:
    archive     ZIP archive containing the variant information files.
    patientID   A QBiC patient ID.

  optional arguments:
    -h, --help  show this help message and exit
    
The output is an XML according to the CetraXX DataExchange specification, that reflects the information parsed from the MTB ZIP archive and can be imported into CentraXX, for example with the ``mtbconverter push`` command.

**Archive format specification**
The ZIP archive name needs to carry the QBIC barcode, and the same needs to present in all files within the archive. This is just to make sure, that the files indeed belong to the same sample.

.. code-block:: bash
  
  Archive name:
  <QBIC-barcode>_*.zip
  
  Archive content:
  <QBiC-Barcode>_somatic_snv.tsv
  <QBiC-Barcode>_somatic_cnv.tsv
  <QBiC-Barcode>_germline_snv.tsv
  <QBiC-Barcode>_germline_cnv.tsv
  <QBiC-Barcode>_somatic_sv.tsv
  <QBiC-Barcode>_metadata.tsv

The information is encoded in the six TSV files, following the specification described in detail in the ``mtbparser`` library_.

push
~~~~
The ``push`` command enables the import of a CentraXX patient XML into the CentraXX system via CentraXX's REST API. With the ``-h`` flag, you get an overview of the arguments:

.. code-block:: bash

    Mtbconverter version 0.1.
    usage: push [-h] [-c config] [-t] [--check] patientdata

    Import a converted XML file into CentraXX.

    positional arguments:
      patientdata  Converted XML file from an MTB ZIP archive with the variant
                   information.

    optional arguments:
      -h, --help   show this help message and exit
      -c config    Configuration file with settings for the remote CentraXX
                   system. (Default: /etc/centraxx.config)
      -t, --test   Import to the CentraXX test system.
      --check      Check the connection to CentraXX.
      
``mtbconverter`` tries to parse a configuration file by default in ``/etc/centraxx.config``, but you can also specify another path via the ``-c`` option.

**CentraXX configuration file**
The configuration file contains information about CentraXX's server location and authentication data. An example config file shall look similar to this:

.. code-block:: bash

    [CENTRAXX_TEST]
    authuser=myuser
    password=mypassword
    serveraddr=127.0.0.1:443
    protocol=https
    infopath=%(protocol)s://%(serveraddr)s/centraxx/rest/info

    [CENTRAXX]
    authuser=myuser
    password=mypassword
    serveraddr=xxx.x.xxx.xxx:xxxx
    protocol=https
    infopath=%(protocol)s://%(serveraddr)s/centraxx/rest/info

The ``[...]`` parts are the sections of the configuration. ``mtbconverter`` currently supports "CENTRAXX" and "CENTRAXX_TEST".  If you specify the "CENTRAXX_TEST" section, then you can perform operations to a target test system using the ``-t`` option flag.

If you supply the ``infopath`` keyword with a valid path, you can check the connection to CentraXX easily by providing the ``--check`` option flag. Either you will get an timeout response, if the target server is not accessible, or you will see the return code with message.

catalogue
~~~~~~~~~
The ``catalogue`` command creates XML files for CentraXX controlled vocabulary, parameters definition and profiles. This needs to be done only once every time a specification changes, so CentraXX knows how to connect the incoming data, once it gets imported.

After executing ``catalogue``, mtbconverter will create 8 XML files:

1. cv_centraxx.xml: The controlled vobaculary for CentraXX.
2. params_centraxx.xml: The parameters and the expected data type for CentraXX.
3. ssnv_profiles_centraxx.xml: The profile for somatic SNVs.
4. scnv_profiles_centraxx.xml: The profile for somatic CNVs.
5. gsnv_profiles_centraxx.xml: The profile for germline SNVs.
6. gcnv_profiles_centraxx.xml: The profile for germline CNVs.
7. sv_profiles_centraxx.xml: The profile for somatic structural variants.
8. metadata_profiles_centraxx.xml: The profile for metadata, containing the diagnosis.


Changelog
---------
Find all the version changes of ``mtbconverter`` here

2018-02-07: v0.1.1
~~~~~~~~~
Small bug fixes, add entry point, so mtbconverter can be used as command line tool

2018-02-06: v0.1
~~~~~~~~~
First official release, not yet supporting all of the desired push options to CentraXX, but coming soon!

Author
------
This code is provided by Sven Fillinger, QBiC, University of Tübingen.


.. _library: https://github.com/qbicsoftware/qbic.mtbparser/blob/master/README.md
  
