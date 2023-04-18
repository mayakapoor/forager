from models.hashforest.alpine import Alpine
from models.hashforest.palm import Palm
from models.date import Date
from models.maple import Maple
from collections import defaultdict
import random
import itertools
import numpy as np
from sklearn.preprocessing import OneHotEncoder

from memory_profiler import profile

"""
Forager is the ensembler for the different supported models.
Implementers should declare a Forager and train it with the classes they want.
"""
class Forager():
    def __init__(self, ALPINE=False, PALM=False, MAPLE=False, DATE=False):
        """
        Initializes the ensemble classifier with a collection of selected models.

        Args:
            ALPINE: bool to indicate whether model is enabled or not.
            PALM:   bool to indicate whether model is enabled or not.
            MAPLE:  bool to indicate whether model is enabled or not.
            DATE:   bool to indicate whether model is enabled or not.

        Examples:
            >>> forager = Forager(ALPINE=True, PALM=True)
                models ALPINE and PALM would be run, MAPLE and DATE disabled.
        """
        self.alpine = None
        self.ALPINE_ENABLED = ALPINE
        if ALPINE:
            print("ALPINE model enabled.")
        self.palm = None
        self.PALM_ENABLED = PALM
        if PALM:
            print("PALM model enabled.")
        self.maple = None
        self.MAPLE_ENABLED = MAPLE
        if MAPLE:
            print("MAPLE model enabled.")
        self.date = None
        self.DATE_ENABLED = DATE
        if DATE:
            print("DATE model enabled.")
        self.finalized = False

    def plant_alpine(self):
        """
        Can be called to enable ALPINE model outside of constructor
        """
        self.alpine = Alpine(columns=["sport","dport","prot","length","dsfield","ip_flags"])
        #self.alpine = Alpine()
        self.ALPINE_ENABLED = True
        print("ALPINE model enabled.")

    def plant_palm(self):
        """
        Can be called to enable PALM model outside of constructor
        """
        self.palm = Palm()
        self.PALM_ENABLED = True
        print("PALM model enabled.")

    def plant_maple(self, labels):
        """
        Can be called to enable MAPLE model outside of constructor
        """
        self.maple = Maple(labels)
        self.MAPLE_ENABLED = True
        print("MAPLE model enabled.")

    def plant_date(self, labels):
        """
        Can be called to enable DATE model outside of constructor
        """
        self.date = Date(labels)
        self.DATE_ENABLED = True
        print("DATE model enabled.")

    #@profile
    def finalize(self):
        """
        Must be called before models run in order to finalize structures.

        MAPLE and DATE run this implicitly when fit is called.
        ALPINE and PALM are forest search structures and must be finalized/indexed.
        """
        if self.alpine and self.ALPINE_ENABLED:
            self.alpine.fit()
        if self.palm and self.PALM_ENABLED:
            self.palm.fit()
        self.finalized = True

    def fit(self, X_train, y_train):
        """
        Called to train the models which have been selected.

        ALPINE and PALM are online models which do not have a saved weights function yet.
        If MAPLE and DATE are configured to save their outputs and/or the appropriate
        JSON and HD5 files exist, they will load the saved model and weights instead
        of refitting.

        Args:
            X_train: the training data (Pandas dataframe object)
            y_train: the ground truth labels for the training data (maps 1:1) (Pandas df)

        """
        # process labels
        if "label" not in y_train.columns:
            print("ERROR: column 'label' not found in input training data. Aborting.")
            sys.exit()
        labels = y_train["label"].unique()
        enc = OneHotEncoder()
        enc.fit(np.array(y_train["label"]).reshape(-1,1))
        train_labels = enc.transform(np.array(y_train["label"]).reshape(-1,1)).toarray()
        print("Detected the following classes: " + str(labels))

        #configure models
        print("Configuring models...")
        if self.ALPINE_ENABLED:
            self.plant_alpine()
        if self.PALM_ENABLED:
            self.plant_palm()
        if self.MAPLE_ENABLED:
            self.plant_maple(len(labels))
        if self.DATE_ENABLED:
            self.plant_date(len(labels))

        alpineCount = 0
        palmCount = 0
        for label in labels:
            curr = X_train.loc[y_train.loc[y_train["label"] == label].index.tolist()]
            encoded_label = enc.transform([[label]]).toarray()[0]
            if self.ALPINE_ENABLED:
                self.alpine.add_bucket(curr, encoded_label, alpineCount)
                alpineCount += len(curr)
            if self.PALM_ENABLED:
                self.palm.add_bucket(curr, encoded_label, palmCount)
                palmCount += len(curr)

        if self.ALPINE_ENABLED:
            self.alpine.fit()
        if self.PALM_ENABLED:
            self.palm.fit()
        if self.MAPLE_ENABLED:
            self.maple.fit(X_train, train_labels)
        if self.DATE_ENABLED:
            self.date.fit(X_train, train_labels)

    #@profile
    def predict(self, data):
        """
        Called on the testing data to make classifications.

        Args:
            data: the X_test data, usually a Pandas df

        Returns:
            y_pred: A list of results where each result corresponds 1:1 with data input
                    as the most predicted value from the label set. This result is from the
                    aggregate votes of all the enabled models.
        """
        alpine = []
        palm = []
        maple = []
        date = []
        #NOTE: need to add maple and date votes
        y_pred = []

        if self.ALPINE_ENABLED:
            alpine = self.alpine.predict(data)
        if self.PALM_ENABLED:
            palm = self.palm.predict(data)
        if self.MAPLE_ENABLED:
            maple = self.maple.predict(data)
        if self.DATE_ENABLED:
            date = self.date.predict(data)

        for vote_arr in itertools.zip_longest(alpine, palm, maple, date):
            votes = defaultdict()
            #ALPINE
            if vote_arr[0] is not None:
                for bucket in vote_arr[0]:
                    bucket = tuple(bucket)
                    if bucket in votes:
                        votes[bucket] += 1
                    else:
                        votes[bucket] = 1
            #PALM
            if vote_arr[1] is not None:
                for bucket in vote_arr[1]:
                    bucket = tuple(bucket)
                    if bucket in votes:
                        votes[bucket] += 1
                    else:
                        votes[bucket] = 1
            #MAPLE
            if vote_arr[2] is not None:
                pred = vote_arr[2]
                bucket = np.zeros_like(pred)
                bucket[pred.argmax(0)] = 1
                bucket = tuple(bucket)
                if bucket in votes:
                    votes[bucket] += self.maple.my_num_votes
                else:
                    votes[bucket] = 1
            #DATE
            if vote_arr[3] is not None:
                pred = vote_arr[3]
                bucket = np.zeros_like(pred)
                bucket[pred.argmax(0)] = 1
                bucket = tuple(bucket)
                if bucket in votes:
                    votes[bucket] += self.date.my_num_votes
                else:
                    votes[bucket] = 1

            if len(votes) == 0:
                print("ERROR: no votes cast, did you configure a model?")
                sys.exit()
            else:
                y_pred.append(max(votes, key=votes.get))

        return y_pred
