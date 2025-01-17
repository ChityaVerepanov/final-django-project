from decimal import Decimal
import xml.etree.ElementTree as ET
from django.contrib.sites import requests
from django.db.models import Count, Avg, F
from django.db.models.functions import ExtractYear
from django.shortcuts import render, redirect
import requests
import json
from django.db.models import Count
from collections import Counter
from .hh_ru_api import hh_api
from .models import Profession
from .parser import main

#берет данные и отрисовывает страницу

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


def home(request):
    #main()
    professions = Profession.objects.all()
    return render(request, 'main.html', {'professions': professions})

def redirect_to_home(request):
    return redirect('/home')

def return_general_statistics(request):
    vacancies_per_year = Profession.objects.annotate(year=ExtractYear('published_at')).values('year').annotate(
        count=Count('id')).order_by('year')

    vacancies_data = list(vacancies_per_year)
    salary_data = get_salary_dynamics()

    vacancies_by_city = Profession.objects.values('area_name').annotate(count=Count('id')).order_by('-count')
    vacancies_data_json = json.dumps(list(vacancies_by_city))

    top_skills = get_top_skills_all_years()
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies

    return render(request, 'general_statistics.html',
                  context={"vacancies_per_year": vacancies_data, "salary_data": salary_data, 'vacancies_by_city_json': vacancies_data_json, "top_skills": top_skills, 'current_theme': current_theme})




def get_salary_dynamics():
    # Агрегируем данные по годам в базе данных
    salary_data = (
        Profession.objects
        .filter(salary_from__lte=10000000, salary_to__lte=10000000)
        .annotate(year=ExtractYear('published_at'))
        .values('year')
        .annotate(average_salary=Avg(F('salary_from') + F('salary_to')))
    )

    average_salary_by_year = {entry['year']: float(entry['average_salary']) for entry in salary_data}
    return average_salary_by_year


def get_exchange_rate(currency, date):
    # Форматируем дату в нужный формат
    date_str = date.strftime('%d/%m/%Y')

    # URL для получения курсов валют
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"

    try:
        # Выполняем GET-запрос
        response = requests.get(url)
        response.raise_for_status()  # Проверяем на ошибки

        # Парсим XML-ответ
        root = ET.fromstring(response.content)

        # Ищем нужную валюту
        for valute in root.findall('Valute'):
            code = valute.find('CharCode').text
            if code == currency:
                value = float(valute.find('Value').text.replace(',', '.'))
                nominal = int(valute.find('Nominal').text)
                return value / nominal  # Возвращаем курс за единицу валюты

    except requests.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
    except ET.ParseError:
        print("Ошибка при парсинге XML-ответа")

    # Если валюта не найдена или произошла ошибка, возвращаем 1
    return 1


def return_demand(request):
    vacancies_per_year = Profession.objects.annotate(year=ExtractYear('published_at')).values('year').annotate(
        count=Count('id')).order_by('year')

    # Получаем данные о средней зарплате
    salary_data = get_salary_dynamics()

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

    # Преобразуем данные в JSON
    vacancies_data_json = json.dumps(list(vacancies_by_city))
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies

    # Возвращаем страницу с данными
    return render(request, "geography.html", {'vacancies_by_city_json': vacancies_data_json, 'current_theme': current_theme})

def return_skills(request):
    top_skills = get_top_skills_all_years()
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies
    return render(request, "skills.html", {"top_skills": top_skills, 'current_theme': current_theme})

def return_latest_vacancies(request):
    items = hh_api()
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies
    return render(request, "latest_vacancies.html",{'current_theme': current_theme, 'items': items,})