from datetime import date
from typing import List, Optional

from django.utils.timezone import localdate
from drf_spectacular.utils import (
    extend_schema_field,
)
from rest_framework import serializers

from children.models import Child
from reports.consts import (
    CONTACT_LANGUAGE_PRIORITIES,
    CONTACT_LANGUAGE_TO_LANGUAGE,
    LANGUAGE_CHOICES,
    OTHER_LANGUAGE_API_NAME,
)


def get_primary_contact_language(contact_languages: List[str]):
    return [
        contact_lang
        for lang in CONTACT_LANGUAGE_PRIORITIES
        for contact_lang in contact_languages
        if contact_lang == lang
    ][0]


class ChildSerializer(serializers.ModelSerializer):
    child_birthyear_postal_code_guardian_emails_hash = serializers.SerializerMethodField(  # noqa
        help_text="Salted hash of child's birthyear, postal code and guardians' emails."
    )
    child_name_birthyear_postal_code_guardian_emails_hash = (
        serializers.SerializerMethodField(
            help_text="Salted hash of child's name (i.e. first name and last name), "
            "birthyear, postal code and guardians' emails."
        )
    )
    registration_date = serializers.SerializerMethodField()
    birthyear = serializers.SerializerMethodField()
    contact_language = serializers.SerializerMethodField()
    languages_spoken_at_home = serializers.SerializerMethodField(
        help_text="Array of ISO 639-3 (language) or ISO 639-5 (language family) "
        "alpha-3 codes. Value `__OTHER__` means any other language."  # noqa
    )
    is_obsolete = serializers.SerializerMethodField(
        help_text="Are all the child's guardian user instances marked as obsolete?"
    )

    class Meta:
        model = Child
        fields = [
            "child_birthyear_postal_code_guardian_emails_hash",
            "child_name_birthyear_postal_code_guardian_emails_hash",
            "registration_date",
            "birthyear",
            "postal_code",
            "contact_language",
            "languages_spoken_at_home",
            "is_obsolete",
        ]

    def get_child_birthyear_postal_code_guardian_emails_hash(self, child: Child) -> str:
        """
        Salted hash of child's birthyear, postal code and guardians' emails.
        """
        return child.birthyear_postal_code_guardian_emails_hash

    def get_child_name_birthyear_postal_code_guardian_emails_hash(
        self, child: Child
    ) -> str:
        """
        Salted hash of child's name (i.e. first name and last name), birthyear, postal
        code and guardians' emails.
        """
        return child.name_birthyear_postal_code_guardian_emails_hash

    def get_registration_date(self, obj: Child) -> date:
        return localdate(obj.created_at)

    def get_birthyear(self, obj: Child) -> int:
        return obj.birthyear

    @extend_schema_field(
        serializers.ChoiceField(
            choices=(("fin", "Finnish"), ("swe", "Swedish"), ("eng", "English"))
        )
    )
    def get_contact_language(self, obj: Child) -> str:
        contact_languages = [
            guardian.language for guardian in list(obj.guardians.all())
        ]
        primary_contact_lang = get_primary_contact_language(contact_languages)
        return CONTACT_LANGUAGE_TO_LANGUAGE[primary_contact_lang]

    @extend_schema_field(
        serializers.ListField(child=serializers.ChoiceField(choices=LANGUAGE_CHOICES))
    )
    def get_languages_spoken_at_home(self, obj: Child) -> List[Optional[str]]:
        return [
            lang.alpha_3_code or OTHER_LANGUAGE_API_NAME
            for lang in obj.guardians.all()[0].prefetched_languages_spoken_at_home
        ]

    def get_is_obsolete(self, obj: Child) -> bool:
        return obj.is_obsolete
