.. vim: set fileencoding=utf-8 :

==============
 User's Guide
==============

This package contains the access API and descriptions for the `UTFVP Fingervein
Database`_. It only contains the Bob_ accessor methods to use the DB directly
from python, with our certified protocols. The actual raw data for the dataset
should be downloaded from the original URL.


Data
----

The fingervein image database consists of 1440 images taken in 2 distinct
session in two days (May 9th, 2012 and May 23rd, 2012) using a custom built
fingervein sensor. In each session, each of the 60 subjects in the dataset were
asked to present 6 fingers to the sensor twice, making up separate tries. The
six fingers are the left and right ring, middle and index fingers. Therefore,
the database contains 60x6 = 360 unique fingers.

Files in the database have a strict naming convention and are organized in
directories following their subject identifier like so:
``0003/0003_5_2_120509-141536``. The fields can be interpreted as
``<subject-id>/<subject-id>_<finger-name>_<trial>_<date>-<hour>``. The subject
identifier is written as a 4-digit number with leading zeroes, varying from 1
to 60. The finger name is one of the following:

  * **1**: Left ring
  * **2**: Left middle
  * **3**: Left index
  * **4**: Right index
  * **5**: Right middle
  * **6**: Right ring

The trial identifiers can vary between 1 and 4. The first two tries were
captured during the first session while the last two, on the second session.
Given the difference in the images between trials on the same day, we assume
users were asked to remove the finger from the device and re-position it
afterwards.


Annotations
===========

We provide region-of-interest (RoI) **hand-made** annotations for all images in
this dataset. The annotations mark the place where the finger is on the image,
excluding the background. The annotation file is a text file with one
annotation per line in the format ``(y, x)``, respecting Bob's image encoding
convention. The interconnection of these points in a polygon forms the RoI.
Annotations can be loaded using :py:meth:`bob.db.utfvp.File.roi`.


Protocols
---------

There are 15 protocols implemented in this package:

 * 1vsall
 * nom
 * nomLeftRing
 * nomLeftMiddle
 * nomLeftIndex
 * nomRightIndex
 * nomRightMiddle
 * nomRightRing
 * full
 * fullLeftRing
 * fullLeftMiddle
 * fullLeftIndex
 * fullRightIndex
 * fullRightMiddle
 * fullRightRing

They are described next.


"nom" Protocols
===============

"nom" means "normal operation mode". In this set of protocols, images from
different clients are separated in different sets that can be used for system
training, validation and evaluation:

  * Fingers from clients in the range [1, 10] are used on the training set
  * Fingers from clients in the range [11, 28] are used on the development
    (or validation) set
  * Fingers from clients in the range [29, 60] are used in the evaluation
    (or test) set

Data from the first session (both trials) can be used for enrolling the finger
while data on the last session (both trials) shold be used exclusively for
probing the finger. In the way setup by this database interface, each of the
samples is returned as a separate enrollment model. If a single score per
finger is required, the user must manipulate the final score listings and fuse
results themselves.

Matching happens exhaustively between all probes and models. The variants named
"nomLeftRing", for example, contain the data filtered by finger name as per the
listings above. For example, "Left Ring" means all files named
``*/*_1_*_*-*.png``. Therefore, the equivalent protocol contains only 1/6 of
the files of its complete ``nom`` version.

The following table specifies the number of samples in each set, together with
the counts of samples, models and probes in each ``nom`` protocol.


.. table:: Counts for the ``nom`` protocols
   :widths: auto

   ================== =============== ======== ======== ==============  ======== ======== ==============
                         Training               Development                       Evaluation
   ------------------ --------------- --------------------------------  --------------------------------
    Protocol              Samples      Models   Probes   Probes/Model    Models   Probes   Probes/Model
   ================== =============== ======== ======== ==============  ======== ======== ==============
    nom                    240           216      216        216           384      384        384
    nomLeftRing             40            36       36         36            64       64         64
    nomLeftMiddle           40            36       36         36            64       64         64
    nomLeftIndex            40            36       36         36            64       64         64
    nomRightIndex           40            36       36         36            64       64         64
    nomRightMiddle          40            36       36         36            64       64         64
    nomRightRing            40            36       36         36            64       64         64
   ================== =============== ======== ======== ==============  ======== ======== ==============


"full" Protocols
================

"full" protocols are meant to match current practices in fingervein reporting
in which most published material don't use a separate evaluation set. All data
is placed on the development (or validation) set. In these protocols, all
images are used both for enrolling and probing for fingers. It is, of course,
a biased setup. Matching happens exhaustively between all samples in the
development set.


The variants named "fullLeftRing", for example, contain the data filtered by
finger name as per the listings above. For example, "Left Ring" means all files
named ``*/*_1_*_*-*.png``. Therefore, the equivalent protocol contains only 1/6
of the files of its complete ``full`` version.

The following table specifies the number of samples in each set, together with
the counts of samples, models and probes in each ``full`` protocol.

.. table:: Counts for the ``full`` protocols
   :widths: auto

   ================== =============== ======== ======== ==============  ======== ======== ==============
                         Training               Development                       Evaluation
   ------------------ --------------- --------------------------------  --------------------------------
    Protocol              Samples      Models   Probes   Probes/Model    Models   Probes   Probes/Model
   ================== =============== ======== ======== ==============  ======== ======== ==============
    full                     0         1440      1440       1440            0         0          0
    fullLeftRing             0          240       240        240            0         0          0
    fullLeftMiddle           0          240       240        240            0         0          0
    fullLeftIndex            0          240       240        240            0         0          0
    fullRightIndex           0          240       240        240            0         0          0
    fullRightMiddle          0          240       240        240            0         0          0
    fullRightRing            0          240       240        240            0         0          0
   ================== =============== ======== ======== ==============  ======== ======== ==============


"1vsall" Protocol
=================

The "1vsall" protocol is meant as a cross-validation protocol. All data from
the dataset is split into training and development (or validation). No samples
are allocated for a separate evaluation (or test) set. The training set is
composed of all samples of fingers ``0001_1`` (left ring finger of subject 1),
``0002_2`` (left middle finger of subjec 2), ``0003_3`` (left index finger of
subject 3), ``0004_4`` (right index finger of subject 4), ``0005_5`` (right
middle finger of subject 5), ``0006_6`` (right ring finger of subject 6),
``0007_1`` (left ring finger of subject 7), ``0008_2`` (left middle finger of
subject 8) and so on, until subject 35 (inclusive). There are 140 images in
total on this set.

All other 1300 samples from the dataset are used as a development (or
validation) set. Each sample generates a single model and is used as a probe
for all other models. Matching happens exhaustively, but with the same image
that generated the model being matched. So, there are 1299 probes per model.
The following table specifies the number of samples in each set, together with
the counts of samples, models and probes this protocol.


.. table:: Counts for the ``1vsall`` protocol
   :widths: auto

   ================== =============== ======== ======== ==============  ======== ======== ==============
                         Training               Development                       Evaluation
   ------------------ --------------- --------------------------------  --------------------------------
    Protocol              Samples      Models   Probes   Probes/Model    Models   Probes   Probes/Model
   ================== =============== ======== ======== ==============  ======== ======== ==============
    1vsall                 140         1300      1300       1299            0         0          0
   ================== =============== ======== ======== ==============  ======== ======== ==============


.. Place your references here
.. _bob: https://www.idiap.ch/software/bob
.. _utfvp fingervein database: http://www.sas.el.utwente.nl/home/datasets
