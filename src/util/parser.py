import argparse
import os
import glob
import gzip
import zlib
import bz2
import pyshark
import nest_asyncio
import pandas as pd
nest_asyncio.apply()
from csv import writer

#----------------------#
#   Helper functions
#----------------------#

def fileToList(path):
    """
    Convert a file of strings to a list of strings

    Args:
        path: the path of the file
        encoding: the encoding of the file

    Returns:
        the list of strings
    """
    lst = []
    try:
        f = open(path, "r", encoding="latin-1")
    except:
        return lst
    for line in f:
        lst.append(line.rstrip())
    f.close()
    return lst

# write a line to the file at path
def writeToFile(path, line):
    """
    Write a line to the file at the provided path

    Args:
        path: the path for the file
        line: the line to write to file
    """
    f = open(path, 'a+')
    f.write(line + '\n')

def hexToChar(hex_string):
    """
    Convert a hex string to ASCII characters

    Args:
        hex_string: the hex string to convert

    Returns:
        ASCII string
    """
    hex_split = hex_string.split(':')
    hex_as_chars = map(lambda hex: chr(int(hex, 16)), hex_split)
    human_readable = ''.join(hex_as_chars)
    return human_readable

def parsePacketsAndCompress(input_path, label):
    """
    Parse input PCAPs and apply a random compression algorithm to their payload

    sip: Source IP Address
    dip: Destination IP Address
    sport: Source port
    dport: Destination port
    prot: Transport protocol
    dsfield: differentiated services field
    ipflags: IP flag value
    length: packet length in bytes
    label: assigned label (parameter)
    comptype: The type of compression done on the payload
    payload: packet payload, if present, compressed

    Args:
        input_path: the input path for the pcap file
        label: the label to assign to the data sample(s)

    Returns:
        pandas dataframe containing header features, payload, and label for each sample
    """
    df = pd.DataFrame(columns=['sip', 'dip', 'sport', 'dport', 'prot', 'dsfield', 'ip_flags', 'length', 'label', 'comptype', 'payload'])
    properties = []
    count = 0

    try:
        packets = pyshark.FileCapture(input_path, use_json=True)
        print("Loading PCAP input file.")

        for packet in packets:
            count += 1
            sip = None
            dip = None
            prot = None
            d_proto = None
            dsfield = None
            ip_flags = None
            payload = None
            comptype = None

            if hasattr(packet, 'ip'):
                sip = packet.ip.src
                dip = packet.ip.dst
                dsfield = packet.ip.dsfield
                ip_flags = packet.ip.flags

            if hasattr(packet, 'ipv6'):
                sip = packet.ipv6.src
                dip = packet.ipv6.dst

            if hasattr(packet, 'tcp'):
                prot = 'tcp'
                if hasattr(packet.tcp, "payload"):
                    if counter % 3 == 0:
                        payload = gzip.compress(bytes(packet.tcp.payload, 'utf-8'))
                        comptype = "gzip"
                    elif counter % 5 == 0:
                        payload = zlib.compress(bytes(packet.tcp.payload, 'utf-8'))
                        comptype = "zlib"
                    else:
                        payload = bz2.compress(bytes(packet.tcp.payload, 'utf-8'))
                        comptype = "bz2"
                    counter += 1

            elif hasattr(packet, 'udp'):
                prot = 'udp'
                if hasattr(packet.udp, "payload"):
                    if counter % 3 == 0:
                        payload = gzip.compress(bytes(packet.udp.payload, 'utf-8'))
                        comptype = "gzip"
                    elif counter % 5 == 0:
                        payload = zlib.compress(bytes(packet.udp.payload, 'utf-8'))
                        comptype = "zlib"
                    else:
                        payload = bz2.compress(bytes(packet.udp.payload, 'utf-8'))
                        comptype = "bz2"
                    counter += 1
            else:
                print("discarding non-TCP/UDP packet, detected: " + str(packet.highest_layer))
                continue

            sport = packet[packet.transport_layer].srcport
            dport = packet[packet.transport_layer].dstport
            length = packet.length
            properties.append([sip, dip, sport, dport, prot, dsfield, ip_flags, length, label, comptype, payload])

    except (UnicodeDecodeError):
        print("Could not load PCAP due to parsing error, skipping.")
        return count

    properties_frame = pd.DataFrame(properties, columns=['sip', 'dip', 'sport', 'dport', 'prot', 'dsfield', 'ip_flags', 'length', 'label', 'comptype', 'payload'])
    df = pd.concat([df, properties_frame])
    return df

def parsePackets(input_path, label):
    """
    Parse input PCAPs to get header features and payload

    sip: Source IP Address
    dip: Destination IP Address
    sport: Source port
    dport: Destination port
    prot: Transport protocol
    dsfield: differentiated services field
    ipflags: IP flag value
    length: packet length in bytes
    label: assigned label (parameter)
    payload: packet payload, if present

    Args:
        input_path: the input path for the pcap file
        label: the label to assign to the data sample(s)

    Returns:
        pandas dataframe containing header features, payload, and label for each sample
    """
    df = pd.DataFrame(columns=['sip', 'dip', 'sport', 'dport', 'prot', 'dsfield', 'ip_flags', 'length', 'label', 'payload'])
    properties = []
    count = 0

    try:
        packets = pyshark.FileCapture(input_path, use_json=True)
        print("Loading PCAP input file.")

        for packet in packets:
            count += 1
            sip = None
            dip = None
            prot = None
            d_proto = None
            dsfield = None
            ip_flags = None
            payload = None

            if hasattr(packet, 'ip'):
                sip = packet.ip.src
                dip = packet.ip.dst
                dsfield = packet.ip.dsfield
                ip_flags = packet.ip.flags

            if hasattr(packet, 'ipv6'):
                sip = packet.ipv6.src
                dip = packet.ipv6.dst

            if hasattr(packet, 'tcp'):
                prot = 'tcp'
                if hasattr(packet.tcp, "payload"):
                    payload = hexToChar(packet.tcp.payload)
            elif hasattr(packet, 'udp'):
                prot = 'udp'
                if hasattr(packet.udp, "payload"):
                    payload = hexToChar(packet.udp.payload)

            else:
                print("discarding non-TCP/UDP packet, detected: " + str(packet.highest_layer))
                continue

            sport = packet[packet.transport_layer].srcport
            dport = packet[packet.transport_layer].dstport

            length = packet.length

            #if sip is None or dip is None or sport is None or dport is None or prot is None:
            #    pass
            properties.append([sip, dip, sport, dport, prot, dsfield, ip_flags, length, label, payload])

    except (UnicodeDecodeError):
        print("Could not load PCAP due to parsing error, skipping.")
        return count

    properties_frame = pd.DataFrame(properties, columns=['sip', 'dip', 'sport', 'dport', 'prot', 'dsfield', 'ip_flags', 'length', 'label', 'payload'])
    df = pd.concat([df, properties_frame])
    return df, count

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process pcap file and integer data.")
    parser.add_argument("-dir", help="The directory containing the pcap files.")
    parser.add_argument("-label", help="label to assign to this pcap group.")
    args = parser.parse_args()
    out_dir = os.getcwd()
    os.chdir(str(args.dir))
    path = os.getcwd()
    filecount = 0
    total = 0
    oldtotal = 0

    output_prefix = out_dir + "/../datasets/processed"
    if not os.path.exists(output_prefix):
        os.makedirs(output_prefix)
    filename = (output_prefix + "/" + str(args.label))
    ext = str(filecount) + ".csv"

    for root,dirs,files in os.walk(path):
        pcap_files = glob.glob(os.path.join(root, "*.pcap"))

        for pcap in files:
            df, count = parsePackets(pcap, str(args.label))
            total += count
            print("Number of packets processed: %d" % total)
            filecount += 1
            ext = str(filecount) + ".csv"
            df.to_csv(filename + ext)
