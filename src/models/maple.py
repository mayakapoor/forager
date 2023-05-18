import tensorflow as tf
from tensorflow import keras
import numpy
import glob
import os
import util.payload
import sklearn
from sklearn.model_selection import train_test_split
from keras.models import model_from_json
import numpy as np

class Maple:
    def __init__(self, labels, num_votes=1, col_name="payload", epochs=50, batch_size=100, weights_path='cache/maple/maple.h5', json_path='cache/maple/maple.json', use_existing=False):
        """
        Generates 2D matrix images and classifies using CNN.
        """
        self.my_num_votes = num_votes
        self.weights_path = weights_path
        self.json_path = json_path
        self.col_name = col_name
        self.epochs = epochs
        self.batch_size = batch_size
        self.labels = labels
        self.use_existing = use_existing

        def make_model(inputSize):
            """
            Builds the classifier model.

            Args:
                inputSize: the number of features, typically the number of pixels of image.

            This function will save the weights and model as HD5 and JSON, respectively.
            These files can be used to re-load the model and save training time.
            """
            inputs = keras.Input(inputSize)
            conv1 = keras.layers.Conv2D(32,(3,3),padding = 'same', activation = 'relu')(inputs)
            add1 = tf.pad(inputs, tf.constant([[0,0],[0,0],[0,0],[0,31]]),'CONSTANT')
            res1 = keras.layers.Add()([conv1,add1])
            conv2 = keras.layers.Conv2D(32,(3,3),strides=2,padding = 'same', activation = 'relu')(res1)
            add2 = keras.layers.MaxPooling2D(2)(res1)
            res2 = keras.layers.Add()([conv2,add2])
            conv3 = keras.layers.Conv2D(64,(3,3),padding = 'same',activation = 'relu')(res2)
            flatten = keras.layers.Flatten()(conv3)
            dense1 = keras.layers.Dense(64, activation = 'relu')(flatten)
            drop = keras.layers.Dropout(.2)(dense1)
            dense2 = keras.layers.Dense(32, activation = 'relu')(drop)
            drop2 = keras.layers.Dropout(.2)(dense2)
            output = keras.layers.Dense(len(self.labels), activation = 'softmax')(drop2)
            maple = keras.Model(inputs,output)
            return maple

        if (self.use_existing and os.path.exists(self.weights_path) and os.path.exists(self.json_path)):
            json_file = open(self.json_path, 'r')
            loaded_model_json = json_file.read()
            json_file.close()
            maple = model_from_json(loaded_model_json)
            maple.load_weights(self.weights_path)
            print("Using existing model at " + str(self.json_path) + ".")
            self.cnn = maple
        else:
            maple = make_model((28,28,1))
            maple.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['acc',keras.metrics.Precision(),keras.metrics.Recall()])
            self.cnn = maple

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

    def fit(self, data, label):
        pays = data[data[self.col_name].isna() == False][self.col_name]
        label = label[data[self.col_name].isna() == False]
        pays =  list(map(lambda pay: list(map(lambda c: int(ord(c)),list(pay))), pays))
        X = []
        if len(pays) == 0:
            pays = [[0]]
        for pay in pays:
            if len(pay) < 784:
                pads = 784 - len(pay)
                pad = [0 for i in range(pads)]
                #adding 0's to the end so we can reshape it
                mat = pay + pad
            elif len(pay) > 784:
                #trimming if more bytes than needed
                mat = pay[:784]
            mat = np.reshape(mat,(28,28))
            X.append(mat)

        self.cnn.fit(np.array(X), np.array(label), epochs = self.epochs, batch_size = self.batch_size)
        self.cnn.save_weights(self.weights_path)
        model_json = self.cnn.to_json()
        with open(self.json_path, "w") as json_file:
            json_file.write(model_json)
        self.cnn.summary()

    def predict(self, data):
        """
        Return a prediction for each entry based on the training model.

        Args:
            data: X_test, a Pandas dataframe of the data entry

        Return:
            the predicted result for each data entry
        """
        data[self.col_name] = data[self.col_name].fillna(' ')
        pays = data[self.col_name]
        #pays = data[data['payload'].isna() == False]['payload']
        #makeing payloads form string to ints
        pays = list(map(lambda pay: list(map(lambda c: int(ord(c)),list(pay))), pays))
        X = []
        if len(pays) == 0:
            pays = [[0]]
        for pay in pays:
            if len(pay) < 784:
                pads = 784 - len(pay)
                pad = [0 for i in range(pads)]
                #adding 0's to the end so we can reshape it
                mat = pay + pad
            elif len(pay) > 784:
                #trimming if more bytes than needed
                mat = pay[:784]
            mat = np.reshape(mat,(28,28))
            X.append(mat)
        all_pred = self.cnn.predict(np.array(X))
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
