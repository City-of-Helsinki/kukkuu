from django import forms
from django.db.models import Q

from languages.models import Language


class LanguageSpokenAtHomeInlineForm(forms.ModelForm):
    """
    Form for an admin inline that links a child or a guardian to a language spoken at
    home. Only languages with `can_be_spoken_at_home` can be chosen, except that the
    language already linked by the form's instance stays available so that an
    existing link can be saved after the flag has been switched off.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["language"].queryset = Language.objects.filter(
            Q(can_be_spoken_at_home=True) | Q(pk=self.instance.language_id)
        )
