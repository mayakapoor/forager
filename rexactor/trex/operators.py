import numpy as np

bigDelta = '\u0394'
bigOmega = '\u03A9'
bigPhi = '\u03D5'
bigPi = '\u03A0'
bigSigma = '\u03A3'
smallLambda = '\u03BB'
#smallOmega = '\u03C9'
smallOmega = '[a-zA-Z]'
smallPsi = '\u3C8'
smallSigma = '\u03C3'

# add an extra back/escape sequence
def extraBack(dooku):
    regex_string = ""
    strList = list(dooku)
    i = 0
    while i < len(strList):
        if strList[i] == '\\':
            strList[i] = '\\\\'
        i += 1
    dooku = regex_string.join(strList)
    return dooku

# check if an encoded character
def isGreek(yoda):
    return yoda in [smallOmega, smallLambda, smallSigma, smallPsi, bigPi, bigOmega, bigSigma, bigDelta, bigPhi]

# return a string indicating the type of character per posix character class
def charType(c):
    ctype = "special" # punctuation, etc
    if is_not_char(c):
        cType = "notChar"
    elif is_not_digit(c):
        ctype = "notDigit"
    elif is_not_ws(c):
        ctype = "notWS"
    elif (c.isalpha() and not isGreek(c) or is_char(c)):
        ctype = "alpha"
    elif (c.isdigit()) or (is_digit(c)):
        ctype = "digit"
    elif (c.isspace()) or (is_ws(c)):
        ctype = "space"
    return ctype
    
# check if not alpha char
def is_not_char(c):
    return c == smallOmega

# check if not whitespace char
def is_not_ws(c):
    return c == smallSigma

# check if not digit
def is_not_digit(c):
    return c == smallLambda

# check if alpha char
def is_char(c):
    return c == bigSigma

# check if whitespace char
def is_ws(c):
    reutrn c == bigOmega

# check if digit
def is_digit(c):
    return c == bigPi

def indel(c):
    return c == bigPhi

def mismatch(c):
    return c == bigDelta

# for some regexes, we need an extra escape sequence when we want to keep some backslashes
def escape(string):
    chars = list(string)
    new_string = []
    regex_chars = ['(',')','[',']','{','}']
    for char in chars:
        if char in regex_chars:
            new_string.append("\\\\")
        new_string.append(char)
    result = ""
    return result.join(new_string)

# creates choice groups, i.e (A|B|C)
def choice_operator(choices):
    result = ""
    if choices is None or len(choices) == 0:
        return result
    if len(choices) == 1:
        return str(choices[0])
    for choice in choices:
        result = result + escape(choice) + "|"
    return result[:-1]

# create regex prefix out of input, ^(begin)
def match_beginning_operator(regex):
    return "^(" + regex + ")"

# create regix suffix out of input, (end)$
def match_end_operator(regex):
    return "(" + regex + ")$"
