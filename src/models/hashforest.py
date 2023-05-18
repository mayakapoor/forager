import re
import farmhash
import xxhash
import mmh3
import hashlib
import numpy as np
import random
from collections import defaultdict
from datasketch import MinHash, MinHashLSHForest

#TODO: add payload delimited by whitespace to tokens as option.
#TODO: add point-cloud payload to tokens as option.
#TODO: any other useful features or ways to represent a payload?

class HashForest:
    """
    This is the parent class for ALPINE and PALM models.

    It is modeled with the same API as a sci-kit learn model, where data should be fit, then predictions made.
    """
    def __init__(self):
        """
        Initializes the number of MinHash permutations and number of votes for classification.
        """
        self.my_forest = MinHashLSHForest(num_perm=256)
        self.hash_type = "sha1"
        self.my_lookup_table = {}
        self.my_num_votes = 10

    def __init__(self, hash):
        """
        Initializes the number of MinHash permutations and number of votes for classification.
        """
        self.my_forest = MinHashLSHForest(num_perm=256)
        self.my_lookup_table = {}
        self.my_num_votes = 10

        if hash == "farmhash":
            self.hash_type = "farmhash"
        elif hash == "xxhash":
            self.hash_type = "xxhash"
        elif hash == "mmh3":
            self.hash_type = "mmh3"
        else:
            self.hash_type = "sha1"

    def hash(self, np_data):
        """
        generates a bulk of MinHashes using a configured number of permutations.

        Args:
            np_data    The dataframe containing the header features to hash

        Return:
            list of hash values
        """
        if self.hash_type == "sha1":
            encoder = np.vectorize(self._encode)
            np_data = encoder(np_data)
            return MinHash.bulk(np_data, num_perm=256)
        return MinHash.bulk(np_data, num_perm=256,hashfunc=self._hash_func)

    # We need to define a new hash function that outputs an integer that
    # can be encoded in 32 bits.
    def _hash_func(self, d):
        """
        allows for a different hash than sha1 if desired (not recommended)

        Args:
            d    the data to hash

        Return:
            the hashed value
        """
        if self.hash_type == "farmhash":
            return farmhash.hash32(d)
        elif self.hash_type == "xxhash":
            return xxhash.xxh32(d).intdigest()
        elif self.hash_type == "mmh3":
            return mmh3.hash(d)

    def _encode(self, x):
        """
        data must be encoded to utf-8 for hashing if it is not already

        Args:
            x    the data to encode

        Return:
            the encoded value
        """
        return x.encode('utf-8')

    def _process_data(self, data):
        """
        dummy method, children may override if additional processing needs to be done before data is hashed.

        Return:
            additionally processed data
        """
        return data

    def add_bucket(self, data, label, count):
        """
        Adds training data to the model with the label. You should add a bucket for each class when building a model.

        Args:
            data    the dataframe, one row for each packet sample
            label   the label to assign to this data sample, i.e. what its classified as, ground truth
            count   a recurring value used as the sample's index. One label has multiple indexes underneath it.
        """
        minhashes = self.hash(self._process_data(data))
        for m in minhashes:
            # add the hash with its index to the forest
            self.my_forest.add(count[0], m)
            self.my_lookup_table[count[0]] = label
            count[0] += 1

    def fit(self):
        """
        Calls the indexing function which builds the finalized forest model for searching. Data cannot be added after calling, model cannot be searched before calling.
        """
        self.my_forest.index()

    def set_votes(self, num):
        """
        Sets a different number of votes for classifying if desired

        Args:
            num    number of votes to set
        """
        self.my_num_votes = num

    def predict(self, data):
        """
        Makes the predictions calling the classifier and looking up the index in the built forest.

        Args:
            data    the y_test data to make predictions on

        Return:
            a list of lists where each list is the forests' votes for a sample from the input data
        """
        data = self._process_data(data)
        minhashes = self.hash(data)
        all_arrs = []
        first = True
        for m in minhashes:
            arr = np.array(self.my_forest.query(m, self.my_num_votes))
            lookup_results = []
            for ret in arr:
                lookup_results.append(self.my_lookup_table[ret])

            if len(lookup_results) < self.my_num_votes:
                remain = self.my_num_votes - len(lookup_results)
                #print("WARNING: no close proximity match found. Using random result")
                choice = random.choice(range(0, len(self.my_lookup_table)))
                supplement = [self.my_lookup_table[choice]] * remain
                lookup_results = lookup_results + supplement

            all_arrs.append(lookup_results)
        return all_arrs
