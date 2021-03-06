# -*- coding: utf-8 -*-
from os import listdir
from os.path import isfile, join
import string

OUT_DIR = './output/'

def process_file(fname):
    with open(fname, 'r') as f:
        text = f.read()
        text = text.replace('\xef\xbb\xbf', '')
        text = [c for c in text if c not in []]
        with open(OUT_DIR + fname, 'w') as g:
            g.write(''.join(text))


def main():
    files = [f for f in listdir('.') if 'txt' in f]
    for f in files:
        process_file(f)

main()
