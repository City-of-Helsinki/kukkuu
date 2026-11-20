import pytest
from django.core.exceptions import ValidationError

from languages.models import Language


@pytest.mark.parametrize("alpha_3_code", ["sme", "und"])
def test_language_clean_accepts_iso_639_3_codes(alpha_3_code):
    Language(alpha_3_code=alpha_3_code).clean()


def test_language_clean_rejects_iso_639_5_codes():
    with pytest.raises(ValidationError):
        Language(alpha_3_code="smi").clean()
