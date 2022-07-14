import numpy

# Base36 constants
ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'
BASE = len(ALPHABET)
LEADER = ALPHABET[0]
FACTOR = numpy.log(BASE) / numpy.log(256) # log(BASE) / log(256), rounded up
iFACTOR = numpy.log(256) / numpy.log(BASE) # log(256) / log(BASE), rounded up

def base36(source):
    if len(source) == 0:
        return ''

    # skip & count leading zeroes
    zeroes = 0
    length = 0
    pbegin = 0
    pend = len(source)
    while pbegin != pend and source[pbegin] == 0:
      pbegin+=1
      zeroes+=1

    # allocate enough space in big-endian base58 representation
    size = int((pend - pbegin) * iFACTOR + 1) >> 0
    b58 = [0] * size
    # process the bytes
    while pbegin != pend:
      carry = source[pbegin]
      # apply "b58 = b58 * 256 + ch"
      i = 0
      it1 = size - 1
      while (carry != 0 or i < length) and (it1 != -1):
        carry += int(256 * b58[it1]) >> 0
        b58[it1] = int(carry % BASE) >> 0
        carry = int(carry / BASE) >> 0
        it1-=1
        i+=1

      if carry != 0:
        raise Exception('Non-zero carry')

      length = i
      pbegin += 1

    # skip leading zeroes in base58 result
    it2 = size - length
    while it2 != size and b58[it2] == 0:
      it2+=1

    # translate the result into a string
    out = ''
    while zeroes > 0:
        out += 0
        zeroes -= 1

    while it2 < size:
        out += ALPHABET[b58[it2]]
        it2+=1

    return 'k' + out
