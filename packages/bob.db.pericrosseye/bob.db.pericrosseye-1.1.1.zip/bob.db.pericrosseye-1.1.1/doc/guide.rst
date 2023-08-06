.. vim: set fileencoding=utf-8 :
.. @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
.. @date:   Mon Oct 19 11:10:18 CEST 2015

==============
 User's Guide
==============

This package contains the access API and descriptions for the Cross-Spectrum Iris/Periocular Recognition Database
`PeriCrosseye_`

It only contains the Bob_ accessor methods to use the DB directly from python, with our certified protocols.
The actual raw data for the database should be downloaded from the original URL.

The Database Interface
----------------------

The :py:class:`bob.db.pericrosseye.Database` complies with the standard biometric verification database as described in `bob.db.base <bob.db.base>`_, implementing the interface :py:class:`bob.db.base.SQLiteDatabase`.

Protocols
---------

In total we provide 5 evaluation protocols called: ``cross-eye-VIS-NIR-split1``, ``cross-eye-VIS-NIR-split2``,
``cross-eye-VIS-NIR-split3``, ``cross-eye-VIS-NIR-split4`` and ``cross-eye-VIS-NIR-split5``.
Each protocol split the 40 subjects in 3 subsets called ```world```, ```dev``` and ```eval```.


The ```world``` set is composed by 20 clients and it is designed to be used as the training set.

The ```dev``` set is composed by 10 clients and it is designed to tune the hyper-parameters of a hererogeneous face recognition approach and to be the decision threshold reference.

The ```eval``` set is composed by 10 clients and it is used to assess the final unbiased system performance.

To fetch the object files using this protocol use the following piece of code:

.. code-block:: python

   >>> import bob.db.pericrosseye
   >>> db = bob.db.pericrosseye.Database()   
   >>> #Training set
   >>> train      = db.objects(protocol='cross-eye-VIS-NIR-split1', groups='world')
   >>>
   >>> #Development set
   >>> dev_enroll = db.objects(protocol='cross-eye-VIS-NIR-split1', groups='dev', purposes="enroll")
   >>> dev_probe = db.objects(protocol='cross-eye-VIS-NIR-split1', groups='dev', purposes="probe")
   >>> 
   >>> #Evaluation set
   >>> eval_enroll = db.objects(protocol='cross-eye-VIS-NIR-split1', groups='eval', purposes="enroll")
   >>> eval_probe = db.objects(protocol='cross-eye-VIS-NIR-split1', groups='eval', purposes="probe")
   >>>              


.. `_PeriCrosseye`: https://sites.google.com/site/crossspectrumcompetition/guidelines
.. _bob: https://www.idiap.ch/software/bob
