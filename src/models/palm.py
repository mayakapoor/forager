from models.hashforest import HashForest
import numpy as np
from datasketch import MinHash

class Palm(HashForest):
    """
    Classifies packets based on a hash of the payload.
    """
    def __init__(self, hash="sha1", col_name="payload"):
        """
        Initialize the PALM model.

        Args:
            hash     optional parameter to change the hash type, can be xxhash, farmhash, or mm3hash
            col_name the name of the column containing the text payload
        """
        HashForest.__init__(self, hash)
        self.col_name = col_name

    #TODO: instead of reading these from csv, should pull directly from pcap
    def hash(self, data):
        """
        Overridden function which first delimits the payload and then generates the hash from it as tokens

        Args:
            data   the input dataframe

        Return:
            list of the hash values from MinHash
        """
        tokens = []
        for i, row in data.iterrows():
            raw_tokens = str(row[self.col_name]).split()
            if (self.hash_type == "sha1"):
                encoded_tokens = []
                for token in raw_tokens:
                    encoded_tokens.append(token.encode('utf-8'))
                tokens.append(encoded_tokens)
            else:
                tokens.append(raw_tokens)
        if (self.hash_type == "sha1"):
            return MinHash.bulk(tokens, num_perm=256)
        return MinHash.bulk(tokens, num_perm=256,hashfunc=self._hash_func)
