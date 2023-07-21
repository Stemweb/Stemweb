#!/bin/bash

cd /home/stemweb
# Wait for the database if necessary
if [ -n "${STEMWEB_DBHOST}" ]; then
    dbport=$STEMWEB_DBPORT
    if [ -z "${STEMWEB_DBPORT}" ]; then
        case $STEMWEB_DBENGINE in
            mysql)
            dbport="3306"
            ;;
            postgresql_psycopg2)
            dbport="5432"
            ;;
        esac
    fi
    echo "Waiting for ${STEMWEB_DBHOST}:${dbport} to come online"
    ./wait-for-it.sh "${STEMWEB_DBHOST}:${dbport}" -t 60 -- echo "######### Initialising Stemweb #########"
fi

# Do the necessary DB migrations
echo "######### Doing database migrations #########"
python manage.py makemigrations
python manage.py migrate --run-syncdb
python manage.py loaddata Stemweb/algorithms/init_algorithms.json
python manage.py loaddata Stemweb/files/files.json
#python manage.py loaddata Stemweb/home/fixtures/bootstrap.json

# Start celery worker
echo "######### Starting Celery worker #########"
#celery -A Stemweb worker --loglevel=DEBUG --config=settings &
celery -A Stemweb worker --config=settings &

# Start Django server
echo "######### Starting Django server #########"
python manage.py runserver 0.0.0.0:8000
