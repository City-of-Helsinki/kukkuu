from .views import error_codes


def get_kukkuu_error_by_code(error_code):
    if not error_code:
        return None
    return next(
        (error for error, code in error_codes.items() if code == error_code), None
    )
