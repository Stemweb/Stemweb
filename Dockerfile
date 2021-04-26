# install everything based on image "python:3.7"

FROM python:3.7
LABEL vendor=DHUniWien
ENV DEBIAN_FRONTEND=noninteractive

#========== create the technical user "stemweb" with sudo-right  =======
RUN adduser stemweb --gecos ""
RUN usermod -aG sudo stemweb
WORKDIR /home/stemweb

#======================== install tools ================================
RUN apt-get update && apt-get -y install graphviz libgraphviz-dev pkg-config wget libffi-dev libssl-dev r-base-core curl vim tree python-dev
RUN pip install -U setuptools
RUN pip install pyopenssl ndg-httpsclient pyasn1 rpy2==2.8.6 mysqlclient ptvsd pygraphviz pymysql

#===================== install requirements ============================
COPY Stemweb/requirements/requirements.txt requirements.txt
RUN pip install -r requirements.txt

#=========== copy configured stemweb repository from host server =======
COPY manage.py .
COPY docker-entrypoint.sh .
COPY Stemweb Stemweb

#=====  compile & build the c-extension "binarysankoff" for python =====
# assumption: in order to get rid of error messages,
# initialization of relevant variables as floating-point numbers in binarysankoff_linux.c
# is already done in the repository on the host server
WORKDIR /home/stemweb/Stemweb/algorithms/rhm
RUN gcc -I/usr/local/include/python3.7/ -I/usr/include/python3.7 -lpython3.7 -I/usr/local/include -L/usr/local/lib -fPIC -g -Wall -c binarysankoff_linux.c
RUN gcc -shared -fPIC -Wall -I/usr/local/include -L/usr/local/lib binarysankoff_linux.o -o binarysankoff.so -lz

#============ make the log directory and set permissions ===============
WORKDIR /home/stemweb
RUN mkdir Stemweb/logs && chown -R stemweb:stemweb .

#====================== start the server ================================
# EXPOSE port 3000 for debugging access from outside of the docker container,
# EXPOSE port 8000 for the web site
# EXPOSE port 51000 as fixed http-request outbound src-port
# EXPOSE 3000 8000 51000
EXPOSE 8000 51000
USER stemweb
ENTRYPOINT ["./docker-entrypoint.sh"]
