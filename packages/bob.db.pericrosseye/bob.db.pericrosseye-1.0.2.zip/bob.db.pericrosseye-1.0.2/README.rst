.. vim: set fileencoding=utf-8 :
.. Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
.. Thu Apr 16 16:39:01 CEST 2015



.. image:: http://img.shields.io/badge/docs-v1.0.2-yellow.png
   :target: https://www.idiap.ch/software/bob/docs/bob/bob.db.pericrosseye/v1.0.2/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/bob/bob.db.pericrosseye/master/index.html
.. image:: https://gitlab.idiap.ch/bob/bob.db.pericrosseye/badges/v1.0.2/build.svg
   :target: https://gitlab.idiap.ch/bob/bob.db.pericrosseye/commits/v1.0.2
.. image:: https://gitlab.idiap.ch/bob/bob.db.pericrosseye/badges/v1.0.2/coverage.svg
   :target: https://gitlab.idiap.ch/bob/bob.db.pericrosseye/commits/v1.0.2
.. image:: https://img.shields.io/badge/gitlab-project-0000c0.svg
   :target: https://gitlab.idiap.ch/bob/bob.db.pericrosseye
.. image:: http://img.shields.io/pypi/v/bob.db.pericrosseye.png
   :target: https://pypi.python.org/pypi/bob.db.pericrosseye
.. image:: https://img.shields.io/badge/original-data--files-a000a0.png
   :target: https://sites.google.com/site/crossspectrumcompetition/guidelines


=======================================================
Cross-Spectrum Iris/Periocular Recognition Database
=======================================================

This package contains the access API and descriptions for the `Cross-Spectrum Iris/Periocular Recognition COMPETITION <https://sites.google.com/site/crossspectrumcompetition/guidelines>`.
The actual raw data for the database should be downloaded from the original URL. 
This package only contains the Bob accessor methods to use the DB directly from python, with the original protocol of the database.

This database is for research on VIS-NIR periocular recognition.
It includes samples of 20 identities captured in both VIS and NIR.


Installation
------------

Complete Bob's `installation`_ instructions. Then, to install this package,
run::

  $ conda install bob.db.pericrosseye


Contact
-------

For questions or reporting issues to this software package, contact our
development `mailing list`_.


.. Place your references here:
.. _bob: https://www.idiap.ch/software/bob
.. _installation: https://gitlab.idiap.ch/bob/bob/wikis/Installation
.. _mailing list: https://groups.google.com/forum/?fromgroups#!forum/bob-devel