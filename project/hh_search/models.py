from django.db import models


class FoundVacancies(models.Model):

    class SearchRequest(models.TextChoices):
        PYTHON = "python", "python"
        DJANGO = "django", "django"
        DATA_ANALYST = "data analyst", "data analyst"
        DATA_ENGINEER = "data engineer", "data engineer"


    search_request = models.CharField(max_length=20, choices=SearchRequest.choices, default=SearchRequest.DJANGO)
    vacancies_id = models.PositiveIntegerField()
    name = models.CharField(max_length=500)
    salary_from = models.FloatField(null=True, blank=True)
    salary_to = models.FloatField(null=True, blank=True)
    salary_currency = models.CharField(max_length=20)
    alternate_url = models.URLField()
    snippet_requirement = models.TextField(null=True, blank=True)
    snippet_responsibility = models.TextField(null=True, blank=True)
    schedule_name = models.TextField(max_length=300)
    employer_name = models.CharField(max_length=500)
    employer_alternate_url = models.CharField(max_length=500)
    employer_id = models.PositiveIntegerField(default=1)
    employer_rating = models.FloatField()
    employer_review_count = models.PositiveIntegerField()
    area_name = models.CharField(max_length=500)
    published_at = models.DateTimeField()
    created_at = models.DateTimeField()
    created_record = models.DateTimeField(auto_now_add=True)
    update_record = models.DateTimeField(auto_now=True)
    employer_responded = models.BooleanField(default=False)
    blacklist = models.BooleanField(default=False)
    negotiations = models.BooleanField(default=False)

    class Meta:
        ordering = ["employer_rating", "employer_review_count", "-published_at"]        

    def __str__(self):
        return self.name
    
class UserTokenModel(models.Model):
    user = models.SmallIntegerField()
    access_token = models.CharField(max_length=200)
    refresh_token = models.CharField(max_length=200)


    def __str__(self):
        return str(self.user)
    
