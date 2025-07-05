#!/bin/sh


echo "Verifying if PostgreSQL is healthy"

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do 
        sleep 0.1
    done

    echo "PostgreSQL started"

fi

echo "Running makemigrations command..."
python manage.py makemigrations --no-input

echo "Running migrate command..."
python manage.py migrate --no-input

echo "Running collectstatic command..."
python manage.py collectstatic --no-input

echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:8000 --workers 9 app.wsgi 








