# -*- coding: utf-8 -*-

"""
Conversion between Katakana <-> Hiragana <-> Romanji
"""

import re

hibiki_dir = os.path.dirname(os.path.abspath(__file__)) + '/data/hibiki_dir/'

# From https://stackoverflow.com/a/47278687/610569
KATAKANA_HIRGANA_SHIFT = 0x30a1 - 0x3041  # KATAKANA LETTER A - HIRAGANA A

def shift_by(n):
    def replacer(match):
        return ''.join(chr(ord(c) + n) for c in match.group(0))

    return replacer

def katakana_to_hiragana(text):
    return re.sub(r'^[\u30a1-\u30f6]+', shift_by(KATAKANA_HIRGANA_SHIFT), text)

def hiragana_to_katakana(text):
    return re.sub(r'^[\u3041-\u3096]+', shift_by(-KATAKANA_HIRGANA_SHIFT), text)


def read_hiragana_mappings(filename):
    hiragana_to_romanji_mappings = {}
    with open(hibiki_dir+filename) as fin:
        for line in fin:
            if line.startswith(';;'):
                continue
            else:
                romanji, hiragana = line.strip().split()
                hiragana_to_romanji_mappings[hiragana] = romanji
    return hiragana_to_romanji_mappings


hiragana_to_hepburn_mappings = read_hiragana_mappings('hepburnhira.utf8')
hiragana_to_passport_mappings = read_hiragana_mappings('passporthira.utf8')
hiragana_to_kunrei_mappings = read_hiragana_mappings('kunreihira.utf8')

katakana_to_hepburn_mappings = read_hiragana_mappings('hepburndict.utf8')
katakana_to_passport_mappings = read_hiragana_mappings('passportdict.utf8')
katakana_to_kunrei_mappings = read_hiragana_mappings('kunreidict.utf8')

__all__ = ['katakana_to_hiragana', 'hiragana_to_katakana']
