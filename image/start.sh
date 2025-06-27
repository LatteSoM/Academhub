#!/bin/bash
DJANGO_SUPERUSER_EMAIL=${SUPERUSER:-admin@admin.admin}
DJANGO_SUPERUSER_PASSWORD=${SUPERUSER_PASSWORD:-admin}
echo "Collection static"
python manage.py collectstatic --noinput

echo "Make migration"
python manage.py makemigrations --noinput

echo "Make migrate"
python manage.py migrate --noinput

echo "Create superuser"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell

echo "Start"
gunicorn Academhub.wsgi:application --bind 0.0.0.0:8000