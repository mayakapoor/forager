from collections import OrderedDict

# Returns a list of dictionaries where each entry represents the character and
# frequency of that character across all packets at that index. We use this to
# find single byte tokens and character ranges.

def track_positions(input_data):
    # keep track of list size
    last_index = 0
    positions = []
    class_frequencies = []
    num_inputs = len(input_data)

    # loop through all the inputs
    for input_string in input_data:
        curr_index = 0

        for input_char in input_string:
            # if this is the longest string we've had yet, add a dictionary
            if (curr_index >= last_index):
                last_index = curr_index
                position_dictionary = {}
                position_dictionary[input_char] = 1
                positions.append(position_dictionary)
            # else, check if we have seen this char or not in the dictionary
            else:
                # increment if seen
                if input_char in positions[curr_index]:
                    positions[curr_index][input_char] = positions[curr_index][input_char] + 1
                # else make a dictionary for it
                else:
                    positions[curr_index][input_char] = 1
            curr_index = curr_index + 1

    single_byte_tokens = {}
    # convert counts to frequencies
    for i in range (len(positions) - 1):
        for key in list(positions[i].keys()):
            positions[i][key] = positions[i][key]/num_inputs
            # if frequency == 1.0, single byte token
            if positions[i][key] == 1:
                single_byte_tokens[key] = i

    return positions, single_byte_tokens

# Takes a list of tokens and data as input and returns a list of dictionaries
# where the token position in the input string corresponds to the beginning of where
# it is found. ex: [{'POST': 0, 'HTTP/': 7}, {'POST': 0, 'HTTP/': 7}, {'HTTP/': 17}, {'HTTP/': 22}]
def track_token_positions(input_data, tokens):
    positions = []
    # loop through the inputs
    for input_string in input_data:
        position_dictionary = OrderedDict()
        # loop through the tokens
        for token in tokens:
            if token in input_string:
                position_dictionary[input_string.index(token)] = token;
        positions.append(position_dictionary);
    return positions

# return a list of tokens which are positionally found at the beginning, i.e. prefix
def find_prefixes(input_data, tokens):
    positions = track_token_positions(input_data, tokens)
    prefixes = {}
    for dictionary in positions:
        if 0 not in dictionary.keys():
            continue
        prefixes[dictionary[0]] = 1
    return list(prefixes.keys())

    # We may want to count prefixes which cover a vast majority of cases instead of all,
    # so this code allows a noise threshold.
    count = 0
    empty_list = []
    for prefix in prefixes:
        count += tokens[prefix]
        if (len(input_data) - count)/len(input_data) > 0.01:
            return empty_list
        else:
            return list(prefixes.keys())

# return a list of tokens which are positionally found at the end, i.e. suffix
def find_suffixes(input_data, tokens):
    reverse_input = []
    reverse_tokens = {}
    for item in input_data:
        reverse_input.append(item[::-1])
    for token in tokens:
        reverse_tokens[token[::-1]] = tokens[token]
    reversed_result = find_prefixes(reverse_input, reverse_tokens)
    result = []
    for item in reversed_result:
        result.append(item[::-1])
    return result

# remove the found prefix from the input data. If we don't do this, alignment
# fixates on the prefix.
def splice_prefix(input_data, prefixes):
    for i in range(len(input_data)):
        for prefix in prefixes:
            if prefix in input_data[i]:
                input_data[i] = input_data[i][len(prefix):]

# remove the found suffix from the input data. If we don't do this, alignment
# fixates on the suffix.
def splice_suffix(input_data, suffixes):
    for i in range(len(input_data)):
        for suffix in suffixes:
            if suffix in input_data[i]:
                input_data[i] = input_data[i][:len(input_data[i]) - len(suffix)]
