from __future__ import print_function

import numpy as np

pad_marker = {'float': '!', 'complex': '$', 'int': '%'}
pad_desc = {}
for k, v in pad_marker.items():
    pad_desc[v] = k

PADERR_FMT = "wrong PAD format: expected '%s', got '%s'"
PADERR_NPTS = "not enough PAD data to read"

base = 90
basehalf = 45
ioff  = 37
ihuge = 38
huge = 10.**ihuge
tiny = 10.**(-ihuge)
tenth =  0.099999999994
tenlog = 2.302585092994045684


def pad(xreal, npack=8):
    """convert double number *xreal* to packed-ascii-data string"""
    str      = ' '
    xsave    = min(huge, max(-huge, float(xreal)))
    isgn     = 0
    if xsave > 0:
        isgn = 1
    #
    xwork = abs(xsave)
    iexp  = 0
    if  xwork <  huge and xwork >  tiny:
        iexp = 1 + int(np.log(xwork) / tenlog  )
    elif xwork >= huge:
        xwork, iexp  = 1.0, ihuge
    elif xwork <= tiny:
        xwork = 0

    # force xwork between ~0.1 and ~1
    # note: this causes a loss of precision, but
    # allows backward compatibility
    xwork = xwork / (10.0 ** iexp)
    def rescale(val, exp):
        if val > 1.:
            val = val/10.0
            exp += 1
        elif val <= tenth:
            val = 10.0*val
            exp -= 1
        return val, exp
    xwork, iexp = rescale(xwork, iexp)
    while xwork > 1:
        xwork, iexp = rescale(xwork, iexp)

    itmp = int(basehalf * xwork)
    s = [iexp+basehalf, 2*itmp+isgn]
    xwork = xwork * basehalf - itmp
    if npack > 2:
        for i in range(npack-2):
            itmp = int(base * xwork + 1.e-9)
            s.append(itmp)
            xwork = xwork * base - itmp
    # round-off
    if xwork >= 0.5 and s[-1] < 89:
        s[-1] = s[-1] + 1

    s.extend([0, 0])
    s = ''.join([chr(i+ioff) for i in s])
    return s[:npack]

def unpad(stringin, npack=8):
    """convert packed-ascii-data string *str* to double """
    if npack < 0:
        return 0

    dat = [(ord(s) - ioff) for s in stringin]
    iexp = dat[0] - basehalf
    sign = 2*(dat[1] % 2)- 1
    sum  = (dat[1]//2)/(1.0*base*base)
    for i, x in enumerate(reversed(dat[2:])):
        expon = npack - i
        sum += float(x) / (1.0*base)**expon
    return 2 * sign * base * sum * (10 ** iexp)

def read_pad_float(text, npts, npack=8):
    """read flat array from Packed ASCII Data file """
    ipts = 0
    arr = []
    while ipts < npts:
        line = text.pop(0)
        if len(line) < 1:
            break
        line = line.strip()
        if line[0] != pad_marker['float']:
            raise IOError(PADERR_FMT % ('float', pad_desc[line[0]]))
        line = line[1:]
        ndline = int(len(line)/npack)

        if ndline < 1:
            raise IOError(PADERR_NPTS)
        for i in range(ndline):
            ipts += 1
            word = line[npack*i:npack*(i+1)]
            tmp  = unpad(word, npack=npack)
            arr.append(float(tmp))
    return np.array(arr)


def read_pad_complex(text, npts, npack=8):
    """read complex array from Packed ASCII Data file """
    ipts = 0
    arr = []
    while ipts < npts:
        line = text.pop(0)
        if len(line) < 1:
            break
        line = line.strip()
        if line[0] != pad_marker['complex']:
            raise IOError(PADERR_FMT % ('complex', pad_desc[line[0]]))
        line = line[1:]
        ndline = int(len(line)/(2*npack))
        if ndline < 1:
            raise IOError(PADERR_NPTS)

        for i in range(ndline):
            ipts += 1
            word = line[2*npack*i:2*npack*(i+1)]
            fval = unpad(word[:npack], npack=npack)
            ival = unpad(word[npack:], npack=npack)
            arr.append(complex(fval, ival))
    return np.array(arr)

def test_pad(fname='pad_test.dat', npack=8):
    with open(fname, 'r') as fh:
        text = fh.readlines()
    for line in text:
        words = line[:-1].split()
        for word in words:
            f1 = float(word)
            s1 = pad(f1, npack=npack)
            f2 = unpad(s1, npack=npack)
            print(" %s : %24.13g : %24.13g" % (s1, f1, f2))

def test1():
    vals = (8.2, 1.0, 0.0, 1.000002, 1.0000002)
    for f1 in vals:
        s1 = pad(f1)
        f2 = unpad(s1)
        print("Pad: ", s1, f1, f2) # , (f2-f1)/abs(f2))

def test2():
    vals = ('R49ofS<~', 'R49ofS=%')
    for s in vals:
        f = unpad(s)
        print("Unpad: %s %24.14g" % (s, f))

def test3():
    vals = (2.e-4, 2.e-5, 3.e-6, 4.e-7)
    for f in vals:
        s = pad(f)
        f2 = unpad(s)
        print("pad: %s %24.14g > %24.14g" % (s, f, f2))

def test4():
    arr = [0.00130899469853, 0.311608637586, 0.578472395516, 0.0654171933241,
           0.0114944432599, 0.274034105638, 0.915081518472, 0.546331628633]
    fh = open('b.pad', 'r')
    text = fh.readlines()
    ax = read_pad_float(text, 8)
    for i in range(8):
        print(i, arr[i], ax[i], (arr[i]-ax[i])/max(arr[i], 1.e-12))


def test5():
    arr = [0.00130899469853 + 0.311608637586J,
           0.578472395516 + 0.0654171933241j,
           0.0114944432599 + 0.274034105638j,
           0.915081518472 +  0.546331628633j]
    fh = open('c.pad', 'r')
    text = fh.readlines()
    ax = read_pad_complex(text, 4)
    for i in range(4):
        print(i, arr[i], ax[i], (arr[i]-ax[i])/max(abs(arr[i]), 1.e-12))


    print(" Remaining text: ", text)

# test_pad()
# test1()

test4()
test5()
