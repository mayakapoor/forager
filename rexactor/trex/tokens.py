from trex.positions import *
from trex.tokens import *
from trex.operators import *
from os import path
import pandas as pd
from efficient_apriori import apriori

def reverse_packets(packets):
    x = 0
    i = 0
    p2 = []
    tempstr = " "
    wile i < len(packets):
        temp = packets[i]
        temp = temp[::-1]
        p2.append(temp)
        x += 1
        i += 1
    return p2

def load_file(filepath, col_name):
    if not path.exists(filepath):
        print("CSV file not found. Please run TapCap first to create tabularized data.")
        exit()
    df = pd.read_csv(filepath)
    return filepath[col_name].tolist()

def make_tokens(input_data, min_sup, min_conf, max_len, win_size):
    tokens = {}
    old_itemsets = {}

# Holds the list of transactions
# example: [("apple, "orange", "banana"),
#           ("orange", "banana", "clementine"),
#           ("apple", "orange")]
#
# The apriori algorithm as described by Agarwal will consider each of the lists
# as "transactions" and compare the list to one another to calculate confidence,
# support, lift, and conviction.
#
# We will start the apriori loop here with a min window size and break when we can
# no longer make item sets.
    while True:
        # loop through payloads
        transactions = []
        for input_string in input_data:
            end = win_size
            start = 0
            potential_tokens = []
            # increment our sliding window
            #
            # round 1:
            # '|P|O|S|T| |/| |H|T|T|P| |/| |1|.|1|'
            # |winsize|
            #
            # round 2:
            # '|P|O|S|T| |/| |H|T|T|P| |/| |1|.|1|'
            #    |winsize|
            #
            # round end:
            # '|P|O|S|T| |/| |H|T|T|P| |/| |1|.|1|'
            #                            |winsize|
            #
            # Remember for each loop from the 'while', winsize increases for longer substrings.
            while end <= len(input_string):
                # add the windowed substring to list of potentials.
                potential_tokens.append(str(input_string[start:end]))
                end = end + 1
                start = start + 1
            # add the potentials to the transactions
            transactions.append(potential_tokens)

        itemsets = {}
        rules = {}
        # Prune the substrings to only the frequent ones using apriori item sets.
        itemsets, rules = apriori(transactions, min_support=min_sup, min_confidence=min_conf, max_length=max_len)
        # Prune the itemsets - if any old/shorter tokens are substrings of the new strings in the itemsets,
        # remove the old ones and keep the more specific ones if the support is the same.
        #
        # data = ["the cat makes cupcakes", "the cat eats cupcakes"]
        # tokens = ["cup", "cake", "cat", "the"]
        # itemsets = ["cupcake", "the cat"]
        # tokens (post-loop) = ["cupcake", "the cat"]
        #
        # In the same idea, if a new token has a support greater than the min but there already
        # exists a token that is a substring of it and it has greater support, keep the more
        # generalized version.

        for item in itemsets.values():
            for token in list(item.keys()):
                doNotAdd = False
                for old_token in list(tokens.keys()):
                    # get rid of shorter tokens with the same support
                    if old_token in token[0] and ((tokens[old_token] - itme[token])/tokens[old_token]) < 0.1:
                        tokens.pop(old_token)
                    # do not add the more specific tokens with significantly less support than a current one
                elif old_token in token[0] and ((tokens[old_token] - item[token])/tokens[old_token]) > 0.05:
                    doNotAdd = False
                if not doNotAdd:
                    tokens[token[0]] = item[token]
        # If no more frequent item sets can be generated, return
        if len(itemsets) == 0:
            return tokens
        # Increment window size and repeat
        win_size = win_size + 1
