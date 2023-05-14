import argparse
import sys
import os
import pylibmagic
import magic
import pickle
import numpy as np
from pick import pick
from pandas import read_csv, concat, DataFrame
from sklearn.preprocessing import OneHotEncoder
import models.alpine as ALPINE
import models.palm as PALM
import models.maple as MAPLE
import models.date as DATE

import rexactor
import tapcap

root_cache = "cache"
alpine_cache = root_cache + "/alpine"
palm_cache = root_cache + "/palm"
maple_cache = root_cache + "/maple"
date_cache = root_cache + "/date"
results_cache = root_cache + "/results"
alpine_bin = alpine_cache + "/alpine.bin"
alpine_labels = alpine_cache + "/labels.txt"
palm_bin = palm_cache + "/palm.bin"
palm_labels = palm_cache + "/labels.txt"
maple_h5 = maple_cache + "/maple.h5"
maple_json = maple_cache + "/maple.json"
maple_labels = maple_cache + "/labels.txt"
date_h5 = date_cache + "/date.h5"
date_json = date_cache + "/date.json"
date_labels = date_cache + "/labels.txt"

def vote(voters):
    joined = voters[0]
    for i in range(1, len(voters)-1):
        joined = np.concatenate((joined, voters[i]), axis=1)
    ballot = []
    for votes in joined:
        ballot.append(max(set(votes), key=votes.count))
    return ballot

def main():
    if not os.path.exists(root_cache):
        os.makedirs(root_cache)
    if not os.path.exists(results_cache):
        os.makedirs(results_cache)

    print("Forager: A Network Training Classification Toolkit")
    title = 'Forager: A Network Training Classification Toolkit.\n\t Please choose a task: '
    options = ['tabularize packet data (TaPCAP)',
               'generate regular expression signatures (RExACtor)',
               'configure and train models (ALPINE, PALM, MAPLE, DATE)',
               'classify packets (ALPINE, PALM, MAPLE, DATE)',
               'clear current cache']

    option, index = pick(options, title, indicator='=>', default_index=0)

    if index == 0:
        print("TaPCAP - features will be extracted to tabular format.")
        another = True
        while another:
            filepath = input("PCAP file input path? ")
            while not os.path.isfile(filepath):
                print("File not found.")
                filepath = input("PCAP file input path? ")
            outpath = input("CSV file output path? ")
            while os.path.isfile(outpath):
                print("CSV file already exists, provide another path.")
                outpath = input("CSV file output path? ")
            tapcap.pcap2csv(filepath, outpath)
            ans = input("Process another file (y/n)? ")
            if ans == "y" or ans == "yes" or ans == "YES":
                another = True
            else:
                another = False

    if index == 1:
        print("RExACtor - a regular expression signature will be generated.")
        preThres = float(input("Prefix frequency threshold (0.0 - 1.0)? "))
        sufThres = float(input("Suffix frequency threshold (0.0 - 1.0)? "))
        filepath = input("File input path (PCAP, PCAPNG, or CSV)? ")
        while not os.path.isfile(filepath):
            print("File not found.")
            filepath = input("File input path (PCAP, PCAPNG, or CSV)? ")

        CSVextension = filepath[len(filepath) - 3:].lower()
        PCAPextension = filepath[len(filepath) - 4:].lower()
        PCAPNGextension = filepath[len(filepath) - 6:].lower()

        if PCAPextension == "pcap" or PCAPNGextension == "pcapng":
            tapcap.pcap2csv(filepath, "local.csv")
            filepath = "local.csv"
        elif CSVextension != "csv":
            print("Invalid source file provided. Must be .csv, .pcap, or .pcapng.")
            sys.exit()
        rexactor.main(filepath, preThres, sufThres)

    if index == 2:
        print("Entering training mode...")
        cont = input("WARNING: editing a model's configuration will override its current cache and settings. Continue (y/n)? ")
        if cont == "n" or cont == "N":
            sys.exit()

        title = 'Forager: A Network Training Classification Toolkit.\nPlease choose one or more models to train (press SPACE to mark, ENTER to continue): '
        options = ['ALPINE',
                   'PALM',
                   'MAPLE',
                   'DATE']
        selected = pick(options, title, indicator='=>', multiselect=True, min_selection_count=1)
        indexes = [i[1] for i in selected]

        if len(indexes) == 0:
            print("configuration failed - user must select at least one model.")
            sys.exit()

        another = True
        colnames=["frame_number", "time", "highest_protocol", "l4_protocol", "text", "src_ip", "src_port", "dst_ip", "dst_port", "len", "ipflags", "tos", "bytes"]
        all_colnames = ["label"] + colnames
        all_dfs = DataFrame(columns=all_colnames)
        labels = []

        while another:
            filepath = input("CSV file input path? ")
            while not os.path.isfile(filepath):
                print("File not found.")
                filepath = input("CSV file input path? ")

            label = input("Label? ")
            while label == "":
                print("No label provided.")
                label = input("Label? ")
            if label not in labels:
                labels.append(label)

            df = read_csv(filepath, delimiter="|", names=colnames, header=None)
            df['label'] = label
            all_dfs = concat([all_dfs, df])

            another_text = input("Add another file (y/n)? ")
            if another_text == "n" or another_text == "N" or another_text == "":
                another = False

        enc = OneHotEncoder()
        enc.fit(np.array(all_dfs["label"]).reshape(-1,1))
        train_labels = enc.transform(np.array(all_dfs["label"]).reshape(-1,1)).toarray()
        labels = sorted(labels)

        alpineCount = [0]
        palmCount = [0]
        mapleCount = [0]
        dateCount = [0]

        #todo: pull in the models
        if 0 in indexes:
            alpine = ALPINE.Alpine(columns=["src_ip", "src_port", "dst_ip", "dst_port", "len", "ipflags", "tos"])
            for label in labels:
                print("Adding data for label: " + label)
                curr = all_dfs.loc[all_dfs['label'] == label]
                if (curr.empty):
                    print("No data provided for label: " + label + ". Skipping this one.")
                alpine.add_bucket(curr, label, alpineCount)
                print("Generated " + str(alpineCount) + " total signatures.")
            alpine.fit()

            if not os.path.exists(alpine_cache):
                os.makedirs(alpine_cache)
            binary_file = open(alpine_bin, mode='wb+')
            pickle.dump(alpine, binary_file)
            binary_file.close()
            label_file = open(alpine_labels,'w+')
            newline = ""
            for label in labels:
                label_file.write(newline + label)
                newline = "\n"
            label_file.close()

        if 1 in indexes:
            print("training PALM...")
            palm = PALM.Palm(col_name="text")
            for label in labels:
                print("Adding data for label: " + label)
                curr = all_dfs.loc[all_dfs['label'] == label]
                palm.add_bucket(curr, label, palmCount)
                print("Generated " + str(palmCount) + " total signatures.")
            palm.fit()

            if not os.path.exists(palm_cache):
                os.makedirs(palm_cache)
            binary_file = open(palm_bin, mode='wb+')
            pickle.dump(palm, binary_file)
            label_file = open(palm_labels,'w+')
            newline = ""
            for label in labels:
                label_file.write(newline + label)
                newline = "\n"
            label_file.close()

        if 2 in indexes:
            print("training MAPLE...")
            if not os.path.exists(maple_cache):
                os.makedirs(maple_cache)
            maple = MAPLE.Maple(labels, weights_path=maple_h5, json_path=maple_json, col_name="bytes", epochs=10)
            maple.fit(all_dfs, train_labels)
            label_file = open(maple_labels,'w+')
            newline = ""
            for label in labels:
                label_file.write(newline + label)
                newline = "\n"
            label_file.close()

        if 3 in indexes:
            print("training DATE...")
            if not os.path.exists(date_cache):
                os.makedirs(date_cache)
            date = DATE.Date(labels, weights_path=date_h5, json_path=date_json, col_name="bytes", epochs=10)
            date.fit(all_dfs, train_labels)
            label_file = open(date_labels,'w+')
            newline = ""
            for label in labels:
                label_file.write(newline + label)
                newline = "\n"
            label_file.close()
        print("Training complete. Models saved to " + root_cache + ".")

    if index == 3:
        print("Entering testing mode...")
        title = 'Forager: A Network Training Classification Toolkit.\nPlease choose one or more models to test with (press SPACE to mark, ENTER to continue): '
        options = ['ALPINE',
                   'PALM',
                   'MAPLE',
                   'DATE']
        selected = pick(options, title, indicator='=>', multiselect=True, min_selection_count=1)
        indexes = [i[1] for i in selected]

        if len(indexes) == 0:
            print("configuration failed - user must select at least one model.")
            sys.exit()

        colnames=["frame_number", "time", "highest_protocol", "l4_protocol", "text", "src_ip", "src_port", "dst_ip", "dst_port", "len", "ipflags", "tos", "bytes"]
        all_colnames = ["label"] + colnames
        all_dfs = DataFrame(columns=all_colnames)
        filepath = ""

        filepath = input("CSV file input path? ")
        while not os.path.isfile(filepath):
            print("File not found.")
            filepath = input("CSV file input path? ")

        path_pieces = filepath.split("/")
        outfile = results_cache + "/" + (path_pieces[len(path_pieces)-1])[:-4] + "_results.txt"
        df = read_csv(filepath, delimiter="|", names=colnames, header=None)
        df['label'] = ""
        all_dfs = concat([all_dfs, df])

        votes = []

        if 0 in indexes:
            print("testing ALPINE")
            if not os.path.exists(alpine_bin):
                print("ERROR: ALPINE has no existing model. Please provide training data first.")
            else:
                with open(alpine_bin, mode='rb') as file: # b is important -> binary
                    alpine = pickle.loads(file.read())
                    alpine_results = alpine.predict(all_dfs)
                    votes.append(alpine_results)

        if 1 in indexes:
            print("testing PALM")
            if not os.path.exists(palm_bin):
                print("ERROR: PALM has no existing model. Please provide training data first.")
            else:
                with open(palm_bin, mode='rb') as file: # b is important -> binary
                    palm = pickle.loads(file.read())
                    palm_results = palm.predict(all_dfs)
                    votes.append(palm_results)

        if 2 in indexes:
            print("testing MAPLE")
            if not os.path.exists(maple_h5) or not os.path.exists(maple_json) or not os.path.exists(maple_labels):
                print("ERROR: MAPLE has no existing model. Please provide training data first.")
            else:
                label_file = open(maple_labels, "r")
                labels = label_file.read().split("\n")
                print(labels)
                maple = MAPLE.Maple(labels, col_name="bytes", weights_path=maple_h5, json_path=maple_json, num_votes=10, use_existing=True)
                maple_results = maple.predict(all_dfs)
                votes.append(maple_results)

        if 3 in indexes:
            print("testing DATE")
            if not os.path.exists(date_h5) or not os.path.exists(date_json) or not os.path.exists(date_labels):
                print("ERROR: DATE has no existing model. Please provide training data first.")
            else:
                label_file = open(maple_labels, "r")
                labels = label_file.read().split("\n")
                date = DATE.Date(labels, col_name="bytes", weights_path=date_h5, json_path=date_json, num_votes=10, use_existing=True)
                date_results = date.predict(all_dfs)
                votes.append(date_results)

        results_file = open(outfile, "w+")
        newline = ""
        for vote in ensemble.vote(votes):
            results_file.write(newline + vote)
            newline = "\n"
        print("Results available.")

    if index == 4:
        answer = input("All cache files will be deleted. Proceed (y/n)? ")
        if answer == 'y' or answer == 'Y':
            os.remove(alpine_cache + "/*")
            os.remove(palm_cache + "/*")
            os.remove(maple_cache + "/*")
            os.remove(date_cache + "/*")
            print("Files deleted.")

if __name__ == "__main__":
    main()
