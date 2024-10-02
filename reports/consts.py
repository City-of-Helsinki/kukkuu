OTHER_LANGUAGE_API_NAME = "__OTHER__"


# Ideally we should get these from the database, as it is theoretically possible we
# might want add more languages dynamically in the future, but there doesn't seem to be
# an easy way to do that in a way that works with DRF Spectacular.
LANGUAGE_CHOICES = [
    ("ara", "Arabic"),
    ("ben", "Bengali"),
    ("deu", "German"),
    ("eng", "English"),
    ("est", "Estonian"),
    ("fas", "Persian"),
    ("fin", "Finnish"),
    ("fra", "French"),
    ("hin", "Hindi"),
    ("ita", "Italian"),
    ("kur", "Kurdish"),
    ("nep", "Nepali"),
    ("nor", "Norwegian"),
    ("pol", "Polish"),
    ("por", "Portuguese"),
    ("ron", "Romanian"),
    ("rus", "Russian"),
    ("smi", "Sami"),
    ("som", "Somali"),
    ("spa", "Spanish"),
    ("sqi", "Albanian"),
    ("swe", "Swedish"),
    ("tgl", "Tagalog"),
    ("tha", "Thai"),
    ("tur", "Turkish"),
    ("urd", "Urdu"),
    ("vie", "Vietnamese"),
    ("zho", "Chinese"),
    (OTHER_LANGUAGE_API_NAME, "Other language"),
]

CONTACT_LANGUAGE_TO_LANGUAGE = {
    "fi": "fin",
    "sv": "swe",
    "en": "eng",
}

CONTACT_LANGUAGE_PRIORITIES = ["fi", "en", "sv"]
