from django.contrib import admin

from .models import FoundVacancies, UserTokenModel


@admin.register(FoundVacancies)
class FoundVacanciesAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "search_request",
        "salary_from",
        "employer_name",
        "employer_rating",
        "employer_review_count",
        "employer_responded",
        "area_name",
    ]
    search_fields = [
        "name",
    ]
    list_filter = [
        "search_request",
        "employer_responded",

    ]


@admin.register(UserTokenModel)
class UserTokerModelAdmin(admin.ModelAdmin):
    list_display = [
        "user",
    ]
