from datetime import datetime, time
from datetime import datetime
import time
import xml.etree.ElementTree as ET
from decimal import Decimal

from django.contrib.sites import requests
from django.db.models import Count, Avg, F, Q
from django.db.models.functions import ExtractYear, ExtractMonth
from django.shortcuts import render, redirect
import requests
import json
from collections import Counter, defaultdict
from .hh_ru_api import hh_api
from .models import Profession, CurrencyRate


#from .parser import *

def home(request):
    #main()
    #fill_currency_table()
    #CurrencyRate.objects.all().delete()
    professions = Profession.objects.all()
    return render(request, 'main.html', {'professions': professions})


def return_general_statistics(request):
    vacancies_per_year = Profession.objects.annotate(year=ExtractYear('published_at')).values('year').annotate(
        count=Count('id')).order_by('year')
    vacancies_data = list(vacancies_per_year)

    salary_by_year_data = get_average_salaries_by_year()
    salary_by_city_data = get_average_salary_by_city()

    vacancies_by_city = Profession.objects.values('area_name').annotate(count=Count('id')).order_by('-count')
    vacancies_data_json = json.dumps(list(vacancies_by_city))

    top_skills = get_top_skills_all_years()
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies


    return render(request, 'general_statistics.html',
                  context={
                      "vacancies_per_year": vacancies_data,
                      "salary_data": salary_by_year_data,
                      "vacancies_by_city_json": vacancies_data_json,
                      "top_skills": top_skills,
                      "salary_by_city": salary_by_city_data,
                      "current_theme": current_theme
                  })


def return_demand(request):
    vacancies_per_year = Profession.objects.annotate(year=ExtractYear('published_at')).values('year').annotate(
        count=Count('id')).order_by('year')

    # Получаем данные о средней зарплате
    salary_data = get_average_salaries_by_year()

    vacancies_data = list(vacancies_per_year)
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies

    return render(request, "demand.html", {
        "vacancies_per_year": vacancies_data,
        "salary_data": salary_data,
        'current_theme': current_theme
    })


def return_geography(request):
    # Получаем данные о вакансиях по городам
    vacancies_by_city = Profession.objects.values('area_name').annotate(count=Count('id')).order_by('-count')

    salary_by_city = get_average_salary_by_city()

    # Преобразуем данные в JSON
    vacancies_data_json = json.dumps(list(vacancies_by_city))
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies

    # Возвращаем страницу с данными
    return render(request, "geography.html", {'vacancies_by_city_json': vacancies_data_json, "salary_by_city": salary_by_city, 'current_theme': current_theme})

def return_skills(request):
    top_skills = get_top_skills_all_years()
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies
    return render(request, "skills.html", {"top_skills": top_skills, 'current_theme': current_theme})

def return_latest_vacancies(request):
    items = hh_api()
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies
    return render(request, "latest_vacancies.html",{'current_theme': current_theme, 'items': items,})






def redirect_to_home(request):
    return redirect('/home')


def get_average_salary_by_city():
    # Получаем все вакансии, фильтруя по зарплате
    vacancies = Profession.objects.filter(salary_from__lte=10000000, salary_to__lte=10000000)

    # Создаем словарь для хранения средних зарплат по городам
    average_salaries = {}

    for vacancy in vacancies:
        # Получаем курс валют на первое число месяца вакансии
        first_day_of_month = vacancy.published_at.replace(day=1)
        currency_rate = CurrencyRate.objects.filter(date__lte=first_day_of_month).order_by('-date').first()

        if currency_rate:
            # Конвертируем зарплату в рубли
            salary_in_rub = 0
            if vacancy.salary_currency == 'USD':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.usd
            elif vacancy.salary_currency == 'EUR':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.eur
            elif vacancy.salary_currency == 'KZT':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.kzt
            elif vacancy.salary_currency == 'UAH':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.uah
            elif vacancy.salary_currency == 'BYR':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.byr
            elif vacancy.salary_currency == 'AZN':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.azn
            elif vacancy.salary_currency == 'UZS':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.uzs
            elif vacancy.salary_currency == 'KGS':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.kgs
            elif vacancy.salary_currency == 'GEL':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.gel
            else:
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2  # Если валюта рубли

            city = vacancy.area_name  # Получаем город
            if city not in average_salaries:
                average_salaries[city] = {'total_salary': 0, 'count': 0}

            average_salaries[city]['total_salary'] += float(salary_in_rub)
            average_salaries[city]['count'] += 1

    # Рассчитываем средние значения
    for city, data in average_salaries.items():
        average_salaries[city] = data['total_salary'] / data['count']

    # Сортируем по убыванию
    sorted_average_salaries = dict(sorted(average_salaries.items(), key=lambda item: item[1], reverse=True))

    return sorted_average_salaries

def get_average_salaries_by_year():
    # Получаем все вакансии, фильтруя по зарплате
    vacancies = Profession.objects.filter(salary_from__lte=10000000, salary_to__lte=10000000)

    # Создаем словарь для хранения средних зарплат по годам
    average_salaries = {}

    for vacancy in vacancies:
        # Получаем курс валют на первое число месяца вакансии
        first_day_of_month = vacancy.published_at.replace(day=1)
        currency_rate = CurrencyRate.objects.filter(date__lte=first_day_of_month).order_by('-date').first()

        if currency_rate:
            # Конвертируем зарплату в рубли
            salary_in_rub = 0
            if vacancy.salary_currency == 'USD':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.usd
            elif vacancy.salary_currency == 'EUR':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.eur
            elif vacancy.salary_currency == 'KZT':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.kzt
            elif vacancy.salary_currency == 'UAH':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.uah
            elif vacancy.salary_currency == 'BYR':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.byr
            elif vacancy.salary_currency == 'AZN':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.azn
            elif vacancy.salary_currency == 'UZS':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.uzs
            elif vacancy.salary_currency == 'KGS':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.kgs
            elif vacancy.salary_currency == 'GEL':
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2 * currency_rate.gel
            else:
                salary_in_rub = (vacancy.salary_from + vacancy.salary_to) / 2  # Если валюта рубли

            year = vacancy.published_at.year
            if year not in average_salaries:
                average_salaries[year] = {'total_salary': 0, 'count': 0}

            average_salaries[year]['total_salary'] += float(salary_in_rub)  # Преобразуем в float чтобы js скушал
            average_salaries[year]['count'] += 1

    # Рассчитываем средние значения
    for year, data in average_salaries.items():
        average_salaries[year] = data['total_salary'] / data['count']

    return average_salaries





def get_top_skills_all_years():
    # Получаем все профессии
    professions = Profession.objects.all()

    # Собираем все ключевые навыки
    all_skills = []
    for profession in professions:
        skills = profession.key_skills.split('\n')  # Предполагаем, что навыки разделены запятыми
        all_skills.extend(skill.strip() for skill in skills)

    # Подсчитываем частоту навыков
    skill_counts = Counter(all_skills)

    # Получаем ТОП-20 навыков
    top_skills = skill_counts.most_common(20)
    top_skills_json = json.dumps(top_skills)
    return top_skills_json
