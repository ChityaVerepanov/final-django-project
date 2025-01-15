from django.db.models import Count
from django.db.models.functions import ExtractYear
from django.shortcuts import render, redirect
from django.template.context_processors import request
import json
from django.db.models import Count
from collections import Counter

from .models import Profession
from .parser import main

#берет данные и отрисовывает страницу
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

    top_skills = get_top_skills_all_years()
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies

    return render(request, 'general_statistics.html',
                  context={"vacancies_per_year": vacancies_data, "top_skills": top_skills, 'current_theme': current_theme})

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

def return_demand(request):
    vacancies_per_year = Profession.objects.annotate(year=ExtractYear('published_at')).values('year').annotate(
        count=Count('id')).order_by('year')

    vacancies_data = list(vacancies_per_year)
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies

    return render(request, "demand.html", {"vacancies_per_year": vacancies_data, 'current_theme': current_theme})

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
    current_theme = request.COOKIES.get('theme', 'light-theme')  # Получаем тему из cookies
    return render(request, "latest_vacancies.html",{'current_theme': current_theme})
