import pytest
from django.forms import modelform_factory

import children.admin
import users.admin
from children.factories import ChildFactory
from languages.models import Language

INLINE_CLASSES = [
    children.admin.LanguagesSpokenAtHomeInline,
    users.admin.LanguagesSpokenAtHomeInline,
]


def get_form_class(inline_class):
    return modelform_factory(
        inline_class.model, form=inline_class.form, fields=["language"]
    )


@pytest.mark.parametrize("inline_class", INLINE_CLASSES)
def test_inline_form_offers_only_languages_that_can_be_spoken_at_home(
    inline_class, languages
):
    form = get_form_class(inline_class)()

    offered = set(form.fields["language"].queryset)
    not_offered = set(Language.objects.all()) - offered
    assert offered
    assert not_offered
    assert all(language.can_be_spoken_at_home for language in offered)
    assert all(not language.can_be_spoken_at_home for language in not_offered)


@pytest.mark.parametrize("inline_class", INLINE_CLASSES)
def test_inline_form_rejects_language_that_cannot_be_spoken_at_home(
    inline_class, languages
):
    speechless = Language.objects.get_option_speechless()
    assert not speechless.can_be_spoken_at_home

    form = get_form_class(inline_class)(data={"language": speechless.pk})

    assert not form.is_valid()
    assert "language" in form.errors


def test_inline_form_keeps_already_linked_language_available(languages):
    speechless = Language.objects.get_option_speechless()
    assert not speechless.can_be_spoken_at_home
    inline_class = children.admin.LanguagesSpokenAtHomeInline
    link = inline_class.model.objects.create(child=ChildFactory(), language=speechless)

    form = get_form_class(inline_class)(instance=link)

    assert speechless in form.fields["language"].queryset
