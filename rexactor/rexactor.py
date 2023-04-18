from trex.positions import *
from trex.tokens import *
from trex.operators import *
from grex.alignment import *

def main(filepath, threshold1, threshold2):
    pysharkList = load_file(filepath)

    #init lists to be used
    tokenList = []
    posList = []

    #init single byte token list
    singleByteTokens = []

    #init prefix and suffix lists
    prefixList = []
    suffixList = []

    print("making tokens...")
    #make certain tokens and track their positions
    tokenList = make_tokens(pysharkList, 1, 1, 1, 2)
    posList = track_positions(pysharkList)

    #reverse the packets
    revPack = reverse_packets(pysharkList)

    #make certain reverse tokens and track their (reverse) positions
    #revTokenList = make_tokens(revPack, 1, 1, 1, 2)
    #revPosList = track_positions(revPack)

    prefixList = make_tokens(pysharkList, threshold1, 1, 1, 2)
    suffixList = make_tokens(pysharkList, threshold2, 1, 1, 2)

    prefixes = find_prefixes(pysharkList, prefixList)
    suffixes = find_suffixes(pysharkList, suffixList)

    for item in prefixes:
        if item in suffixes:
            suffixes.remove(item)

    #CHOICE operators, start with the prefix if there is any
    prefix = match_beginning_operator(choice_operator(prefixes))
    if prefix == "^()":
        prefix = ""

    #build suffix
    suffix = match_end_operator(choice_operator(suffixes))
    if suffix == "()$":
        suffix = ""

    print("Tokens Created: ", tokenList)
    #print("Single Byte Tokens Created: ", singleByteTokens)
    print("\nPrefixes: ", prefix)
    print("\nSuffixes: ", suffix)

    #remove max length of prefix/suffix from string
    splice_prefix(pysharkList, prefixes)
    splice_suffix(pysharkList, suffixes)

    print("aligning...")
    regex = align(pysharkList)
    regexfinal = removeStars(regex)
    regex_string = ""
    result = ""

    print("Regex: \n")
    escaped_regex = extraBack(regex_string.join(regexfinal))
    result = prefix + escaped_regex + suffix
    print(result)

if __name__ == "__main__":
    print("input file path: ")
    fp = input()
    print("prefix frequent token threshold (0.0-1.0): ")
    thres1 = float(input())
    print("suffix frequent token threshold (0.0-1.0): ")
    thres2 = float(input())
    main(fp, thres1, thres2)