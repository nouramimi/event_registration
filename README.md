# event_registration

python -m venv myenv

myenv\Scripts\activate


pip install Django
python -m pip install Pillow

django-admin startproject event_scheduling


cd event_scheduling

python manage.py startapp events

code .
python manage.py makemigrations
python manage.py migrate

python manage.py startapp users



python manage.py runserver


