#!/bin/bash

echo "Waiting for database to be ready..."
python manage.py wait_for_db

echo "Running database migrations..."
python manage.py migrate

echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

echo "Starting Django application..."
if [ $# -eq 0 ]; then
    exec python manage.py runserver 0.0.0.0:8000
else
    exec "$@"
fi
