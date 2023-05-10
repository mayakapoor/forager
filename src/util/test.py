from models.forager import Forager
import time
import random
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report,confusion_matrix, ConfusionMatrixDisplay, cohen_kappa_score
from sklearn.preprocessing import OneHotEncoder
import matplotlib.pyplot as plt
import numpy as np
import os

import seaborn as sns
import statistics
from imblearn.under_sampling import RandomUnderSampler

USE_BALANCER     = True
USE_SAVED_MODELS = True
USE_ALPINE       = True
USE_PALM         = False
USE_MAPLE        = True
USE_DATE         = False

TEST_SIZE    = 0.2

def runTrainAndTest(X, y, ALPINE=False, PALM=False, MAPLE=False, DATE=False):
    """
    Testing harness function, for example purposes

    Args:
        X: the data as a pandas dataframe
        y: the labels as a pandas dataframe

    This class uses some global variables.

    USE_BALANCER     = use under-sampling to balance classes (will drop samples so classes are evenly distributed)
    USE_SAVED_MODELS = use a pre-trained model (faster, but you have to train the first time)
    USE_ALPINE       = use the alpine model (T/F)
    USE_PALM         = use the palm model (T/F)
    USE_MAPLE        = use the maple model (T/F)
    USE_DATE         = use the date model (T/F)

    TEST_SIZE    = if using the balancer, percentage of data to test with (80/20, 60/40)

    Using this function will generate classifier statistics, throughput rates, and a confusion matrix
    """
    global USE_SAVED_MODELS
    if not USE_SAVED_MODELS:
        if os.path.exists("models"):
            for file in os.listdir("models/*.h5"):
                try:
                    file_path = os.path.join("models", file)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
            for file in os.listdir("models/*.json"):
                try:
                    file_path = os.path.join("models", file)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

    print("Data count before sampling: " , len(y))
    global USE_BALANCER
    if (USE_BALANCER):
        rus = RandomUnderSampler(random_state=888)
        X, y = rus.fit_resample(X, y)
        print("Data count after sampling: " , len(y))
    else:
        print("(Sampling disabled.)")

    global TEST_SIZE
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=4, stratify=y)
    labels = y_train["label"].unique()

    global USE_ALPINE
    global USE_PALM
    global USE_DATE
    global USE_MAPLE
    forager = Forager(USE_ALPINE, USE_PALM, USE_MAPLE, USE_DATE)

    start = time.time()
    forager.fit(X_train, y_train)
    print("total training time in seconds: " + str(time.time() - start))

    total = 0
    MBs = 0
    for i, row in X_test.iterrows():
        total = total + int(row["length"])
        if total > 1000000:
            MBs += total/1000000
            total = 0
    if MBs == 0:
        MBs = total/1000000
    print("beginning testing phase...")

    classification_time = []
    start = time.time()
    y_pred = forager.predict(X_test)
    enc = OneHotEncoder()
    enc.fit(np.array(y_train["label"]).reshape(-1,1))
    y_pred = enc.inverse_transform(y_pred)
    end = time.time()
    print("ms per classification: " + str((((end-start)/len(y_test))*1000)))
    print("number of test samples: " + str(len(y_test)))
    print("Mb/s: " + str((MBs*8)/(end-start)))
    print("accuracy: " + str(accuracy_score(y_pred, y_test)))
    #print("cohen kappa score: " + str(cohen_kappa_score(y_test, y_pred)))
    print("classification report: \n"+ classification_report(y_test, y_pred))
    cm = confusion_matrix(y_test["label"].tolist(), y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    fig, ax = plt.subplots(figsize=(20, 15))
    disp.plot(ax=ax)
    tick_marks=np.arange(len(labels))
    plt.xticks(tick_marks,labels,rotation=45,fontsize=10)
    plt.yticks(tick_marks,labels,fontsize=10,rotation=0)
    plt.show()
