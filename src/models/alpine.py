from models.hashforest import HashForest
import numpy as np

#TODO: add payload delimited by whitespace to tokens as option.
#TODO: add point-cloud payload to tokens as option.
#TODO: any other useful features or ways to represent a payload?

class Alpine(HashForest):
    """
    Classifies packets based on a hash of header features
    """
    def __init__(self, hash="sha1", columns=["sip","dip","sport","dport","prot","length","dsfield","ip_flags"]):
        """
        Initializes the ALPINE model.

        Args:
            hash    optional parameter to use a different hash function, options are xxhash, farmhash, m3hash
            columns optional parameter to list which columns from input dataframe to select for hash values
        """
        HashForest.__init__(self, hash)
        self.columns = columns
        print("Using these features for ALPINE: " + str(columns))

    def _process_data(self, data):
        """
        Extracts a subset of the data columns provided.

        Args:
            data    the dataframe to process

        Return:
            the columns extracted
        """
        values = data[self.columns]
        values = values.astype('str').fillna("")
        return values

    #TODO: Instead of reading these from csv, should pull from pcap
    def hash(self, data):
        """
        overridden function to call the hash function to make MinHashes

        Args:
            data the dataframe, pre-processed

        Return:
            The hashes as a numpy array
        """
        return np.array(HashForest.hash(self, data))
