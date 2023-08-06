.. vim: set fileencoding=utf-8 :
.. Fri 19 Aug 2016 15:03:52 CEST


==============
 Installation
==============

The installation of this package is divided in 2-parts. Installation of the
package and its software dependencies and the installation of databases.


Package Installation
--------------------

To install this package, first follow our `installation`_ instructions. Then,
using the Python interpreter provided by the distribution, install this
package:


.. code-block:: sh

  $ conda install bob.bio.vein


You must also install drivers for all database interfaces you may want to use.
The next command line install some of the available drivers:

.. code-block:: sh

  $ conda install bob.db.utfvp bob.db.verafinger

For a list of currently maintained database drivers, you may check `this file <https://gitlab.idiap.ch/bob/bob.bio.vein/blob/master/test-requirements.txt>`_.


Setting up Databases
--------------------

In order to run vein recognition algorithms using this package, you'll need to
make sure to download the raw files corresponding to the databases you'd like
to process. The raw files are not distributed with Bob_ software as biometric
data is, to most countries, considered sensible data that cannot be obtained
without explicit licensing from a data controller. You must visit the websites
below, sign the license agreements and then download the data before trying out
to run the baselines.

.. note::

   If you're at the Idiap Research Institute in Switzlerand, the datasets in
   the baselines mentioned in this guide are already downloaded and
   pre-installed on our shared file system.


The current system readily supports the following freely available datasets:

* ``vera``: `Vera Fingervein`_
* ``utfvp``: `UTFVP`_
* ``fv3d``: `3D Fingervein`_

.. * ``put``: `PUT`_ Vein Dataset


After downloading the databases, annotate the base directories in which they
are installed. Then, follow the instructions in
:ref:`bob.bio.base.installation` to let this framework know where root
installation of such databases are located on your system.


Development
-----------

If you're developing this package, you may automatically clone all necessary
Bob_ repositories on your local package installation. This allows you to build
against an environment which contains all of our dependencies_, but no
previously installed Bob_ packages. To do so, use the buildout recipe in
``develop.cfg`` just after bootstraping:

.. code-block:: sh

  $ buildout -c develop.cfg


Database SQL support files
==========================

If you installed all packages from scratch like above, you'll need to download
the SQL support files of some of the database front-ends available in this
package. This operation can be easily done like this:

.. code-block:: sh

  $ bob_dbmanage.py all download --missing


.. include:: links.rst
