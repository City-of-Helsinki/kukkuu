import factory

from tags.models import ThemePath


class ThemePathFactory(factory.django.DjangoModelFactory):
    slug = factory.Sequence(lambda n: f"theme_path_{n}")
    name = factory.Faker("text", max_nb_chars=32)
    description = factory.Faker("text")

    class Meta:
        model = ThemePath
        django_get_or_create = ("slug",)
        skip_postgeneration_save = True  # Not needed after factory v4.0.0

    @factory.post_generation
    def translations(self, create, extracted, **kwargs):
        if not extracted:
            return
        for language_code, fields in extracted.items():
            self.set_current_language(language_code)
            self.name = fields.get("name", "")
            self.description = fields.get("description", "")
        if create:
            self.save()
