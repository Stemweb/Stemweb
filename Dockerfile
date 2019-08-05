# stemweb_Dockerfile_2
# install everything based on image "ubuntu:bionic"

FROM python:2.7
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update && apt-get -y install graphviz wget sqlite virtualenv libffi-dev libssl-dev
RUN pip install -U setuptools
RUN pip install pyopenssl ndg-httpsclient pyasn1 

#================= create the technical user "stemweb" =================
RUN adduser stemweb --gecos ""
WORKDIR /home/stemweb
COPY Stemweb/requirements/requirements.txt requirements.txt
RUN pip install -r requirements.txt

#=========== copy configured stemweb repository from host server =======
COPY manage.py .
COPY Stemweb Stemweb

#=====  compile & build the c-extension "binarysankoff" for python =====
# assumption: in order to get rid of error messages, 
# initialization of relevant variables as floating-point numbers in binarysankoff_linux.c
# is already done in the repository on the host server
WORKDIR Stemweb/algorithms/rhm
RUN gcc -I/usr/local/include/python2.7/ -I/usr/include/python2.7 -lpython2.7 -I/usr/local/include -L/usr/local/lib -fPIC -g -Wall -c binarysankoff_linux.c
RUN gcc -shared -fPIC -Wall -I/usr/local/include -L/usr/local/lib binarysankoff_linux.o -o binarysankoff.so -lz

#============ make the log directory and set permissions ===============
WORKDIR /home/stemweb
RUN mkdir Stemweb/logs && chown -R stemweb Stemweb/logs
USER stemweb

#============ create/start database in background ======================
RUN mkdir sqlite3db
RUN sqlite3 sqlite3db/stemweb_v01.db &

#====================== syncdb =========================================
RUN python manage.py migrate

#===================== start the server ================================
EXPOSE 8000
CMD python manage.py runserver 0.0.0.0:8000
