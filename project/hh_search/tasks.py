import pandas as pd
import requests
from flatten_json import flatten
from celery import shared_task

from .models import FoundVacancies, UserTokenModel
from . import utils


@shared_task(name="find_vacancies")
def find_vacancies(user_id=1, search_request="django"):

    user_tokens = list(UserTokenModel.objects.filter(user=user_id).values())
    access_token = user_tokens[0].get("access_token")
    
    saved_id = list(
            FoundVacancies.objects.all().values_list("vacancies_id", "employer_id")
        )
    saved_id = pd.DataFrame(saved_id, columns=["vacancies_id", "employer_id"])

    columns = utils.columns
    df = pd.DataFrame()
    pages = utils.get_vacansies_or_403(search_request, 0, access_token)

    if pages == 403:
        refresh_token = user_tokens[0].get("refresh_token")
        user_tokens = utils.refresh_user_token(user_id, refresh_token)
        access_token = user_tokens[0].get("access_token")
        pages = utils.get_vacansies_or_403(search_request, 0, access_token)["pages"]
    else:
        pages = pages["pages"]

    for page in range(0, pages - 1):
        vacancies = utils.get_vacansies_or_403(search_request, page, access_token)
        flat_dict = [flatten(d) for d in vacancies["items"]]
        df = pd.concat([df, pd.json_normalize(flat_dict)])

    saved_vacancies_id = saved_id.vacancies_id.astype("str").unique().tolist()
    df = df.assign(
        search_request=search_request,
    ).loc[lambda x: ~x.id.isin(saved_vacancies_id)]

    saved_employer_id = saved_id.employer_id.astype("str").unique().tolist()
    employer_rating = (
        df.copy()[["employer_id"]]
        .drop_duplicates()
        .loc[lambda x: ~x.employer_id.isin(saved_employer_id)]
    )
    employer_rating = utils.get_employer_rating(
        employer_rating[:] # добавь срез для теста
    )
    df = (
        df.merge(employer_rating, how="left", on="employer_id")[columns]
        .loc[
            lambda x: (x.employer_rating >= 3)
            & (x.employer_review_count > 10)
            & (~x.id.isin(saved_id.vacancies_id))
        ]
        .sort_values(
            by=["employer_rating", "employer_review_count", "published_at"]
        )
    )

    vacancies = [
        FoundVacancies(
            search_request=row["search_request"],
            vacancies_id=row["id"],
            name=row["name"],
            salary_from=row["salary_from"],
            salary_to=row["salary_to"],
            salary_currency=row["salary_currency"],
            alternate_url=row["alternate_url"],
            employer_id=row["employer_id"],
            snippet_requirement=row["snippet_requirement"],
            snippet_responsibility=row["snippet_responsibility"],
            schedule_name=row["schedule_name"],
            employer_name=row["employer_name"],
            employer_alternate_url=row["employer_alternate_url"],
            employer_rating=row["employer_rating"],
            employer_review_count=row["employer_review_count"],
            area_name=row["area_name"],
            published_at=row["published_at"],
            created_at=row["created_at"],
        )
        for i, row in df.iterrows()
    ]
    FoundVacancies.objects.bulk_create(vacancies)
    vacancies = FoundVacancies.objects.filter(negotiations=False)
    return "search started"


@shared_task(name="find vacancies by scedule")
def find_vacancies_by_schedule():
    search_requests = FoundVacancies.SearchRequest.values
    [find_vacancies.delay(search_request=request) for request in search_requests]
    return "start task: find_vacancies_by_schedule"


