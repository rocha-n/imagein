import math

# cover image
coverImage = [240, 15, 85, 94, 25, 92, 69, 154, 250, 241, 161, 185, 112, 105, 105, 85, 9, 99, 64, 123, 201, 79, 104, 12,
              100, 97, 118, 49, 206, 111, 190]

# secret stream
secretStream = [int("01001110", 2), int("01100101", 2), int("01101100", 2),
                int("01110011", 2), int("01101111", 2), int("01101110", 2)]


ranges = [range(0, 1), range(1, 3), range(3, 7), range(7, 15), range(15, 31), range(31, 63), range(63, 127),
          range(127, 255)]


# Searches for value d in the ranges list
# Returns the index of list where val is
# If not found, returns -1
def rangeOf(val):
    counter = 0

    for r in ranges:
        if (val in r):
            return counter
        else:
            counter += 1

    # val not found
    return -1


# Returns the width of the list at ranges[r]
def widthOfRange(r):
    return len(ranges[r])


# get nb of bits from the secret string stream s
# returns the decimal value of the taken number of bits
# updates the index of current position bitPos
def getSecretBits(bitPos, nb, s):
    startByte = math.floor(bitPos / 8)
    workSegment = bin(s[startByte])[2:].zfill(8)

    # if we are not on the last byte, retrieve next one
    if startByte < len(s) - 1:
        workSegment = workSegment + bin(s[startByte + 1])[2:].zfill(8)

    bitPos -= 8 * startByte
    secretBits = workSegment[bitPos:bitPos + nb]

    secretVal = int(secretBits, 2)

    return secretVal


def printRange(nb):
    print("Range " + str(nb) + " has a width of " + str(widthOfRange(nb)))


# Inverse calculation function for computing the new g values
def invCalc(g, m, d):
    if d % 2 == 0:
        g1prime = g[0] - math.floor(m / 2)
        g2prime = g[1] + math.ceil(m / 2)
    else:
        g1prime = g[0] - math.ceil(m / 2)
        g2prime = g[1] + math.floor(m / 2)

    return g1prime, g2prime


def verifInvCalc():
    mprime = 10
    msecond = 30
    m = mprime + msecond

    g = [183, 29]

    a = invCalc(g, m, 2)
    b = invCalc(invCalc(g, mprime, 2), msecond, 2)

    if a == b:
        print("Function invCalc check succeeded!")
    else:
        print("Function invCalc check failed!")


# takes a binary string as input
# returns an integer array with its contents
def binStrToIntArray(bstr):
    vals = [int(bstr[i:i+8], 2) for i in range(0, len(bstr), 8)]

    return vals


# Encode the secret stream s in the cover image p
def WuTsaiEncode(p, s):
    # index of the current block being processed
    currBlockIndx = 0

    # index of the current read bit in secret stream s
    bitPos = 0

    while currBlockIndx < len(p) - 1 and bitPos < len(s * 8):
        # delta of the block
        d = p[currBlockIndx + 1] - p[currBlockIndx]

        # range of d
        k = rangeOf(abs(d))

        # number of bits that can be encoded
        n = int(math.log(widthOfRange(k), 2))

        # d' computation
        dprime = ranges[k][0] + getSecretBits(bitPos, n, s)

        if d < 0:
            dprime = dprime * -1

        # new p values
        m = dprime - d

        g = [p[currBlockIndx], p[currBlockIndx + 1]]
        g1prime, g2prime = invCalc(g, m, d)

        # falling-off-boundary checking
        ghat1, ghat2 = invCalc(g, (ranges[k][widthOfRange(k) - 1]) - d, d)

        if (0 <= ghat1 <= 255) and (0 <= ghat2 <= 255):
            p[currBlockIndx] = g1prime
            p[currBlockIndx + 1] = g2prime

            bitPos += n

        # a block is composed of two bytes, so we have to jump 2 by 2
        currBlockIndx += 2

    if bitPos < len(s) * 8:
        print("Cover image too small to hide the secret!")


def WuTsaiDecode(p, secretLength):
    binString = ""
    currBlockIndx = 0
    decSizeDelta = 0

    while currBlockIndx < len(p) - 1 and decSizeDelta <= 0:
        # delta of the block
        dstar = p[currBlockIndx + 1] - p[currBlockIndx]

        # range of d
        k = rangeOf(abs(dstar))

        gstar = [p[currBlockIndx], p[currBlockIndx + 1]]

        ghat1, ghat2 = invCalc(gstar, (ranges[k][widthOfRange(k) - 1]) - dstar, dstar)

        if (0 <= ghat1 <= 255) and (0 <= ghat2 <= 255):  # the block was used to encode data
            if dstar >= 0:
                binVal = str(bin(dstar - ranges[k][0])[2:].zfill(k))
            else:
                binVal = str(bin((-1 * dstar) - ranges[k][0])[2:].zfill(k))

            decSizeDelta = len(binString) + len(binVal) - (secretLength*8)

            if decSizeDelta > 0:
                binVal = binVal[decSizeDelta:
                         ]
            binString += binVal

        # transform the res to a binary representation of length k
        currBlockIndx += 2

    return binStrToIntArray(binString)


print("Encoded values: " + str(secretStream))
WuTsaiEncode(coverImage, secretStream)

print("Decoded values: " + str(WuTsaiDecode(coverImage, len(secretStream))))


