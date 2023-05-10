ALPINE
=======

ALPINE is A Locality-Sensitive Packet Inspection Engine which
generates locality-sensitive hash fingerprints from feature sets extracted from
the headers of packets through :ref:`tapcap`.

Feature Extraction
~~~~~~~~~~~~~~~~~~~

.. list-table:: Header Features
   :widths: 20 50
   :header-rows: 1

   * - Feature
     - Description
   * - `L4 Protocol <https://thepacketgeek.com/pyshark/packet-object/>`_
     - The transport layer protocol (ex: TCP, UDP) detected using PyShark.
   * - Source IP Address
     - IP address from which the packet was sent.
   * - Source Port
     - The port from which the packet was sent.
   * - Destination IP Address
     - IP address which the packet is destined for.
   * - Destination Port
     - The port which the packet is destined for.
   * - Total Packet Length
     - The length of the packet, in bytes.
   * - `IP Flags <https://www.rfc-editor.org/rfc/rfc791/>`_
     - Bit 0: reserved, Bit 1: Do Not Fragment flag, Bit 2: More Fragments flag.
   * - `Differentiated Services (DS) Field <https://www.rfc-editor.org/rfc/rfc2474/>`_
     - Marks data belonging to certain protocols so they get priority through the network.


MinHash LSH Forest
~~~~~~~~~~~~~~~~~~~

For each feature set, ALPINE uses the MinHash algorithm to generate hash values
which can be compared among packets (see `datasketch <https://ekzhu.com/datasketch/lsh.html>`_ for further details).

Suppose you have a very large collection of `sets <https://en.wikipedia.org/wiki/Set_(mathematics)>`_.
Given a query, which is also a set, you want to find sets in your collection
that have Jaccard similarities above certain threshold, and you want to do it
with many other queries. To do this efficiently, you can create a MinHash for
every set, and when a query comes, you compute the Jaccard similarities between
the query MinHash and all the MinHash of your collection, and return the sets
that satisfy your threshold.

The said approach is still an O(n) algorithm, meaning the query cost increases
linearly with respect to the number of sets. A popular alternative is to use
Locality Sensitive Hashing (LSH) index. LSH can be used with MinHash to achieve
sub-linear query cost - that is a huge improvement. The details of the algorithm
can be found in `Chapter 3, Mining of Massive Datasets <http://infolab.stanford.edu/~ullman/mmds/ch3.pdf>`_.

In order to support **top-k** queries, ALPINE implements
`MinHashLSHForest <https://ekzhu.com/datasketch/lshforest.html>`_.
Bawa et al proposed `LSH Forest <http://ilpubs.stanford.edu:8090/678/1/2005-14.pdf>`_
as a general LSH data structure that makes top-k query possible for many
different types of LSH indexes, including MinHash LSH. The MinHash LSH Forest
takes a MinHash data sketch of the query set and returns the top-k matching
sets that have approximately the highest Jaccard similarities with the query set.

Storage and Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~

For optimization and re-use, MinHash LSH Forest supports "pickling" as the MinHash LSH
object is serializable. By default, ALPINE MinHash LSH are stored in the "cache"
directory in the forager source directory under the "alpine" directory.
``alpine.bin`` contains the serialized binary object which will be reloaded when
Forager is run in test mode and where data will be written when run in training
mode. ``labels.txt`` contains the labels corresponding to the indexes assigned
by MinHash LSH Forest for query lookup. For accuracy, it is important that the
same labels file which is generated when the MinHash LSH Forest is created in
training mode is used for classification during testing mode.


Installation
~~~~~~~~~~~~~

ALPINE is included as a supported module inside Forager.


Usage
~~~~~

ALPINE must be pre-trained with data and labels before being used for classification.
PCAP/PCAPNG data may be provided to :ref:`tapcap` and given a label during the
training steps. You may add as many labels and input files as you would like to
the training model.

**Training Mode**:

.. code-block::

  Forager: A Network Training Classification Toolkit.
          Please choose a task:

     tabularize packet data (TapCap)
     mine tokens only (RExACtor)
     generate regular expression signatures (RExACtor)
  => configure and train models (ALPINE, PALM, MAPLE, DATE)
     classify packets (ALPINE, PALM, MAPLE, DATE)
     clear current cache

In the main Forager menu, select "configure and train models" from the options.
Note that if you choose to proceed, the stored model and labels in the cache
directory will be overwritten. To save these models, copy them elsewhere before
proceeding to train new ones. Next, select ALPINE as a training model. Note here
that you may choose to train multiple models sequentially to save manual entry
and effort.

.. code-block::

  Forager: A Network Training Classification Toolkit.
  Please choose one or more models to train (press SPACE to mark, ENTER to continue):

  => (x) ALPINE
     ( ) PALM
     ( ) MAPLE
     ( ) DATE

Following selection, you will be asked to provide input files and a label for
each file. Labels may be re-used for multiple files. Note that labels must be
exact in order to match (i.e. case-sensitive, spelled identically). You will be
prompted for more files until you reply 'n'.

.. code-block::

  Forager: A Network Training Classification Toolkit
  Entering training mode...
  WARNING: editing a model's configuration will override its current cache and settings. Continue (y/n)? y
  CSV file input path? /Users/mkapoor1/Desktop/pop.csv
  Label? POP3
  Add another file (y/n)?

Once input files are provided, training will commence and the MinHash LSH Forest
will be serialized and saved to ``cache/alpine/alpine.bin``. The labels will be
saved to ``cache/alpine/labels.txt``.

**Publication:**

Kapoor, M., Krishnan, S., Moyer, T.
`Deep Packet Inspection at Scale: Search Optimization Through Locality-Sensitive Hashing.
<https://ieeexplore.ieee.org/document/10013504>`_
In proceedings of IEEE 21st International Symposium
on Network Computing and Applications (NCA). 14-16 December, 2022.
