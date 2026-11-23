# ISO 639-3 special code "und" (Undetermined) is used for the "Other language" option.
OTHER_LANGUAGE_ALPHA_3_CODE = "und"
OTHER_LANGUAGE_NAMES = {
    "fi": "Muu kieli",
    "sv": "Annat språk",
    "en": "Other language",
}

# ISO 639-3 special code "zxx" (No linguistic content) is used for the "Speechless"
# option, e.g. for occurrences that have no linguistic content at all.
SPEECHLESS_LANGUAGE_ALPHA_3_CODE = "zxx"
SPEECHLESS_LANGUAGE_NAMES = {
    "fi": "Sanaton",
    "sv": "Ordlös",
    "en": "Speechless",
}

# ISO 639-3 special codes:
# - "mis" (Uncoded languages)
# - "mul" (Multiple languages)
# - "und" (Undetermined)
# - "zxx" (No linguistic content)
# See https://iso639-3.sil.org/code_tables/639/data
SPECIAL_LANGUAGE_ALPHA_3_CODES = ("mis", "mul", "und", "zxx")
