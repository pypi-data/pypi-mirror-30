===========================
NWB Documentation Utilities
===========================

*This project is under active development. Its content, API and behavior may change at any time. We mean it.*

Overview
--------

This project is a collection of CLIs, scripts and modules useful to generate the NWB documentation.


Installation
------------

::

  pip install nwb-docutils



Available Tools
---------------

* ``nwb_generate_format_docs``: Generate figures and RST documents from the NWB YAML specification for the
  format specification documentation.

* ``nwb_init_sphinx_extension_doc``: Create format specification SPHINX documentation for an NWB extension.

* ``nwb_gallery_prototype``


Available Modules
-----------------

* ``nwb_docutils/render.py``: This module is used to generate figures of the hierarchies of NWB-N files and
  specifications as well as to help with the programmatic generation of reStructuredText (RST) documents.


History
-------

nwb-utils was initially a sub-directory of the nwb-schema project. Corresponding history was extracted during
the `4th NWB Hackathon <https://neurodatawithoutborders.github.io/nwb_hackathons/HCK04_2018_Seattle/>`_ into a
dedicated *pip-installable* project to facilitate its use by both core NWB documentation projects and various
NWB extensions.
