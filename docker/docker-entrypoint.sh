#!/bin/bash

# Wait for MySQL to come up
echo "######### waiting 60 secs for MySQL to come up #########"
now=$(date)
echo $now
sleep 60 
echo "######### waiting finihed #########"
now=$(date)
echo $now

#su stemweb
#actualuser=$(whoami)
#echo $actualuser        # should be: stemweb

# Do the necessary DB migrations
echo "######### Doing database migrations #########"
cd /home/stemweb
python manage.py makemigrations
python manage.py migrate --run-syncdb
python manage.py loaddata Stemweb/algorithms/init_algorithms.json
python manage.py loaddata Stemweb/files/files.json
#python manage.py loaddata Stemweb/home/fixtures/bootstrap.json

# Start celery worker
echo "######### Starting Celery worker #########"
#celery -A Stemweb worker &
#celery -A Stemweb worker --loglevel=DEBUG --config=settings &
celery -A Stemweb worker --config=settings &

# Start Django server
echo "######### Starting Django server #########"
python manage.py runserver 0.0.0.0:8000
