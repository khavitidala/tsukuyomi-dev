# ScoreMaster
A backend for RPLGDC lab project using DjangoRESTframework.

## How to
1. Clone this repository.
2. Create your environment variable as well as a postgresql database. Take a look at the config/.sample_env for example.
3. Make sure you've installed python as well as pip on your local environtment.
4. Install pipenv using python package manager:
```
$ pip install pipenv
```
4. Install all dependencies using pipenv:
```
$ pipenv install
```
5. Migrate the database, create superuser, then run on your localhost:
```
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py runserver

Django version 3.2.6, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```
6. You can use your favorite tools to test the RESTful API. Fyi, you can find the documentation of this RESTful API at http://127.0.0.1:8000/redoc/
