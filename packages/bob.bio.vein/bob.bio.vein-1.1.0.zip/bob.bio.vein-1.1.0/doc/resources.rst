.. vim: set fileencoding=utf-8 :
.. Mon 11 Jul 2016 16:39:15 CEST


.. _bob.bio.vein.resources:

===========
 Resources
===========

This section contains a listing of all ready-to-use resources you can find in
this package. Each module may contain references different resource types,
including ``database``, ``preprocessor``, ``extractor`` and ``algorithm``. By
combining *complementary* resources, you can run baseline experiments as
explained on :ref:`bob.bio.vein.baselines`.


.. _bob.bio.vein.resources.databases:

Databases
---------

These resources represent configuration files containing at least settings for
the following runtime attributes of ``verify.py``:

  * ``database``
  * ``protocol``


.. _bob.bio.vein.resources.database.verafinger:

Verafinger Database
===================

.. automodule:: bob.bio.vein.configurations.verafinger
   :members:


.. _bob.bio.vein.resources.database.utfvp:

UTFVP Database
==============

.. automodule:: bob.bio.vein.configurations.utfvp
   :members:

.. _bob.bio.vein.resources.database.fv3d:

3D Fingervein Database
======================

.. automodule:: bob.bio.vein.configurations.fv3d
   :members:


.. _bob.bio.vein.resources.database.putvein:

PUT Vein Databas
======================

.. automodule:: bob.bio.vein.configurations.putvein
   :members:


.. _bob.bio.vein.resources.recognition:

Recognition Systems
-------------------

These resources represent configuration files containing at least settings for
the following runtime attributes of ``verify.py``:

  * ``sub_directory``
  * ``preprocessor``
  * ``extractor``
  * ``algorithm``


.. _bob.bio.vein.resources.recognition.rlt:

Repeated Line Tracking and Miura Matching
=========================================

.. automodule:: bob.bio.vein.configurations.repeated_line_tracking
   :members:


.. _bob.bio.vein.resources.recognition.mc:

Maximum Curvature and Miura Matching
====================================

.. automodule:: bob.bio.vein.configurations.maximum_curvature
   :members:


.. _bob.bio.vein.resources.recognition.wld:

Wide-Line Detector and Miura Matching
=====================================

.. automodule:: bob.bio.vein.configurations.wide_line_detector
   :members:


Other Resources
---------------

Other resources which include configuration parameters for circumstantial
usage.

.. _bob.bio.vein.resources.parallel:


Parallel Running
================

.. automodule:: bob.bio.vein.configurations.parallel
   :members:


Using SGE at Idiap
==================

.. automodule:: bob.bio.vein.configurations.gridio4g48
   :members:

