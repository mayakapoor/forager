from rexactor.operators import *
from rexactor.grex.needlemanwunsch import *

# not digit
def exception1(dig):
    return not (is_not_char(dig) or is_not_ws(dig))

# not alpha
def exception2(alp):
    return not (is_not_ws(alp) or is_not_digit(alp))

# not whitespace
def exception3(ws):
    return not (is_not_char(ws) or is_not_digit(ws))

# replace matching character classes with Greek symbols
def encode(seqA, seqB):
    encoded_sequence = []
    for i in range(min(len(seqA), len(seqB))):
        typeA = char_type(seqA[i])
        typeB = char_type(seqB[i])

        if seqB[i] == smallPsi or seqA[i] == smallPsi: # NW gaps
            encoded_sequence.append(bigPhi)

        elif seqA[i] == bigPhi or seqB[i] == bigPhi:
            encoded_sequence.append(bigPhi)

        else:
            if typeA == typeB:
                if typeA == "alpha":
                    encoded_sequence.append(bigSigma)
                elif typeA == "digit":
                    encoded_sequence.append(bigPi)
                elif typeA == "space":
                    encoded_sequence.append(bigOmega)

            else:
                if (typeA != "alpha" and typeB != "alpha" and exception2(seqA[i]) and exception2(seqB[i])) or (typeA == "notChar" and typeB == "notChar"):
                    encoded_sequence.append(smallOmega) # not char
                elif (typeA != "digit" and typeB != "digit" and exception1(seqA[i]) and exception1(seqB[i])) or (typeA == "notDigit" and typeB == "notDigit"):
                    encoded_sequence.append(smallLambda) # not digit
                elif (typeA != "space" and typeB != "space" and exception3(seqA[i]) and exception3(seqB[i])) or (typeA == "notWS" and typeB == "notWS"):
                    encoded_sequence.append(smallSigma) # not whitespace
                else:
                    encoded_sequence.append(bigDelta)

    if (len(seqA) != len(seqB)):
        encoded_sequence += "".join([bigPhi * ((max(len(seqA), len(seqB))) - len(encoded_sequence))])
    return encoded_sequence

# replace symbols with regex classes
def replace(result):
    t = []
    f = []
    indexr = 0
    indext = 0
    indexf = 0

    while indexr < len(result):
        t.append(result[indexr])
        indexr += 1
        if indexr < len(result):
            f.append(t)
            t = [] # erase t
            indext = 0
            indexf += 1

    g = []
    i = 0
    while i < len(f):
        if indel(f[i][0]): #Phi
            phicount = 0
            while i < len(f) and indel(f[i][0]):
                phicount = phicount + 1
                i = i + 1
            g.append('.{0,' + str(phicount) + '}') # Single Phi
        elif mismatch(f[i][0]): # Delta
            if len(f[i]) > 1:
                g.append('.' + str(len(f[i])) + '}') # Multiple Delta
                appendlen = len(str(len(f[i])))
                a = 0
                while a < appendlen:
                    a += 1
            else:
                g.append('.') # Single Delta

        elif (f[i][0] == bigSigma): # alpha class type
            x = 0
            g.append(alphaChar(len(f[i])))
        elif (f[i][0] == bigPi): # digit class type
            g.append(digitChar(len(f[i])))
        elif(f[i][0] == bigOmega): # whitespace class type
            g.append(whitespaceChar(len(f[i])))
        elif(f[i][0] == smallOmega): # not alpha class type
            g.append(notAlphaChar(len(f[i])))
        elif(f[i][0] == smallLambda): # not digit class type
            g.append(notDigitChar(len(f[i])))
        elif(f[i][0] == smallSigma):
            g.append(notWhitespaceChar(len(f[i]))) # not whitespace class type
        elif(isSpecial(f[i][0])):
            x = 0
            spec = f[i][0]
            while x < len(f[i]):
                if spec != '.':
                    specstr = '\\' + spec
                else:
                    spectr = spec
                g.append(specstr)
                x += 1
        else:
            g.append(exactChar(f[i][0], len(f[i])))
        i += 1
    return g

# pairwise substring alignment
def align(passedList):
    result = passedList[0]
    for i in range(1, len(passedList)):
        continueAlignment = False
        for c in result:
            if c != bigPhi:
                continueAlignment = True
        if continueAlignment:
            a,b = NW(result, passedList[i])
            result = encode(a,b)
        else:
            result = [bigPhi * max(len(result), len(passedList[i]))]
    regex = replace(result)
    return regex
