# -*- coding: utf-8 -*-
"""
This verlanize french. 
"""

import logging
import re

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

verlan_words = {
    'américain': 'cainri',      
    'arabe': 'reubeu',
    'argent': 'gen-ar',
    'barette': 'retba',
    'bite': 'teub',
    'bizarre': 'zarbi',
    'black': 'keubla',
    'bombe': 'beubon',
    'bouche': 'cheubou',
    'branché': 'chébran',
    'branchée': 'chébrans',
    'branchées': 'chébrans',
    'bête': 'teubé',
    'carotter': 'rot-ca',
    'chaud': 'auch',
    'cher': 'reuch',
    'chien': 'iench',
    'choper': 'pécho',
    'cigarette': 'garetci',
    'cité': 'téci',
    'comme ça': 'ça kom',
    'dingue': 'gueudin',
    'disque': 'skeud',
    'défoncé': 'fonsdé',
    'énervé': 'vénèr',
    'femme': 'meuf',
    'flasher': 'chéfla',
    'flic': 'keuf',
    'fou': 'ouf',
    'français': 'céfran',
    'frère': 'reuf',
    'fumer': 'méfu',
    'fête': 'teuf',
    'gentil': 'tigen',
    'gramme': 'meug',
    'grave': 'veugra',
    'herbe': 'beuh',
    'je ne sais pas': 'Ché ap',
    'joint': 'oinj',
    'juif': 'feuj',
    'louche': 'cheulou',
    'lourd': 'relou',
    'manger': 'géman',
    'mate': 'téma',
    'mater': 'téma',
    'mec': 'keum',
    'merde': 'deumer',
    'moche': 'cheum',
    'moi': 'wam',
    'monnaie': 'némo',
    'mouche': 'cheumou',
    'mouillé': 'yémou',
    'mouillés': 'yémous',
    'mouillées': 'yémous',
    'musique': 'zicmu',
    'mère': 'reum',
    'méchant': 'chan-mé',
    'métro': 'tromé',
    'nez': 'zen',
    'noir': 'renoi',
    'pakistanais': 'kospa',
    'pakos': 'kospa',
    'parents': 'rempa',
    'petit': 'tipeu',
    'photo': 'tofo',
    'pied': 'ièp',
    'planqué': 'képlan',
    'planqués': 'képlans',
    'planquées': 'képlans',
    'pompes': 'peupon',
    'pourri': 'ripou',
    'pute': 'teupu',
    'père': 'reup',
    'pétard': 'tarpé',
    'pétasse': 'tasspé',
    'rage': 'geura',
    'rap': 'peura',
    'ricain': 'cainri',
    'rigoler': 'golri',
    'sec': 'keussé',
    'sein': 'eins',
    'shit': 'teuch',
    'soeur': 'reus',
    'soirée': 'réssoi',
    'toi': 'wat',
    'toubab': 'babtou',
    'triper': 'pétri',
    'truc': 'keutru',
    'vas-y': 'ziva',
    'voiture': 'turvoi',
}

verlan_re = dict()

def init():
    for word in verlan_words:
        # Normal case
        pattern = r'\b%s\b' % word
        prog = re.compile(pattern)
        verlan_re[prog] = verlan_words[word]
        
        # UPPER case
        pattern = r'\b%s\b' % word.upper()
        prog = re.compile(pattern)
        verlan_re[prog] = verlan_words[word].upper()
        
        # Title case
        pattern = r'\b%s\b' % word.title()
        prog = re.compile(pattern)
        verlan_re[prog] = verlan_words[word].title()


def verlanize(text):
    if text is None:
        return (None, [])
    verlanized = []
    temp = text
    for prog in verlan_re:
        match = prog.search(temp) 
        if match:
            verlanized.append(match.group())
            temp = prog.sub(verlan_re[prog], temp)
    return [temp, verlanized]
