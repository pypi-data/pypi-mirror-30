.. vim: set fileencoding=utf-8 :
.. Tue 13 Mar 10:11:57 2018 CET

.. _bob.db.verafinger.guide:

============
 User Guide
============

This section contains information for installing and using basic functionality
of this package to view database information and check its consistency.

Before proceeding, make sure you install the `VERA Fingervein Database`_ and
annotate its final destination on your hard drive. For the purposes of this
guide, we assume you have downloaded and uncompressed the dataset into a
(ficticious) folder called ``/path/to/verafinger``. Replace that string from
the command examples below to the actual location of files in your hard drive.

Once you uncompressed the files in the `VERA Fingervein Database`_, you should
be able to see at least 6 entries among directories and files:

.. code-block:: sh

   $ ls -l /path/to/verafinger
   total 4
   drwxr-xr-x 5 user staff   170 Mar 10 13:56 cropped/
   drwxr-xr-x 4 user staff   136 Mar 10 13:57 full/
   -rw-r--r-- 1 user staff  1004 Mar 10 14:03 metadata.csv
   drwxr-xr-x 6 user staff   204 Mar 10 14:32 annotations/
   drwxr-xr-x 3 user staff   102 Mar 12 17:29 protocols/
   -rw-r--r-- 1 andre staff 3461 Apr  9 14:41 README.rst


Checking Installation
---------------------

You can quickly check your installation of the database by using the following
command line:

.. code-block:: sh

   $ bob_dbmanage.py verafinger checkfiles --directory=/path/to/verafinger --annotations


If everything is OK, the command should return a status of 0 (zero) and print
no output. Any missing files from the dataset will be printed on the output. In
this case, check your installation once more.


Dumping File Lists
------------------

It may be useful to dump file lists that can be used by another framework to
process the raw files in this dataset. You can do this with the following
command:

.. code-block:: sh

   $ bob_dbmanage.py verafinger dumplist --directory=/path/to/verafinger --protocol=Full --group=dev --purpose=enroll --model=001_L_1 --extension='.png'
   /path/to/verafinger/full/bf/001-M/001_L_1.png

The command above lists files used to enroll the model ``001_L_1``. Other
options exist if you use the flag ``--help`` on the command line.


Metadata Population
-------------------

If you built this package from scratch, and did not use our recommended
`installation instructions`_, you will need to re-create the internal package
metadata, which is not shipped with the source code. To do so, execute the
following command:

.. code-block:: sh

   $ bob_dbmanage.py verafinger create --directory=/path/to/verafinger


Optionally pass one more ``-v`` flags to increase verbosity. Use the flag
``--recreate`` to overwrite any existing metadata files.


Metadata Downloading
--------------------

You may want to download a version of the metadata files provided by our
servers. In this case, you can skip the creation step above and just do:

.. code-block:: sh

   $ bob_dbmanage.py verafinger download


Use the flag ``--force`` to overwrite any existing files. Use the flag
``--missing`` to just download and uncompress metadata files missing from the
current installation.


.. todolist::

.. include:: links.rst
