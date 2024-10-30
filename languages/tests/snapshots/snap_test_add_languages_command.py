# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_add_default_languages 1'] = '''Created special language "Other"
Created Arabic (ara)
Created Bengali (ben)
Created German (deu)
Created English (eng)
Created Estonian (est)
Created Persian (fas)
Created Finnish (fin)
Created French (fra)
Created Hindi (hin)
Created Italian (ita)
Created Kurdish (kur)
Created Nepali (macrolanguage) (nep)
Created Norwegian (nor)
Created Polish (pol)
Created Portuguese (por)
Created Romanian (ron)
Created Russian (rus)
Created Sami languages (smi)
Created Somali (som)
Created Spanish (spa)
Created Albanian (sqi)
Created Swedish (swe)
Created Tagalog (tgl)
Created Thai (tha)
Created Turkish (tur)
Created Ukrainian (ukr)
Created Urdu (urd)
Created Vietnamese (vie)
Created Chinese (zho)
All done!
'''

snapshots['test_add_default_languages 2'] = {
    None: {
        'en': 'Other language',
        'fi': 'muu kieli',
        'sv': 'Annat språk'
    },
    'ara': {
        'en': 'Arabic',
        'fi': 'arabia',
        'sv': 'Arabiska'
    },
    'ben': {
        'en': 'Bengali',
        'fi': 'bengali',
        'sv': 'Bengali'
    },
    'deu': {
        'en': 'German',
        'fi': 'saksa',
        'sv': 'Tyska'
    },
    'eng': {
        'en': 'English',
        'fi': 'englanti',
        'sv': 'Engelska'
    },
    'est': {
        'en': 'Estonian',
        'fi': 'viro',
        'sv': 'Estniska'
    },
    'fas': {
        'en': 'Persian',
        'fi': 'persia',
        'sv': 'Persiska'
    },
    'fin': {
        'en': 'Finnish',
        'fi': 'suomi',
        'sv': 'Finska'
    },
    'fra': {
        'en': 'French',
        'fi': 'ranska',
        'sv': 'Franska'
    },
    'hin': {
        'en': 'Hindi',
        'fi': 'hindi',
        'sv': 'Hindi'
    },
    'ita': {
        'en': 'Italian',
        'fi': 'italia',
        'sv': 'Italienska'
    },
    'kur': {
        'en': 'Kurdish',
        'fi': 'kurdi',
        'sv': 'Kurdiska'
    },
    'nep': {
        'en': 'Nepali (macrolanguage)',
        'fi': 'Nepali (macrolanguage)',
        'sv': 'Nepali'
    },
    'nor': {
        'en': 'Norwegian',
        'fi': 'norja',
        'sv': 'Norska'
    },
    'pol': {
        'en': 'Polish',
        'fi': 'puola',
        'sv': 'Polska'
    },
    'por': {
        'en': 'Portuguese',
        'fi': 'portugali',
        'sv': 'Portugisiska'
    },
    'ron': {
        'en': 'Romanian',
        'fi': 'romania',
        'sv': 'Rumänska'
    },
    'rus': {
        'en': 'Russian',
        'fi': 'venäjä',
        'sv': 'Ryska'
    },
    'smi': {
        'en': 'Sami languages',
        'fi': 'Sami languages',
        'sv': 'Sami languages'
    },
    'som': {
        'en': 'Somali',
        'fi': 'somali',
        'sv': 'Somali'
    },
    'spa': {
        'en': 'Spanish',
        'fi': 'espanja',
        'sv': 'Spanska'
    },
    'sqi': {
        'en': 'Albanian',
        'fi': 'albania',
        'sv': 'Albanska'
    },
    'swe': {
        'en': 'Swedish',
        'fi': 'ruotsi',
        'sv': 'Svenska'
    },
    'tgl': {
        'en': 'Tagalog',
        'fi': 'tagalog',
        'sv': 'Tagalog'
    },
    'tha': {
        'en': 'Thai',
        'fi': 'thai',
        'sv': 'Thailändska'
    },
    'tur': {
        'en': 'Turkish',
        'fi': 'turkki',
        'sv': 'Turkiska'
    },
    'ukr': {
        'en': 'Ukrainian',
        'fi': 'ukraina',
        'sv': 'Ukrainska'
    },
    'urd': {
        'en': 'Urdu',
        'fi': 'urdu',
        'sv': 'Urdu'
    },
    'vie': {
        'en': 'Vietnamese',
        'fi': 'vietnam',
        'sv': 'Vietnamesiska'
    },
    'zho': {
        'en': 'Chinese',
        'fi': 'kiina',
        'sv': 'Kinesiska'
    }
}

snapshots['test_add_languages 1'] = '''Created Manide (abd)
Created Ngelima (agh)
All done!
'''

snapshots['test_add_languages 2'] = {
    'abd': {
        'en': 'Manide',
        'fi': 'Manide',
        'sv': 'Manide'
    },
    'agh': {
        'en': 'Ngelima',
        'fi': 'Ngelima',
        'sv': 'Ngelima'
    }
}

snapshots['test_add_languages_and_flush 1'] = '''Flushed existing languages
Created Manide (abd)
Created Ngelima (agh)
All done!
'''

snapshots['test_add_languages_and_flush 2'] = {
    'abd': {
        'en': 'Manide',
        'fi': 'Manide',
        'sv': 'Manide'
    },
    'agh': {
        'en': 'Ngelima',
        'fi': 'Ngelima',
        'sv': 'Ngelima'
    }
}

snapshots['test_no_arguments 1'] = '''Nothing to do. Hint: try --help.
'''
