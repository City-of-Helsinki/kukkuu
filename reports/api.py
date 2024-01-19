from datetime import date
from typing import List, Optional

from django.db.models import Prefetch
from django.utils.timezone import localdate
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_field,
    extend_schema_serializer,
    extend_schema_view,
    OpenApiExample,
)
from rest_framework import mixins, serializers, viewsets

from children.models import Child
from languages.models import Language

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


def get_primary_contact_language(contact_languages: List[str]):
    return [
        contact_lang
        for lang in CONTACT_LANGUAGE_PRIORITIES
        for contact_lang in contact_languages
        if contact_lang == lang
    ][0]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Example 1",
            value=[
                {
                    "registration_date": "2021-02-18",
                    "birth_year": 2021,
                    "contact_language": "fin",
                    "languages_spoken_at_home": ["fin", "nor", "__OTHER__"],
                },
                {
                    "registration_date": "2021-03-18",
                    "birth_year": 2020,
                    "contact_language": "eng",
                    "languages_spoken_at_home": [],
                },
            ],
            response_only=True,
        ),
    ]
)
class ChildSerializer(serializers.ModelSerializer):
    child_birthdate_postal_code_guardian_emails_hash = serializers.SerializerMethodField(  # noqa
        help_text="Salted hash of child's birthdate, postal code and guardians' emails."
    )
    child_name_birthdate_postal_code_guardian_emails_hash = (
        serializers.SerializerMethodField(
            help_text="Salted hash of child's name (i.e. first name and last name), "
            "birthdate, postal code and guardians' emails."
        )
    )
    registration_date = serializers.SerializerMethodField()
    birth_year = serializers.SerializerMethodField()
    contact_language = serializers.SerializerMethodField()
    languages_spoken_at_home = serializers.SerializerMethodField(
        help_text="Array of ISO 639-3 (language) or ISO 639-5 (language family) "
        "alpha-3 codes. Value `__OTHER__` means any other language."  # noqa
    )

    class Meta:
        model = Child
        fields = [
            "child_birthdate_postal_code_guardian_emails_hash",
            "child_name_birthdate_postal_code_guardian_emails_hash",
            "registration_date",
            "birth_year",
            "postal_code",
            "contact_language",
            "languages_spoken_at_home",
        ]

    def get_child_birthdate_postal_code_guardian_emails_hash(self, child: Child) -> str:
        """
        Salted hash of child's birthdate, postal code and guardians' emails.
        """
        return child.birthdate_postal_code_guardian_emails_hash

    def get_child_name_birthdate_postal_code_guardian_emails_hash(
        self, child: Child
    ) -> str:
        """
        Salted hash of child's name (i.e. first name and last name), birthdate, postal
        code and guardians' emails.
        """
        return child.name_birthdate_postal_code_guardian_emails_hash

    def get_registration_date(self, obj: Child) -> date:
        return localdate(obj.created_at)

    def get_birth_year(self, obj: Child) -> int:
        return obj.birthdate.year

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
            l.alpha_3_code or OTHER_LANGUAGE_API_NAME
            for l in obj.guardians.all()[0].prefetched_languages_spoken_at_home
        ]


@extend_schema_view(list=extend_schema(description="Get all children data."))
class ChildViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        Child.objects.exclude(guardians=None)
        .prefetch_related(
            Prefetch(
                "guardians__languages_spoken_at_home",
                queryset=Language.objects.order_by("alpha_3_code"),
                to_attr="prefetched_languages_spoken_at_home",
            ),
        )
        .prefetch_related("guardians")
        .order_by("name")
    )
    serializer_class = ChildSerializer
