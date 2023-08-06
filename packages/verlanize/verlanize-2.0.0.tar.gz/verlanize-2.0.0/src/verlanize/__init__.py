# -*- coding: utf-8 -*-
"""
This verlanize french. 
"""

import logging
import re

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)

# we use X-SAMPA instead of IPA, because IPA uses UTF-8 symbols that are hard 
# to display in an editor
verlan_words = {
    'américain': ['cainri', 'kE~.Ri'],
    'arabe': ['rebeu', None],
    'brancher': ['chébrans', None],
    'branché': ['chébrans', None],
    'branchée': ['chébrans', None],
    'branchées': ['chébrans', None],
    'bête': ['teubé', None],
    'carotter': ['rot-ca', None],
    'carotté': ['rot-ca', None],
    'chaud': ['auch', None],
    'cher': ['reuch', None],
    'chien': ['iench', None],
    'choper': ['pécho', None],
    'chopé': ['pécho', None],
    'chopés': ['pécho', None],
    'chopée': ['pécho', None],
    'chopées': ['pécho', None],
    'cigarette': ['garetci', None],
    'cité': ['téci', None],
    'cités': ['téci', None],
    'comme ça': ['ça kom', None],
    'dingue': ['gueudin', None],
    'dingues': ['gueudin', None],
    'disque': ['skeud', None],
    'disques': ['skeud', None],
    'défoncer': ['fonsdé', None],
    'défoncé': ['fonsdé', None],
    'défoncés': ['fonsdé', None],
    'défoncée': ['fonsdé', None],
    'défoncées': ['fonsdé', None],
    'énervé': ['vénèr', None],
    'femme': ['meuf', None],
    'flasher': ['chéfla', None],
    'flic': ['keuf', None],
    'fou': ['ouf', None],
    'français': ['céfran', None],
    'frère': ['reuf', None],
    'fumer': ['méfu', None],
    'fête': ['teuf', None],
    'gentil': ['tigen', None],
    'gramme': ['meug', None],
    'grave': ['veugra', 'v@.gRa'],
    'herbe': ['beuh', None],
    'je ne sais pas': ['Ché ap', None],
    'joint': ['oinj', None],
    'juif': ['feuj', None],
    'louche': ['cheulou', None],
    'lourd': ['relou', None],
    'manger': ['géman', None],
    'mate': ['téma', None],
    'mater': ['téma', None],
    'mec': ['keum', None],
    'mecs': ['keums', None],
    'merde': ['deumer', None],
    'moche': ['cheum', None],
    'moches': ['cheums', None],
    'moi': ['wam', None],
    'monnaie': ['némo', None],
    'mouche': ['cheumou', None],
    'mouillé': ['yémou', None],
    'mouillés': ['yémous', None],
    'mouillées': ['yémous', None],
    'musique': ['zicmu', None],
    'mère': ['reum', None],
    'méchant': ['chan-mé', None],
    'métro': ['tromé', None],
    'nez': ['zen', None],
    'noir': ['renoi', None],
    'pakistanais': ['kospa', None],
    'pakos': ['kospa', None],
    'parents': ['rempa', None],
    'petit': ['tipeu', None],
    'photo': ['tofo', None],
    'pied': ['ièp', None],
    'planqué': ['képlan', None],
    'planqués': ['képlans', None],
    'planquées': ['képlans', None],
    'pompes': ['peupon', None],
    'pourri': ['ripou', None],
    'pute': ['teupu', None],
    'père': ['reup', None],
    'pétard': ['tarpé', None],
    'pétasse': ['tasspé', None],
    'rage': ['geura', None],
    'rap': ['peura', None],
    'ricain': ['cainri', None],
    'rigoler': ['golri', None],
    'sec': ['keussé', None],
    'sein': ['eins', None],
    'shit': ['teuch', None],
    'soeur': ['reus', None],
    'soirée': ['réssoi', None],
    'toi': ['wat', None],
    'toubab': ['babtou', None],
    'triper': ['pétri', None],
    'truc': ['keutru', None],
    'vas-y': ['ziva', None],
    'voiture': ['turvoi', None],
}

verlan_re = dict()

def init():
    for word in verlan_words:
        verlan = verlan_words[word][0]
        x_sampa = verlan_words[word][1]
        # Normal case
        pattern = r'\b%s\b' % word
        prog = re.compile(pattern)
        verlan_re[prog] = [verlan, x_sampa] 
        
        # UPPER case
        pattern = r'\b%s\b' % word.upper()
        prog = re.compile(pattern)
        verlan_re[prog] = [verlan.upper(), x_sampa]
        
        # Title case
        pattern = r'\b%s\b' % word.title()
        prog = re.compile(pattern)
        verlan_re[prog] = [verlan.title(), x_sampa]


def default_observer(match, verlan, x_sampa):
    LOGGER.debug("Text: %s", match.string)
    return ''.join([match.string[:match.start()],
                    verlan, 
                    match.string[match.end():]])


def find_matching(matcher, verlanized, string, prog):
    temp = string
    match = None
    while True:
        match = prog.search(temp, 0 if match is None else match.pos + len(match.group()))
        if match is None:
            break
        LOGGER.debug("Found %s in %s at %s", match.group(), match.string, match.start())
        verlanized.append(match.group())
        temp = matcher(match, verlan_re[prog][0], verlan_re[prog][1])

    return temp

def verlanize(text, matcher=default_observer):
    if text is None:
        return (None, [])
    verlanized = []
    temp = text
    for prog in verlan_re:
        temp = find_matching(matcher, verlanized, temp, prog)
    return [temp, verlanized]
