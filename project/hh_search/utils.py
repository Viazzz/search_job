import pandas as pd
import requests
from flatten_json import flatten
import re
import json
import urllib


columns = [
    "search_request",
    "id",
    "name",
    "salary_from",
    "salary_to",
    "salary_currency",
    "alternate_url",
    "employer_id",
    "snippet_requirement",
    "snippet_responsibility",
    "schedule_name",
    "employer_name",
    "employer_alternate_url",
    "employer_rating",
    "employer_review_count",
    "area_name",
    "published_at",
    "created_at",
]


def get_vacansies_or_403(search_request, page, access_token):
    url = "https://api.hh.ru/vacancies"
    headers = {
        "User-Agent": "job search (jobsearch@mail.com)",
        "Authorization": f"Bearer {access_token}",
    }
    params = {
        "text": search_request,
        "per_page": 100,
        "schedule": "remote",
        "page": page,
    }
    params=urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 403:
        return response.status_code
    else:
        return response.json()


def convert_to_float(str_value):
    if str_value != "Нет отзывов":
        result = (
            float(str_value.replace(",", ".")) if "," in str_value else float(str_value)
        )

    else:
        result = str_value
    return result


def get_employer_rating(df):
    employer_rating = (
        df.assign(
            employer_rating_dict=lambda x: x.employer_id.apply(
                lambda x: extract_raiting_from_html(x)
            )
        )
        .loc[lambda x: x.employer_rating_dict.notna()]
        .assign(
            employer_rating=lambda x: pd.to_numeric(
                x.employer_rating_dict.apply(lambda x: x.get("ratingValue")),
                errors="coerce",
                downcast="float",
            ),                
            employer_review_count=lambda x: pd.to_numeric(
                x.employer_rating_dict.apply(lambda x: x.get("reviewCount")),
                errors="coerce",
                downcast="float",
            ),
        )
        .assign(employer_rating=lambda x: x.employer_rating.apply(lambda x: round(x, 1)))
        .drop(columns=["employer_rating_dict"])
    )
    return employer_rating

# changed api, removed rating
def extract_employer_rating(employer_id, access_token):
    url = f"https://api.hh.ru/vacancies?employer_id={employer_id}"
    headers = {
        "User-Agent": "job search (jobsearch@mail.com)",
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(url, headers=headers)
    employer_rating = response.json()
    employer_rating = (
        employer_rating.get("items")[0].get("employer").get("employer_rating")
    )
    print(url, employer_rating)
    return employer_rating

# get rating from dreamjob
def extract_raiting_from_html(employer_id):
    headers = {"User-Agent": "job search (jobsearch@mail.com)"}
    url = f"https://hh.ru/employer/{employer_id}/reviews?type=6&hhtmFrom=BigWidget"
    response = requests.get(url, headers=headers)
    html = response.text
    text = re.findall('"aggregateRating":(.*?),"name"', html)
    text = json.loads(text[0]) if text else {}
    print(f"{url=}, {text=}")
    return text
