## [RU](#это-простой-учебный-проект-для-университета) / [EN](#this-is-a-simple-educational-project-for-the-university)


# Это простой учебный проект для университета
## Инструкция по запуску:

1. Скачайте / клонируйте репозиторий на вашу локальную машину:
```bash
https://github.com/ChityaVerepanov/final-django-project.git
```
2. Перейдите в папку с проектом:
```bash
cd final-django-project
```
3. Создайте виртуальное окружение:

  ```bash
  python -m venv your_venv
  ```
4. Активируйте виртуальное окружение:

  - Для Windows:
    
    ```bash
    your_venv\Scripts\activate
    ```
  - Для macOs и Linux:

    ```bash
    source your_venv/bin/activate
    ```

5. Установите необходимые зависимости из файла ```requirements.txt```:
```bash
pip install -r requirements.txt
```

6. Выполните миграции:
```bash
python manage.py migrate
```

7. Запустите сервер:
```bash
python manage.py runserver
```
Сервер будет запущен по умолчанию на ```http://127.0.0.1:8000/```

    
## Страницы:
* **Main** page - /home
* **General statistics** page - /general_statistics
* **Demand** page - /demand
* **Geography** page - /geography
* **Skills** page - /skills
* **Latest vacancies** page - /latest_vacancies

***


# This is a simple educational project for the university
## Instructions for launch:

1. Download / clon the repository on your local machine:
```bash
https://github.com/chityaverepanov/final-django-project.git
```
2. Go to the folder with the project:
```bash
cd final-django-project
```
3. Create a virtual environment:

  ```bash
  python -m venv your_venv
  ```
4. Activate the virtual environment:

  - For Windows:
    
    ```bash
    your_venv\scripts\activate
    ```
  - For MacOS and Linux:

    ```bash
    Source your_venv/bin/activate
    ```

5. Set the necessary dependencies from the file ```requirements.txt```:
```bash
pip install -r requirements.txt
```

7. Perform migrations:
```bash
python manage.py migrate
```

7. Run the server:
```bash
python manage.py runserver
```
The server will be launched by default on ```http: //127.0.0.1: 8000/```

    
## Pages:
* **Main** page - /home
* **General statistics** page - /general_statistics
* **Demand** page - /demand
* **Geography** page - /geography
* **Skills** page - /skills
* **Latest vacancies** page - /latest_vacancies
