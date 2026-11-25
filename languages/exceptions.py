class InvalidLanguageCodeError(Exception):
    """Invalid ISO 639-3 alpha-3 language code"""


class LanguageNameNotFoundError(Exception):
    """No Unicode CLDR name for the language in some non-English supported language"""


class LanguageAlreadyExistsError(Exception):
    """Language already exists"""
