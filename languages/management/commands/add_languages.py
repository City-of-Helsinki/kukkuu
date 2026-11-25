from django.core.management import BaseCommand
from django.db import transaction
from django.utils import translation

from languages.exceptions import LanguageAlreadyExistsError
from languages.models import Language

DEFAULT_LANGUAGES_FILE = "data/default_languages.csv"


class Command(BaseCommand):
    help = "Adds languages by their ISO 639-3 alpha-3 codes."

    def add_arguments(self, parser):
        parser.add_argument(
            "codes",
            nargs="?",
            type=str,
            help="Comma-separated list of codes to be added.",
        )
        parser.add_argument(
            "--default",
            action="store_true",
            help=(
                f'Add default languages provided in file "{DEFAULT_LANGUAGES_FILE}" '
                'and special languages "Other" and "Speechless".'
            ),
        )
        parser.add_argument(
            "--use-english-fallback",
            action="store_true",
            help=(
                "Use the English name for the names that Unicode CLDR does not have, "
                "instead of failing."
            ),
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Flush all existing languages before adding new ones. Use with caution!",  # noqa: E501
        )

    @transaction.atomic
    @translation.override("en")
    def handle(self, *args, **options):
        if not any(options[a] for a in ("flush", "default", "codes")):
            self.stdout.write("Nothing to do. Hint: try --help.")
            return

        if options["flush"]:
            Language.objects.all().delete()
            self.stdout.write("Flushed existing languages")

        codes = []

        if options["default"]:
            with open(DEFAULT_LANGUAGES_FILE, "rt") as f:
                codes.extend(f.read().split(","))
            self._create_special_languages()

        if options["codes"] is not None:
            codes.extend(options["codes"].split(","))

        for code in codes:
            code = code.strip()
            try:
                created = Language.objects.create_from_language_code(
                    code, use_english_fallback=options["use_english_fallback"]
                )
            except LanguageAlreadyExistsError:
                language_str = (
                    Language.objects.filter(alpha_3_code=code).first() or code
                )
                self.stdout.write(f"{language_str} already exists")
            else:
                self.stdout.write(f"Created {created.language}")
                if created.fallback_language_codes:
                    fallback_language_codes = ", ".join(created.fallback_language_codes)
                    self.stdout.write(
                        self.style.WARNING(
                            f"Used the English name for {code} "
                            f"in language(s): {fallback_language_codes}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("All done!"))

    def _create_special_languages(self):
        for special_name, create_special_language in (
            ("Other", Language.objects.create_option_other),
            ("Speechless", Language.objects.create_option_speechless),
        ):
            try:
                create_special_language()
                self.stdout.write(f'Created special language "{special_name}"')
            except LanguageAlreadyExistsError:
                self.stdout.write(f'Special language "{special_name}" already exists')
