import django_filters
from django import forms
from django.urls import reverse_lazy

from .models import FoundVacancies
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_bootstrap5.bootstrap5 import Switch


class FoundVacancisFilter(django_filters.FilterSet):
    search_request = django_filters.ChoiceFilter(choices=FoundVacancies.SearchRequest.choices, empty_label=None)
    blacklist = django_filters.BooleanFilter(widget=forms.CheckboxInput())
    
    class Meta:
        model = FoundVacancies
        fields = {
            "search_request": ["exact",],
            "employer_name": ["icontains",],
            "blacklist": ["exact",],
        }
        
    
    @property
    def form(self):
        form = super().form
        form["search_request"].label=None
        form["employer_name__icontains"].label=None
        form.helper = FormHelper()
        form.helper.attrs = {
            "hx-get": reverse_lazy("work_search:vacancies_list"),
            "hx-trigger": "change, keyup delay:.5s",
            "hx-target": "#vacancies_list",
        }
        form.helper.layout = Layout(
            Row(
                Column("search_request", css_class="col-3"),
                Column("employer_name__icontains", css_class="col-3"),
                Column(Switch("blacklist"), css_class="col-2 align-self-end mb-2"),
            css_class="justify-content-center"
            ),
        )
        return form
    
    