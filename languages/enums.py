from enum import Enum


class LanguageType(Enum):
    """
    ISO 639-3 language type, see "Type" in:
    https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso639-3_table_definition.txt
    """

    ANCIENT = "A"
    CONSTRUCTED = "C"
    EXTINCT = "E"
    HISTORICAL = "H"
    LIVING = "L"
    SPECIAL = "S"
