import numpy as np
import pandas
import pyshark
from PIL import Image

def delimiterToken(pcap):
    """
    Extracts the payloads and separates them by whitespace

    Args:
        pcap: the pcap file to pull payloads from

    Returns:
        list of tokenized payloads
    """
    i = 0
    payloads = []
    # go through every packet in a pcap and add both representations
    # of the payload to two seperate lists
    for p in pcap:
        tokened,length = tokenPayload(p)
        if tokened == None:
            continue
        tokened =  list(map(lambda hex: chr(hex), tokened))
        sentence = ''.join(tokened)
        delimitedTok = sentence.split()
        payloads.append(delimitedTok)
    print(payloads[0])
    #will return payload list
    return payloads

#takes a pcap of one session and then makes a gray scale image from
#the first 90 packets or till it is 784 bytes long.
def matrix2d(pcap):
    """
    Makes a gray scale image from the first 784 bytes.
    """
    #count = 0
    payload = []
    matpayloads = []
    # go through every packet in a pcap and add both representations
    # of the payload to two seperate lists
    for p in pcap:
        tokened,length = tokenPayload(p)
        #matrixed = payMatrix(p)
        if tokened == None:
            continue
        #count += 1
        #if len(payload) > 784 or count == 90:
            #break
        matrixed = payMatrix(tokened, len(tokened))
        matpayloads.append(matrixed)
    #will return payload list as a padded matrix
    return matpayloads

#below is the corresponding function to the 224x224 papers method
'''def matrix2d(pcap):
    i = 0
    matpayloads = []
    maxpayload = 0
    # go through every packet in a pcap and add both representations
    # of the payload to two seperate lists
    for p in pcap:
        tokened,length = tokenPayload(p)
        #matrixed = payMatrix(p)
        if tokened == None:
            continue
        matrixed = payMatrix(tokened, length)
        matpayloads.append(matrixed)
    #will return payload list as a padded matrix
    return matpayloads'''

def matrix3d(pcap):
    """
    Right now just make a 3d matrix from the payload shape still needs to be decided
    """
    payloads3d = []
    # go through every packet in a pcap and add both representations
    # of the payload to two seperate lists
    for p in pcap:
        tokened,length = tokenPayload(p)
        #matrixed = payMatrix(p)
        if tokened == None:
            continue
        matrixed = payMatrix3d(tokened, length)
        payloads3d.append(matrixed)
    #will return payload list as a padded matrix
    return payloads3d


def tokenPayload(packet):
    """
        first extracts the payloads and then returns a list of the bytes of the payload as ints
    """
    payload = None
    #check if tcp and has payload
    if hasattr(packet, 'tcp'):
        prot = 'tcp'
        if hasattr(packet.tcp, "payload"):
            payload = packet.tcp.payload
    #check if udp and has payload
    elif hasattr(packet, 'udp'):
        prot = 'udp'
        if hasattr(packet.udp, "payload"):
            payload = packet.udp.payload
    if not payload:
        return None,0
    #split the payload into the individual numbers
    payload = payload.split(':')
    #convert them from hexi to integers based 10
    payload = list(map(lambda num: int(num,16), payload))
    return payload, len(payload)

def payMatrix(payArray, size):
    """
    This makes a 2-d representation of the payload makes it into a 28x28 image

    Any payload larger than this will be trimmed.
    Any smaller will be zero padded.

    Args:
        payArray: the payload as an array of ints
        size: total size of payload array

    Returns:
        2d matrix of the payload
    """
    #take several packet data split and make grayscale
    #making 28x28 so only want 784 bytes
    if size < 784:
        pads = 784 - size
        pad = [0 for i in range(pads)]
        #adding 0's to the end so we can reshape it
        payArray = payArray + pad
    elif size > 784:
        #trimming if more bytes than needed
        payArray = payArray[:784]
    #numpy reshapes for you so convert
    matrix = np.array(payArray).reshape(28,28).astype(np.uint8)
    #image = Image.fromarray(matrix)
    #return the image for the sessino
    return matrix

#below is the code to make a grayscale image for the payload
#seen in a different paper making it a size of 224x224
'''def payMatrix(payArray,size):
    #take the token version and reshape it
    #payArray,length = tokenPayload(packet)
    if not payArray:
        return None
    #rows on wireshark are len 16 so doing the same
    #want all rows to be same length
    #pads = 16 - (size%16) + (size - len(payArray))
    #like the packet vision paper where size is nx8
    pads = 8 - (size%8) + (size - len(payArray))
    #pads = 256*256 - len(payArray)
    pad = [0 for i in range(pads)]
    #adding 0's to the end so we can reshape to rows of 16
    payArray = payArray + pad
    #numpy reshapes for you so convert
    #matrix = np.array(payArray).reshape(-1,16)
    matrix = np.array(payArray).reshape(-1,8).astype(np.uint8)
    image = Image.fromarray(matrix)
    image = image.resize((224,224))
    #matrix = np.array(payArray).reshape(256,256)
    return image'''

def payMatrix3d(payArray,size):
    """
    This makes a 3-d representation of the payload making it nx8x3
    Any payload larger than this will be trimmed.
    Any smaller will be zero padded.

    Args:
        payArray: the payload as an array of ints
        size: total size of payload array

    Returns:
        3d matrix of the payload
    """

    pads = 24 - (size%24) + (size - len(payArray))
    pad = [0 for i in range(pads)]
    #adding 0's to the end so we can reshape to rows of 16
    payArray = payArray + pad
    #numpy reshapes for you so convert
    #matrix = np.array(payArray).reshape(-1,16)
    matrix = np.array(payArray).reshape(-1,8,3)
    return matrix


'''pcap = pyshark.FileCapture('../datasets/raw/combined_pcaps/bittorrent.pcap')
pcaps = matrix2d(pcap)
for i in range(10):
    Image.fromarray(pcaps[i]).save('28x28_'+str(i)+'.jpeg')'''
