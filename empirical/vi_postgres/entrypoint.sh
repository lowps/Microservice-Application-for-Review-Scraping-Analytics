#!/bin/sh

echo "Verifying if PostgreSQL is healthy"

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do 
        sleep 0.1
    done

    echo "PostgreSQL started"

fi

echo "PostgreSQL is healthy"
echo PostgreSQL started"

exec "$@"