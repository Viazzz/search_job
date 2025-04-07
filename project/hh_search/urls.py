from django.urls import path

from . import views


app_name = "work_search"


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("find_vacancies/", views.find_vacancies, name="find_vacancies"),
    path("change_blacklist/<int:pk>/", views.change_blacklist, name="change_blacklist"),
    path("employer_responded/<int:pk>/", views.employer_responded, name="employer_responded"),
    path("send_responses_to_vacancies/", views.send_responses_to_vacancies, name="send_responses_to_vacancies"),
    path("get_vacancies_list/", views.get_vacancies_list, name="get_vacancies_list"),

    path("vacancies_list/", views.vacancies_list, name="vacancies_list"),
    path("find_employer_name/", views.find_employer_name, name="find_employer_name"),
    path("get_bar_chart_data/", views.get_bar_chart_data, name="get_bar_chart_data"),
    path("infine_scroll_table/", views.infine_scroll_table, name="infine_scroll_table"),
    path("employer_filter_table/", views.employer_filter_table, name="employer_filter_table"),

]
