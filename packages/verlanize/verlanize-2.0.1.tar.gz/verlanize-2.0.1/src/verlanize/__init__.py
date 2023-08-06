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
    'américains': ['cainris', 'kE~.Ri'],
    
    'arabe': ['rebeu', 'R@.b2'],
    'arabes': ['rebeus', 'R@.b2'],
    
    'brancher': ['chébrans', 'SebRA~'],
    'branché': ['chébrans', 'SebRA~'],
    'branchée': ['chébrans', 'SebRA~'],
    'branchées': ['chébrans', 'SebRA~'],
    
    'bête': ['teubé', 't9be'],
    'bêtes': ['teubés', 't9be'],
    
    'carotter': ['rot-ca', 'ROtka'],
    'carotté': ['rot-ca', 'ROtka'],
    
    'chaud': ['auch', 'oS'],
    'chauds': ['auchs', 'oS'],
    
    'cher': ['reuch', 'R2S'],
    'chers': ['reuchs', 'R2S'],
    'chère': ['reuchs', 'R2S'],
    'chères': ['reuchs', 'R2S'],
    
    'chien': ['iench', 'jE~S'],
    'chiens': ['ienchs', 'jE~S'],
    
    'choper': ['pécho', 'pe.SO'],
    'chopé': ['pécho', 'pe.SO'],
    'chopés': ['pécho', 'pe.SO'],
    'chopée': ['pécho', 'pe.SO'],
    'chopées': ['pécho', 'pe.SO'],
    
    'cigarette': ['garetci', 'gaREtsi'],
    'cigarettes': ['garetci', 'gaREtsi'],
    
    'cité': ['téci', 'te.si'],
    'cités': ['téci', 'te.si'],
    
    'comme ça': ['ça kom', 'sa kOm'],
    
    'dingue': ['gueudin', 'g2dE~'],
    'dingues': ['gueudin', 'g2dE~'],
    
    'disque': ['skeud', 'sk2d'],
    'disques': ['skeud', 'sk2d'],
    
    'défoncer': ['fonsdé', 'fO~sde'],
    'défoncé': ['fonsdé', 'fO~sde'],
    'défoncés': ['fonsdé', 'fO~sde'],
    'défoncée': ['fonsdé', 'fO~sde'],
    'défoncées': ['fonsdé', 'fO~sde'],
    
    'énervé': ['vénèr', 'venER'],
    'énervée': ['vénèr', 'venER'],
    'énervés': ['vénèr', 'venER'],
    'énervées': ['vénèr', 'venER'],
    
    'femme': ['meuf', 'm9f'],
    'femmes': ['meufs', 'm9f'],
    
    'flasher': ['chéfla', 'Seflaa'],
    'flashé': ['chéfla', 'Seflaa'],
    'flashée': ['chéfla', 'Seflaa'],
    'flashés': ['chéfla', 'Seflaa'],
    'flashées': ['chéfla', 'Seflaa'],
    
    'flic': ['keuf', 'k9f'],
    'flics': ['keufs', 'k9f'],
    
    'fou': ['ouf', 'uf'],
    'fous': ['oufs', 'uf'],
    
    'français': ['céfran', 'se.fRA~'],
    
    'frère': ['reuf', 'R9f'],
    'frères': ['reuf', 'R9f'],
    
    'fumer': ['méfu', 'me.fy'],
    'fumé': ['méfu', 'me.fy'],
    'fumée': ['méfu', 'me.fy'],
    'fumés': ['méfu', 'me.fy'],
    'fumées': ['méfu', 'me.fy'],
    
    'fête': ['teuf', 't9f'],
    'fêtes': ['teufs', 't9f'],
    
    'gentil': ['tigen', 'tiZA~'],
    'gentils': ['tigens', 'tiZA~'],
    
    'gramme': ['meug', 'm3g'],
    'grammes': ['meug', 'm3g'],
    
    'grave': ['veugra', 'v@.gRa'],
    'graves': ['veugra', 'v@.gRa'],
    
    'herbe': ['beuh', 'b2'],
    'herbes': ['beuh', 'b2'],
    
    'je ne sais pas': ['Ché ap', 'Se Ap'],
    
    'joint': ['oinj', 'wE~Z'],
    'joints': ['oinj', 'wE~Z'],
    
    'juif': ['feuj', 'f2Z~'],
    'juifs': ['feuj', 'f2Z~'],
    
    'louche': ['cheulou', 'S@.luu'],
    'louches': ['cheulou', 'S@.luu'],
    
    'lourd': ['relou', 'R@.lu'],
    'lourds': ['relous', 'R@.lu'],
    'lourde': ['relou', 'R@.lu'],
    'lourdes': ['relous', 'R@.lu'],
    
    'manger': ['géman', 'ZemA~'],
    'mangé': ['géman', 'ZemA~'],
    'mangés': ['géman', 'ZemA~'],
    'mangée': ['géman', 'ZemA~'],
    'mangées': ['géman', 'ZemA~'],
    
    'mater': ['téma', 'tema'],
    'maté': ['téma', 'tema'],
    'matée': ['téma', 'tema'],
    'matés': ['téma', 'tema'],
    'matées': ['téma', 'tema'],
    
    'mec': ['keum', 'k9m'],
    'mecs': ['keums', 'k9m'],

    'merde': ['deumer', 'd2mER'],
    'merdes': ['deumers', 'd2mER'],

    'merci': ['cimer', 'simER~'],

    'moche': ['cheum', 'S9m'],
    'moches': ['cheums', 'S9m'],

    'moi': ['wam', 'wam'],

    'monnaie': ['némo', 'nemo'],
    'monnaies': ['némos', 'nemo'],

    'mouche': ['cheumou', 'S@mu'],
    'mouches': ['cheumous', 'S@mu'],

    'mouillé': ['yémou', 'jemu'],
    'mouillés': ['yémous', 'jemu'],
    'mouillées': ['yémous', 'jemu'],

    'musique': ['zicmu', 'zik.my'],
    'musiques': ['zicmus', 'zik.my'],

    'mère': ['reum', 'R2~m'],
    'mères': ['reums', 'R2~m'],

    'méchant': ['chan-mé', 'SA~.mee'],
    'méchants': ['chan-més', 'SA~.mee'],

    'métro': ['tromé', 'tRo.mee'],
    'métros': ['tromés', 'tRo.mee'],

    'nez': ['zen', 'zEn'],

    'noir': ['renoi', 'R@.nwa'],
    'noirs': ['renois', 'R@.nwa'],

    'pakos': ['kospa', 'kospa'],

    'parents': ['rempa', 'RA~pa'],
    'parents': ['rempas', 'RA~pa'],

    'petit': ['tipeu', 'tip2'],
    'petits': ['tipeu', 'tip2'],

    'photo': ['tofo', 'tofo'],
    'photos': ['tofos', 'tofo'],

    'pied': ['ièp', 'jE.p'],
    'pieds': ['ièps', 'jE.p'],

    'planqué': ['képlan', 'keplA~.'],
    'planqués': ['képlans', 'keplA~.'],
    'planquées': ['képlans', 'keplA~.'],

    'pompe': ['peupon', 'p2pO~'],
    'pompes': ['peupon', 'p2pO~'],

    'pomper': ['pépon', 'pepO~'],
    'pompé': ['pépon', 'pepO~'],
    'pompée': ['pépon', 'pepO~'],
    'pompés': ['pépon', 'pepO~'],
    'pompées': ['pépon', 'pepO~'],

    'pourri': ['ripou', 'Ri.pu'],
    'pourris': ['ripoux', 'Ri.pu'],

    'pute': ['teupu', 't2.py'],
    'putes': ['teupus', 't2.py'],

    'père': ['reup', 'R9p'],
    'pères': ['reups', 'R9p'],

    'pétard': ['tarpé', 'taR.pe'],
    'pétards': ['tarpés', 'taR.pe'],

    'pétasse': ['tasspé', 'tas.pe'],
    'pétasses': ['tasspés', 'tas.pe'],

    'rage': ['geura', 'Z2Ra'],
    'rages': ['geuras', 'Z2Ra'],

    'rap': ['peura', 'p@rA'],

    'ricain': ['cainri', 'kE~.Ri'],
    'ricains': ['cainris', 'kE~.Ri'],

    'rigoler': ['golri', 'gOl.Ri'],
    'rigolé': ['golri', 'gOl.Ri'],
    'rigolée': ['golrie', 'gOl.Ri'],
    'rigolés': ['golris', 'gOl.Ri'],
    'rigolées': ['golries', 'gOl.Ri'],

    'sec': ['keussé', 'k9s'],
    'secs': ['keussés', 'k9s'],

    'sein': ['eins', 'E~~s'],
    'seins': ['eins', 'E~~s'],

    'shit': ['teuch', 't9.Si'],

    'soeur': ['reus', 'R9ss'],
    'soeurs': ['reus', 'R9ss'],

    'soirée': ['réssoi', 'Reswa'],
    'soirées': ['réssois', 'Reswa'],

    'toi': ['wat', 'wat'],
    
    'toubab': ['babtou', 'bab.tu~'],
    'toubabs': ['babtous', 'bab.tu~'],
    
    'triper': ['pétri', 'pe.tRi'],
    'tripé': ['pétri', 'pe.tRi'],
    'tripée': ['pétri', 'pe.tRi'],
    'tripés': ['pétri', 'pe.tRi'],
    'tripées': ['pétri', 'pe.tRi'],

    'truc': ['keutru', 'k@tRy'],
    'trucs': ['keutru', 'k@tRy'],
     
    'vas-y': ['ziva', 'zi.va'],
    
    'voiture': ['turvoi', 'tyrvwa'],
    'voitures': ['turvois', 'tyrvwa'],
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
