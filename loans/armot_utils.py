#!/usr/bin/env python3
# -*- py-which-shell: "python3"; python: "python3" -*-

# Copyright (c) 2015 Frank Sergeant
# MIT license (see LICENSE file or http://pygmy.utoh.org/amort/LICENSE)
# frank@pygmy.utoh.org


# utils.py by fcs

# Miscellaneous utilities used by the other files.

# following allows printing commas to separate thousands with something like
#     locale.format('%13.2f', 12345.92, True) 

# or
# locale.setlocale(locale.LC_ALL, "en_US")

# For getting commas to separate thousands
# Here is Tim Keating's comment at
#   http://code.activestate.com/recipes/498181-add-thousands-separator-commas-to-formatted-number/
# >>> locale.setlocale(locale.LC_ALL, "")    -->  'English_United States.1252'
# >>> locale.format('%d', 12345, True)       -->  '12,345'
# and following is my test with a float
# >>> locale.format('%13.2f', 12345.92, True) 




import locale
locale.setlocale(locale.LC_ALL, "")

# This is from PPW32
ROUNDING_THRESHOLD = 0.0001    #100 times smaller than cents or pennies

def isZero (n):
    return abs(n) < ROUNDING_THRESHOLD

def rounded (n):
    if isZero(n):
        return 0.0
    else:
        return n

def money (num, width=10, decimals=2):
    '''Format a number with commas.  E.g.,
       money(13250) --> ' 13,250.00'
       
    '''
    fmt = "%%%d.%df" % (width, decimals)
    return locale.format(fmt, num, True) 

def money12 (num):
    return money (num, 12)

def money14 (num):
    return money (num, 14)

def money_3 (num):
    return money (num,decimals=3)

def money14_3 (num):
    return money (num,14,3)


def first (seq):
    return seq[0]

if __name__ == '__main__':

    print ("hello utils.py")
