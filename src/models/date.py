from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import LabelEncoder
from keras.wrappers.scikit_learn import KerasClassifier
from keras.utils import np_utils
from keras.models import model_from_json
from collections import Counter
from itertools import islice
from datasketch import MinHash
from multiprocessing import Pool, cpu_count

import numpy as np
import copy
import math
import os
import pandas as pd
import matplotlib.pyplot as plt
import keras
import tensorflow as tf


class Date():

    def __init__(self, labels, num_votes=1, col_name="payload", epochs=50, batch_size=100, weights_path='cache/date/date.h5', json_path='cache/date/date.json', use_existing=False):
        """
        Generates 3D Point Clouds and performs DBSCAN.
        """
        self.my_num_votes = num_votes
        self.weights_path = weights_path
        self.json_path = json_path
        self.col_name = col_name
        self.epochs = epochs
        self.batch_size = batch_size
        self.labels = labels
        self.use_existing = use_existing

        def initModel():
            """
            Builds the classifier model which takes the 5 statistical features derived from DBSCAN.

            This function will save the weights and model as HD5 and JSON, respectively.
            These files can be used to re-load the model and save training time.
            """
            model = keras.Sequential([
                keras.layers.Dense(5, activation=tf.nn.relu),  ## two layers of processing nodes and one node for the output (binary)
                keras.layers.Dense(5, activation=tf.nn.relu),
                keras.layers.Dense(len(self.labels), activation=tf.nn.softmax),  ## ????? labels used to just be 1
            ])
            return model

        if self.use_existing and (os.path.exists(self.weights_path) and os.path.exists(self.json_path)):
            json_file = open(self.json_path, 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            model = model_from_json(loaded_model_json)
            model.load_weights(self.weights_path)
            self.nn = model
        else:
            model = initModel()
            model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['acc',keras.metrics.Precision(),keras.metrics.Recall()])
            self.nn = model

        # loss = binary_crossentrophy
        # not sure if this will work

    def save_weights(self, path=""):
        """
        Save the weights of the trained model

            Args:
                path: a path to save the weights to, optional
        """
        if (path == ""):
            path = self.weights_path
        self.cnn.save_weights(path)

    def delete_weights(self):
        """
        Delete the cached weights from previous training
        """
        os.remove(self.weights_path)

    def fit(self, data, label): ## train the data against the label.
    ####################################################################################################3
        """
        Train the model with provided data. If saved weights/JSON is found, will skip this step and use the saved values instead.

        Args:
            data: the training data, X_train (Pandas dataframe)
            label: the training labels, y_train (Pandas dataframe)
        """

        label = label[data[self.col_name].isna() == False]
        y = np.array(label)
        # retrieving data from file.
        pays = data[data[self.col_name].isna() == False][self.col_name]
        X = Date.cloudify(pays)
        X = np.asarray(X).astype(np.float32)

        self.nn.fit(X, y, epochs = self.epochs, batch_size = self.batch_size)  ## 20 was preferred on. TODO update this.
        self.nn.save_weights(self.weights_path)
        model_json = self.nn.to_json()
        with open(self.json_path, "w") as json_file:
            json_file.write(model_json)
        self.nn.summary()

    def cloudify(data):
        """
            Transform the provided data into a series of 3D point clouds, performs DBSCAN, and returns the 5 statistical features per sample

            clusterCount: number of clusters
            averageClusterSize: average size of db cluster
            standardDeviation: standard deviation of points from center
            noisePercent: percent of noise in the cloud, indicates uniformity
            totalSize: total size of the cloud

            Args:
                data: the input data, Pandas dataframe

            Returns:
                a Pandas data frame where each row corresponds 1:1 with sample, contains 5 stat features.
        """
        resultTable = pd.DataFrame(columns = ['clusterCount', 'averageClusterSize', 'standardDeviation', 'noisePercent', 'totalSize'])
        results = []
        with Pool(cpu_count()) as p:
            results = pd.DataFrame(p.map(Date.cloudgen, [str(entry) for entry in data]),
                columns = ['clusterCount', 'averageClusterSize', 'standardDeviation', 'noisePercent', 'totalSize'])

        resultTable = pd.concat([resultTable, results])
        return resultTable


    def cloudgen(entry):
        """
            Helper function for cloudify, makes 3D points from packet bytes, then performs DBSCAN.

            Args:
                entry: a single payload of a packet

            Returns:
                a list of the five statistical features (see cloudify)
        """

        window_size = 3
        tokens = []
        newTokens = []
        payloadCloud = np.array([[0,0,0]])
        payloadData = bytes(entry, 'utf-8')

        clusterCount = 0
        averageClusterSize = 0
        standardDeviation = 0
        noisePercent = 0
        totalSize = 0

        x = 0
        numPoints = 0
        for i in range(len(payloadData) - window_size + 1):
            tempList = [0,0,0]
            for element in (payloadData[i: i + window_size]):
                tempList[x] = (element)
                x = x + 1
                if(x == 3):
                    x = 0
                    payloadCloud = np.vstack((payloadCloud,np.array(tempList)))
                    numPoints = numPoints + 1  ## keep track of number of points in the cloud

        payloadCloud = np.delete(payloadCloud, (0), axis = 0)
        if(len(payloadCloud) == 0):
            return [clusterCount, averageClusterSize, standardDeviation, noisePercent, totalSize]

        clustering = DBSCAN(eps=7, min_samples=7)
        finalCloud = clustering.fit(payloadCloud)


        cloudLabels = finalCloud.labels_
        cloudLabelsCounter = Counter(finalCloud.labels_)
        #print((cloudLabelsCounter))
        trueLen = 0
        trueSize = 0
        totalSize = 0
        averageClusterSize = 0.0
        #uniqueClouds = set(finalCloud.labels_)

        clusterCount = len(cloudLabelsCounter)
        noiseCount = (cloudLabelsCounter[-1])
        entryCount = len(cloudLabels)

        #print(cloudLabelsCounter)
        for element in cloudLabelsCounter:
            if(element != -1):
                trueLen = trueLen + 1
                trueSize = totalSize + cloudLabelsCounter[element]
            totalSize = totalSize + cloudLabelsCounter[element]
        #print(uniqueClouds)

        if(trueLen > 0):
            averageClusterSize = trueSize / (trueLen)  ## ignores outliers
        else:
            averageClusterSize = 0.0
        if(totalSize > 0):
            noisePercent = noiseCount / totalSize     ## gives percent of cloud that is just noise
        else:
            noisePercent = 0.0

        ## standard deviation calculation below

        size = 0
        xminusmu = 0.0
        summation = 0.0
        standardDeviation = 0.0

        if(averageClusterSize > 0.0):
            for element in cloudLabelsCounter:
                size = cloudLabelsCounter[element]
                xminusmu = (abs(size - averageClusterSize))**2
                summation = summation + xminusmu
            standardDeviation = math.sqrt(summation / entryCount)
        else:
            standardDeviation = 0.0
        return [clusterCount, averageClusterSize, standardDeviation, noisePercent, totalSize]

    def set_votes(self, num):
        """
        Sets the number of votes for the DATE model, so you can weight it more or less in an ensemble

        Args:
            num: the number of votes to set
        """
        self.my_num_votes = num

    def predict(self,data):
        """
        Return a prediction for each entry based on the training model.

        Args:
            data: X_test, a Pandas dataframe of the data entry

        Return:
            the predicted result for each data entry
        """
        pays = data[self.col_name]
        X = Date.cloudify(pays)
        X = np.asarray(X).astype(np.float32)
        all_pred = self.nn.predict(np.array(X))
        all_results = []
        for pred in all_pred:
            result = np.zeros_like(pred)
            result[pred.argmax(0)] = 1
            result = list(result)
            all_results.append(result)
        index_results = np.argmax(all_results, axis=1)
        final = []
        for i in index_results:
            final.append([self.labels[i]] * self.my_num_votes)
        return final
