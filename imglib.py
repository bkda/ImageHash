#!/usr/bin/env python3
# coding=UTF-8
'''
    Created by Tracy on 2016/8/2
    Mail tracyliubai@gmail.com
'''

from functools import reduce
from PIL import Image

SL = [0, 1, 2, 3, 10, 11, 12, 13, 20, 21, 22, 23, 30, 31, 32, 33, 100, 101, 102, 103, 110, 111, 112, 113, 120, 121, 122,
      123, 130, 131, 132, 133, 200, 201, 202, 203, 210, 211, 212, 213, 220, 221, 222, 223, 230, 231, 232, 233, 300, 301,
      302, 303, 310, 311, 312, 313, 320, 321, 322, 323, 330, 331, 332, 333]


def averageHash(img, size=8):
    '''
    :param img: img file
    1.  resize the image to 8 x 8 with ANTIALIAS and convert to grayscale  ('L')
    2.  calculate the average of 64 grayscales
    3.  compare the 64 grayscales to the average if greater than avg get 1 else get 0
    4   convert binary to hex using shift operator
    :return: hash value
    '''
    if not isinstance(img, Image.Image):
        img = Image.open(img)
    im = img.resize((size, size), Image.ANTIALIAS).convert('L')

    avg = reduce(lambda x, y: x + y, im.getdata()) / (size * size)
    binary_list = [0 if i < avg else 1 for i in im.getdata()]

    hs = reduce(lambda x, y_z: x | (y_z[1] << y_z[0]), enumerate(binary_list), 0)
    hh = hex(hs)[2:]
    # print(img, '{: >30}  {: <20}'.format(hs, hh))
    return hs


def colorHistogram(img, size=8):
    '''
    :param img:
    :return:  64-dimensional vector to calculate cosine similarity
    '''
    if not isinstance(img, Image.Image):
        img = Image.open(img)

    pixels = list(img.getdata())
    c = [i[0] // (size * size) * 100 + i[1] // (size * size) * 10 + i[2] // (size * size) for i in pixels]
    return [c.count(i) for i in SL]


def dct_coefficients(data, upper_left=8):
    '''
    :param data:
    :param upper_left: use upper left corner
    :return:
    '''
    from math import cos, pi, sqrt

    A, M, N = [], 32, 32
    coefficients = []
    for i in range(32):
        A.append([data.pop(0) for j in range(32)])

    for p in range(upper_left):
        tmp = []
        alpha_p = sqrt(1 / M)
        if p != 0:
            alpha_p = alpha_p * sqrt(2)
        for q in range(upper_left):
            alpha_q = sqrt(1 / N)
            if q != 0:
                alpha_q = alpha_q * sqrt(2)
            b = sum(
                [A[m][n] * cos(pi * (2 * m + 1) * p / 2 / M) * cos(pi * (2 * n + 1) * q / 2 / N) for m in range(M)
                 for n
                 in range(N)])

            tmp.append(alpha_p * alpha_q * b)
        coefficients.append(tmp)
    return coefficients


def perceptiveHash(img):
    '''
    :param img:
    :return: the upper left corner of the DCT,default return 8x8 coefficient matrix
              It can reduce the computational time efficiently.
    '''

    if not isinstance(img, Image.Image):
        img = Image.open(img)
    im = img.resize((32, 32), Image.ANTIALIAS).convert('L')
    da = list(im.getdata())
    matrx = dct_coefficients(da)
    avg = sum([e for r in matrx for e in r]) / 64

    binary_list = [0 if e < avg else 1 for r in matrx for e in r]
    hs = reduce(lambda x, y_z: x | (y_z[1] << y_z[0]), enumerate(binary_list), 0)

    return hs


def differenceHash(img, size=8):
    '''
    :param img:
    :param size:
    :return:  In this case, the 9 pixels per row yields 8 differences between adjacent pixels. Eight rows of eight differences becomes 64 bits.
    '''
    if not isinstance(img, Image.Image):
        img = Image.open(img)
    im = img.resize((size + 1, size), Image.ANTIALIAS).convert('L')

    c = list(im.getdata())
    d = []
    for i in range(len(c) - 1):
        if c[i] < c[i + 1] and i % 9 != 8:
            d.append(1)
        elif i % 9 != 8:
            d.append(0)
    d.reverse()
    hs = reduce(lambda x, y_z: x | (y_z[1] << y_z[0]), enumerate(d), 0)

    return hs


def hammingDistance(h1, h2):
    '''
    if h1 and h2 are string,they should have the same length
    :param h1: int or string 'da' & 'ad' or 3 & 1
    :param h2:
    :return: hamming distance between two vectors
    '''
    if isinstance(h1, int) and isinstance(h2, int):
        h, d = 0, h1 ^ h2
        while d:
            h += 1
            d &= d - 1
        return h
    elif isinstance(h1, str) and isinstance(h2, str):
        if len(h1) != len(h2):
            raise ValueError("Unequal length")
        return sum(e1 != e2 for e1, e2 in zip(h1, h2))
    else:
        raise ValueError("Mismatch")


def cosine_similarity(c1, c2):
    '''
    :param c1:  vector c1   (list) it can be integer or string list e.g. ['am','is']
    :param c2:  vector c2   (list)
    :return: cosine similarity , degrees
    '''
    '''
    integer list should have equal length
    string list will be calculated the frequency and generate list to get cosine similarity
    '''
    from math import degrees, acos, sqrt
    def cs(a, b):
        c = sum(a[i] * b[i] for i in range(len(a)))
        norm = lambda v: sqrt(sum(i * i for i in v))
        result = c / norm(a) / norm(b)
        return result, degrees(acos(result))

    if isinstance(c1[0], int):
        if len(c1) != len(c2):
            raise ValueError("Unequal length")
        return cs(c1, c2)
    elif isinstance(c1[0], str):
        d1, d2 = [], []
        for i in list(set(c1 + c2)):
            d1.append(c1.count(i))
            d2.append(c2.count(i))
        return cs(d1, d2)
