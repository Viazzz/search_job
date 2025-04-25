import requests
import json
from flatten_json import flatten
import pandas as pd
import time

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import FoundVacancies, UserTokenModel, ResumeId
from . import utils, filters
from . import tasks


@login_required
def find_vacancies(request):
    if request.htmx:
        search_request = request.GET.get("search_request")
        user_id = request.user.id

        tasks.find_vacancies.delay(user_id, search_request)
        vacancies = {}
        context = {
            "vacancies": vacancies,
        }
        return render(request, "partials/tables/vacancies_list_table.html", context)
    else:
        find_vacancies_active_link = "active"
        choices = FoundVacancies.SearchRequest.choices
        vacancies = FoundVacancies.objects.filter(
            search_request=choices[0][0], negotiations=False
        )
        context = {
            "find_vacancies_active_link": find_vacancies_active_link,
            "choices": choices,
            "vacancies": vacancies,
        }
        return render(request, "hh_search/find_vacancies.html", context)


@login_required
def get_authorization_code(request):
    authorization_code = request.GET.get("code", "")
    context = {
        "authorization_code": authorization_code,
    }
    return render(request, "hh_search/get_authorization_code.html", context)


@login_required
def change_blacklist(request, pk):
    vacancy = FoundVacancies.objects.get(pk=pk)
    if request.GET.get("blacklist"):
        vacancy.blacklist = True
        vacancy.save()
    else:
        vacancy.blacklist = False
        vacancy.save()
    return HttpResponse("")


@login_required
def employer_responded(request, pk):
    vacancy = FoundVacancies.objects.get(pk=pk)
    if request.GET.get("employer_responded"):
        vacancy.employer_responded = True
        vacancy.save()
    else:
        vacancy.employer_responded = False
        vacancy.save()
    return HttpResponse("")


@login_required
def send_responses_to_vacancies(request):
    search_request = request.GET.get("search_request")
    vacancies = FoundVacancies.objects.filter(
        search_request=search_request,
        negotiations=False,
        blacklist=False,
    )
    user_id = request.user.id
    user_tokens = list(UserTokenModel.objects.filter(user=user_id).values())
    access_token = user_tokens[0].get("access_token")
    resume = list(ResumeId.objects.filter(search_request=search_request).values())[0]
    resume_id = resume.get("resume_id")
    resume_message = resume.get("message")

    [
        utils.send_response_to_employer(
            access_token, vacancy.vacancies_id, resume_id, resume_message
        )
        for vacancy in vacancies
    ]

    return HttpResponse("")


@login_required
def get_vacancies_list(request):
    search_request = request.GET.get("search_request")
    vacancies = FoundVacancies.objects.filter(
        search_request=search_request, negotiations=False
    )
    context = {
        "vacancies": vacancies,
    }
    return render(request, "partials/tables/vacancies_list_table.html", context)


@login_required
def vacancies_list(request):
    if request.htmx:
        print(request.GET)
        filter_set = filters.FoundVacancisFilter(
            request.GET, queryset=FoundVacancies.objects.all()
        )
        context = {
            "vacancies": filter_set.qs,
        }
        return render(request, "partials/tables/vacancies_list_table.html", context)
    else:
        vacancies_list_active_link = "active"
        choices = FoundVacancies.SearchRequest.choices
        init_filter = {
            "search_request": "django",
        }
        filter_set = filters.FoundVacancisFilter(
            init_filter, queryset=FoundVacancies.objects.all()
        )
        vacancies = filter_set.qs
        form = filter_set.form
        context = {
            "vacancies_list_active_link": vacancies_list_active_link,
            "choices": choices,
            "vacancies": vacancies,
            "form": form,
        }
    return render(request, "hh_search/vacancies_list.html", context)


@login_required
def find_employer_name(request):
    employer_name = request.GET.get("employer_name")
    vacancies = FoundVacancies.objects.filter(employer_name__icontains=employer_name)
    context = {"vacancies": vacancies}
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
    bar_chart_data = (
        FoundVacancies.objects.filter(blacklist=False)
        .values("search_request")
        .annotate(total=Count("search_request"))
    )
    bar_chart_data = pd.DataFrame(bar_chart_data).to_json(orient="split")
    data = json.loads(bar_chart_data)
    return JsonResponse(data, safe=False)


def infine_scroll_table(request):
    filter = request.GET.get("search_field")

    page = request.GET.get("page", 1)
    vacancies = FoundVacancies.objects.filter(
        Q(blacklist=False),
        Q(employer_name__icontains=filter) | Q(search_request__icontains=filter),
    )
    pagingator = Paginator(vacancies, 3)
    vacancies_page = pagingator.page(page)

    context = {
        "vacancies": vacancies_page,
    }
    return render(request, "partials/tables/infine_scroll.html", context)


def employer_filter_table(request):
    filter = request.GET.get("search_field")
    page = request.GET.get("page", 1)
    vacancies = FoundVacancies.objects.filter(
        Q(blacklist=False),
        Q(employer_name__icontains=filter) | Q(search_request__icontains=filter),
    )
    pagingator = Paginator(vacancies, 3)
    vacancies_page = pagingator.page(page)

    context = {
        "vacancies": vacancies_page,
    }
    return render(request, "partials/tables/vacancies_list_table_dash.html", context)


@login_required
def change_negotiations(request, pk):
    vacancy = FoundVacancies.objects.get(pk=pk)
    if request.GET.get("negotiations"):
        vacancy.negotiations = True
        vacancy.save()
    else:
        vacancy.negotiations = False
        vacancy.save()
    return HttpResponse("")
