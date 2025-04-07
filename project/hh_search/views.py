import requests
import json
from flatten_json import flatten
import pandas as pd
import time

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import Count
from django.core.paginator import Paginator

from .models import FoundVacancies, UserTokenModel
from . import utils


def refresh_user_token(user_id, refresh_token):
    url = "https://api.hh.ru/token"
    headers = {
        "User-Agent": "job search (jobsearch@mail.com)",
    }
    params = {
        "refresh_token": f"{refresh_token}",
        "grant_type": "refresh_token",
    }
    response = requests.post(url, params=params, headers=headers)
    if response.status_code == 200:
        response = response.json()
        access_token = response.get("access_token")
        refresh_token = response.get("refresh_token")

        UserTokenModel.objects.filter(user=user_id).update(
            access_token=access_token, refresh_token=refresh_token
        )
        obj = list(UserTokenModel.objects.filter(user=user_id).values())
        return obj
    else:
        return response.text


def find_vacancies(request):
    if request.htmx:
        user_id = request.user.id
        user_tokens = list(UserTokenModel.objects.filter(user=user_id).values())
        access_token = user_tokens[0].get("access_token")

        saved_id = list(
            FoundVacancies.objects.all().values_list("vacancies_id", "employer_id")
        )
        saved_id = pd.DataFrame(saved_id, columns=["vacancies_id", "employer_id"])

        columns = utils.columns
        df = pd.DataFrame()
        search_request = request.GET.get("search_request")
        pages = utils.get_vacansies_or_403(search_request, 0, access_token)

        if pages == 403:
            refresh_token = user_tokens[0].get("refresh_token")
            user_tokens = refresh_user_token(user_id, refresh_token)
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
            df.copy()
            [["employer_id"]]
            .drop_duplicates()
            .loc[lambda x: ~x.employer_id.isin(saved_employer_id)]
        )
        employer_rating = utils.get_employer_rating(employer_rating[:]) #добавь срез для теста
        df =(
            df.merge(employer_rating, how="left", on="employer_id")
            [columns]
            .loc[
                lambda x: (x.employer_rating > 4)
                & (x.employer_review_count > 10)
                & (~x.id.isin(saved_id.vacancies_id))
            ]
            .sort_values(by=["employer_rating", "employer_review_count", "published_at"])
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
            for i, row in df.iterrows()]
        FoundVacancies.objects.bulk_create(vacancies)
        vacancies = FoundVacancies.objects.filter(negotiations=False)
        context = {
            "vacancies": vacancies,
        }
        return render(request, "partials/tables/vacancies_list_table.html", context)
    else:
        find_vacancies_active_link = "active"
        choices = FoundVacancies.SearchRequest.choices
        vacancies = FoundVacancies.objects.filter(search_request=choices[0][0], negotiations=False)
        context = {
            "find_vacancies_active_link": find_vacancies_active_link,
            "choices": choices,
            "vacancies": vacancies,
        }
        return render(request, "hh_search/find_vacancies.html", context)


def get_authorization_code(request):
    authorization_code = request.GET.get("code", "")
    context = {
        "authorization_code": authorization_code,
    }
    return render(request, "hh_search/get_authorization_code.html", context)

def change_blacklist(request, pk):
    vacancy = FoundVacancies.objects.get(pk=pk)
    if request.GET.get("blacklist"):
        vacancy.blacklist=True
        vacancy.save()
    else:
        vacancy.blacklist=False
        vacancy.save()
    return HttpResponse("")

def employer_responded(request, pk):
    vacancy = FoundVacancies.objects.get(pk=pk)
    if request.GET.get("employer_responded"):
        vacancy.employer_responded=True
        vacancy.save()
    else:
        vacancy.employer_responded=False
        vacancy.save()
    return HttpResponse("")

def send_responses_to_vacancies(request):
    search_request = request.GET.get("search_request")
    vacancies = FoundVacancies.objects.filter(search_request=search_request, negotiations=False)
    vacancies.update(negotiations=True)
    return HttpResponse("")

def get_vacancies_list(request):
    search_request = request.GET.get("search_request")
    vacancies = FoundVacancies.objects.filter(search_request=search_request, negotiations=False)
    context = {
        "vacancies":vacancies,
    }
    return render(request, "partials/tables/vacancies_list_table.html", context)

def vacancies_list(request):
    if request.htmx:
        search_request = request.GET.get("search_request")
        blacklist = request.GET.get("select_blacklist")
        if blacklist:
            vacancies = FoundVacancies.objects.filter(search_request=search_request, blacklist=blacklist)
        else:
            vacancies = FoundVacancies.objects.filter(search_request=search_request)
        context = {
            "vacancies": vacancies,
        }
        return render(request, "partials/tables/vacancies_list_table.html", context)
    else:    
        vacancies_list_active_link = "active"
        choices = FoundVacancies.SearchRequest.choices
        vacancies = FoundVacancies.objects.filter(search_request=choices[0][0])
        
        context = {
            "vacancies_list_active_link": vacancies_list_active_link,
            "choices": choices,
            "vacancies": vacancies,
        }
    return render(request, "hh_search/vacancies_list.html", context)

def find_employer_name(request):
    employer_name = request.GET.get("employer_name")
    vacancies = FoundVacancies.objects.filter(employer_name__icontains=employer_name)
    context = {
        "vacancies":vacancies
    }
    return render(request, "partials/tables/vacancies_list_table.html", context)

def dashboard(request):
    vacancies = FoundVacancies.objects.filter(blacklist=False)
    pagingator = Paginator(vacancies, 3)
    vacancies_page = pagingator.page(1)
    context = {
        "vacancies": vacancies_page,
    }
    return render(request, "hh_search/dashboard.html", context)

def get_bar_chart_data(request):
    bar_chart_data = FoundVacancies.objects.values("search_request").annotate(total=Count("search_request"))
    bar_chart_data = (
        pd.DataFrame(bar_chart_data)
        .to_json(orient="split") 
    )
    data = json.loads(bar_chart_data)
    return JsonResponse(data,safe=False)

def infine_scroll_table(request):
    employer_name = request.GET.get("employer_name")

    page = request.GET.get("page", 1)
    vacancies = FoundVacancies.objects.filter(blacklist=False, employer_name__icontains=employer_name)
    pagingator = Paginator(vacancies, 3)
    vacancies_page = pagingator.page(page)
    
    context = {
        "vacancies": vacancies_page,
    }
    return render(request, "partials/tables/infine_scroll.html", context)

def employer_filter_table(request):
    employer_name = request.GET.get("employer_name")
    page = request.GET.get("page", 1)
    vacancies = FoundVacancies.objects.filter(blacklist=False, employer_name__icontains=employer_name)
    pagingator = Paginator(vacancies, 3)
    vacancies_page = pagingator.page(page)
    
    context = {
        "vacancies": vacancies_page,
    }
    return render(request, "partials/tables/vacancies_list_table_dash.html", context)










