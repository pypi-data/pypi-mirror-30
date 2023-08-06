.. vim: set fileencoding=utf-8 :
.. @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
.. @date:   Mon Oct 19 11:10:18 CEST 2015

.. _bob.db.pericrosseye:

======================================================
Cross-Spectrum Iris/Periocular Recognition COMPETITION
======================================================

Collected by University of Reading, the Cross-Spectrum Iris/Periocular contains VIS and NIR periocular images from the
same subjects form the left and right eyes.

The dataset contains a total of 20 subjects and for each subject it has:
 - 8 VIS captures from the left eye
 - 8 NIR captures from the left eye
 - 8 VIS captures from the right eye
 - 8 NIR captures from the right eye

Here we are considering that each eye is an independent observation.
Hence, the database has 40 subjects.

The informations above were extracted from:

.. code-block:: latex

  @INPROCEEDINGS{7736915,
    author={A. Sequeira and L. Chen and P. Wild and J. Ferryman and F. Alonso-Fernandez and K. B. Raja and R. Raghavendra and C. Busch and J. Bigun},
    booktitle={2016 International Conference of the Biometrics Special Interest Group (BIOSIG)},
    title={Cross-Eyed - Cross-Spectral Iris #x002F;Periocular Recognition Database and Competition},
    year={2016},
    pages={1-5},
    keywords={iris recognition;cross-eyed cross-spectral iris recognition database;cross-eyed cross-spectral periocular recognition database;dual-spectrum database;indoor environment;iris image capture;periocular image capture;Benchmark testing;Databases;Iris;Iris recognition;Training},
    doi={10.1109/BIOSIG.2016.7736915},
    month={Sept},}



Documentation
-------------

.. toctree::
   :maxdepth: 2

   guide
   py_api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

