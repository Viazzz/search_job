from crispy_forms.helper import FormHelper

from django import forms

from .models import FoundVacancies


class SearchForm(forms.Form):
    choices = FoundVacancies.SearchRequest.choices

    search_request = forms.ChoiceField(choices=choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-inline"
