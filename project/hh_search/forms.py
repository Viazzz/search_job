from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

from django import forms

from .models import FoundVacancies


class FoundVacancisForm(forms.ModelForm):
    choices = FoundVacancies.SearchRequest.choices
    search_request = forms.ChoiceField(choices=choices, label="sdfsd")

    class Meta:
        model = FoundVacancies
        fields = {
            "search_request",
            "blacklist",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("search_request"),
                Column("blacklist"),
            ),
        )
