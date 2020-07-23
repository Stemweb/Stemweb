# install everything based on image "python:2.7"

FROM python:2.7
ENV DEBIAN_FRONTEND=noninteractive 

#========== create the technical user "stemweb" with sudo-right  =======
RUN adduser stemweb --gecos ""
RUN usermod -aG sudo stemweb
WORKDIR /home/stemweb
 
#=========== copy configured stemweb repository from host server =======
COPY manage.py .
COPY Stemweb Stemweb
COPY Stemweb/requirements/requirements.txt requirements.txt

#========= replace apt sources file and add public key =================
RUN rm /etc/apt/sources.list
COPY apt_sources.list /etc/apt/sources.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32

#======================== install tools ================================
RUN apt-get update && apt-get -y install graphviz libgraphviz-dev pkg-config wget libffi-dev libssl-dev r-base-core curl vim tree python-dev  mysql-server libmysqlclient-dev redis-server httpie
RUN pip install -U setuptools
RUN pip install pyopenssl ndg-httpsclient pyasn1 rpy2==2.8.6 mysqlclient ptvsd pygraphviz ete2 pymysql djangorestframework==3.9.4 httplib2

#===================== install requirements ============================
RUN pip install -r requirements.txt

#=====  compile & build the c-extension "binarysankoff" for python =====
# assumption: in order to get rid of error messages, 
# initialization of relevant variables as floating-point numbers in binarysankoff_linux.c
# is already done in the repository on the host server
WORKDIR /home/stemweb/Stemweb/algorithms/rhm
RUN gcc -I/usr/local/include/python2.7/ -I/usr/include/python2.7 -lpython2.7 -I/usr/local/include -L/usr/local/lib -fPIC -g -Wall -c binarysankoff_linux.c
RUN gcc -shared -fPIC -Wall -I/usr/local/include -L/usr/local/lib binarysankoff_linux.o -o binarysankoff.so -lz

#============ make the log directory and set permissions ===============
WORKDIR /home/stemweb
RUN mkdir Stemweb/logs && chown -R stemweb:stemweb .

#============= start mysql server as a service/daemon && create the mysql DB and DB-user with grants =============
#============= then migrate/syncdb, init algorithm tables, import files, reenable foreign key checks  ====
COPY createMysqlDBandUserWithGrants.sql .
RUN chown -R stemweb:stemweb .
RUN service mysql start &&  ./createMysqlDBandUserWithGrants.sql && su stemweb && \
    python manage.py makemigrations && \ 
    python manage.py migrate --run-syncdb && \ 
    python manage.py loaddata Stemweb/algorithms/init_algorithms.json && \
    python manage.py loaddata Stemweb/files/files.json && \
    python manage.py loaddata Stemweb/home/fixtures/bootstrap.json && \
    mysql -D stemwebdb_v1 -u stemweb -pChangeMe -e "SET GLOBAL FOREIGN_KEY_CHECKS = 1"

#================= configure the redis-server ===========================
#=== redis is used as message broker and as result backend for celery ===
RUN sed -i '0,/supervised no/! s/supervised no/supervised systemd/' /etc/redis/redis.conf


#====================== start the server ================================
# EXPOSE port 3000 for debugging access from outside of the docker container, 
# EXPOSE port 8000 for the web site
# EXPOSE port 80 for the stemmaweb.net RESTapi endpoint outside of the docker container // needed?
# EXPOSE port 443 for the https://stemmaweb.net RESTapi endpoint outside of the docker container // needed?
# EXPOSE port 51000 as fixed http-request outbound src-port
EXPOSE 3000 8000 80 51000 443
USER root
CMD service mysql start && \
    service redis-server start && \
    (celery worker -A Stemweb &) ; \ 
    python manage.py runserver 0.0.0.0:8000 