.. vim: set fileencoding=utf-8 :
.. Tue Jan 13 19:42:18 CEST 2015

.. _bob.db.verafinger:

==========================
 VERA Fingervein Database
==========================

This package contains iterators for accessing samples of the `VERA Fingervein
Database`_ in a programmatic way. This package does **not** contain data
samples themselves - you must procure those yourself through the links above.

The `VERA Fingervein Database`_ for finger vein biometric recognition consists
of 440 images from 110 clients.  The dataset also contains presentation (a.k.a.
*spoofing*) attacks to the same 440 images that can be used to study
vulnerability of biometric systems or presentation attack detection schemes.
This database was produced at the `Idiap Research Institute
<http://www.idiap.ch>`_, in Switzerland.

If you use this database in your publication, please cite the following papers
on your references. This database introduced the VERA fingervein dataset for
biometric recognition:

.. code-block:: bibtex

   @inproceedings{Vanoni_BIOMS_2014,
     author = {Vanoni, Matthias and Tome, Pedro and El Shafey, Laurent and Marcel, S{\'{e}}bastien},
     month = oct,
     title = {Cross-Database Evaluation With an Open Finger Vein Sensor},
     booktitle = {IEEE Workshop on Biometric Measurements and Systems for Security and Medical Applications (BioMS)},
     year = {2014},
     location = {Rome, Italy},
     url = {http://publications.idiap.ch/index.php/publications/show/2928}
   }

This paper introduced fingervein vulnerability, providing recipes and a set of
attacks for checking existing biometric pipelines:

.. code-block:: bibtex

  @inproceedings{Tome_IEEEBIOSIG2014,
    author = {Tome, Pedro and Vanoni, Matthias and Marcel, S{\'{e}}bastien},
    keywords = {Biometrics, Finger vein, Spoofing Attacks},
    month = sep,
    title = {On the Vulnerability of Finger Vein Recognition to Spoofing},
    booktitle = {IEEE International Conference of the Biometrics Special Interest Group (BIOSIG)},
    year = {2014},
    location = {Darmstadt, Germay},
    url = {http://publications.idiap.ch/index.php/publications/show/2910}
  }


This paper contains results for the first fingervein presentation-attack
detection competition. It also introduces protocols for PAD in the context of
fingerveins:

.. code-block:: bibtex

  @inproceedings{Tome_ICB2015_AntiSpoofFVCompetition,
    author = {Tome, Pedro and Raghavendra, R. and Busch, Christoph and Tirunagari, Santosh and Poh, Norman and Shekar, B. H. and Gragnaniello, Diego and Sansone, Carlo and Verdoliva, Luisa and Marcel, S{\'{e}}bastien},
    keywords = {Biometrics, Finger vein, Spoofing Attacks, Anti-spoofing},
    month = may,
    title = {The 1st Competition on Counter Measures to Finger Vein Spoofing Attacks},
    booktitle = {The 8th IAPR International Conference on Biometrics (ICB)},
    year = {2015},
    location = {Phuket, Thailand},
    url = {http://publications.idiap.ch/index.php/publications/show/3095}
  }


Documentation
-------------

.. toctree::
   :maxdepth: 2

   guide
   bio
   pa
   references
   py_api

.. todolist::

.. include:: links.rst
