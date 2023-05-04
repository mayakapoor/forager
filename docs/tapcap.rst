TaPCAP
=======

TaPCAP provides the ability to "tap" into packet capture files (PCAP or PCAPNG),
decode bytes into readable human format, and extract specific header fields in
order to create tabular feature data.

.. code-block::

  Forager: A Network Training Classification Toolkit.
         Please choose a task:

  => tabularize packet data (TapCap)
    mine tokens only (RExACtor)
    generate regular expression signatures (RExACtor)
    configure and train models (ALPINE, PALM, MAPLE, DATE)
    classify packets (ALPINE, PALM, MAPLE, DATE)
    clear current cache


Installation
~~~~~~~~~~~~~

At the command line::

    easy_install tapcap

Or, if you have pip installed::

    pip install tapcap

Usage
~~~~~~

.. code-block::

  usage: tapcap.py [-h] --pcap <input pcap file> --csv <output csv file>
  optional arguments:
  -h, --help               show this help message and exit
  --pcap <input pcap file> pcap file to parse
  --csv <output csv file>  csv file to create

TaPCAP accepts two arguments: a **PCAP input file path** and a **CSV output file
path**. Both of these paths should be provided as absolute paths. The input file
will be parsed according to the following schema into CSV format, and written
to the provided output path.

.. list-table:: Output Schema
   :widths: 10 20 50
   :header-rows: 1

   * - Index
     - Feature
     - Description
   * - 0
     - Frame Number
     - Indicates the order in which packets appeared in the capture file.
   * - 1
     - `Time <https://www.elvidence.com.au/understanding-time-stamps-in-packet-capture-data-pcap-files/>`_
     - Timestamp derived from the machine which performed the packet capture.
   * - 2
     - `Highest Protocol <https://thepacketgeek.com/pyshark/packet-object/>`_
     - The highest layer protocol detected in the packet using PyShark.
   * - 3
     - `L4 Protocol <https://thepacketgeek.com/pyshark/packet-object/>`_
     - The transport layer protocol (ex: TCP, UDP) detected using PyShark.
   * - 4
     - `Text <https://thepacketgeek.com/pyshark/packet-object/>`_
     - Summary of application layer info, (e.g. ‘HTTP GET /resource_folder/page.html'). In PyShark, this is the ".info" layer of the Packet object.
   * - 5
     - Source IP Address
     - IP address from which the packet was sent.
   * - 6
     - Source Port
     - The port from which the packet was sent (from source IP address).
   * - 7
     - Destination IP Address
     - IP address which the packet is destined for.
   * - 8
     - Destination Port
     - The port which the packet is destined for (to destination IP address).
   * - 9
     - Total Packet Length
     - The length of the packet, in bytes.
   * - 10
     - `IP Flags <https://www.rfc-editor.org/rfc/rfc791/>`_
     - Bit 0: reserved, Bit 1: Do Not Fragment flag, Bit 2: More Fragments flag.
   * - 11
     - `Differentiated Services (DS) Field <https://www.rfc-editor.org/rfc/rfc2474/>`_
     - Marks data belonging to certain protocols so they get priority through the network. In IPv4, also called the Type of Service (ToS) field; in IPv6, also called the Traffic Class field.
   * - 12
     - Hexdump
     - The literal raw bytes of the packet in hexadecimal.
