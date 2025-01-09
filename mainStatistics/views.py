from django.shortcuts import render
from .models import Profession
from .parser import main

#берет данные и отрисовывает страницу
def home(request):
    #main()
    professions = Profession.objects.all()
    return render(request, 'main.html', {'professions': professions})

# Create your views here.
