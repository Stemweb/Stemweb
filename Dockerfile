# install everything based on image "python:3.7"

FROM python:3.7
ENV DEBIAN_FRONTEND=noninteractive

#========== create the technical user "stemweb" with sudo-right  =======
RUN adduser stemweb --gecos ""
RUN usermod -aG sudo stemweb
WORKDIR /home/stemweb

#=========== copy configured stemweb repository from host server =======
COPY manage.py .
COPY docker-entrypoint.sh .
COPY Stemweb Stemweb
COPY Stemweb/requirements/requirements.txt requirements.txt

#======================== install tools ================================
RUN apt-get update && apt-get -y install graphviz libgraphviz-dev pkg-config wget libffi-dev libssl-dev r-base-core curl vim tree python3-dev sed gawk sudo gcc 
# with debugging tools:
#RUN apt-get update && apt-get -y install graphviz libgraphviz-dev pkg-config wget libffi-dev libssl-dev r-base-core curl vim tree python3-dev sed gawk sudo gdb gcc gdbserver
RUN pip install -U setuptools
RUN pip install pyopenssl ndg-httpsclient pyasn1 rpy2 mysqlclient ptvsd pygraphviz pymysql djangorestframework

#===================== install requirements ============================
RUN pip install -r requirements.txt

#=====  compile & build the c-extension "binarysankoff" for python =====
WORKDIR /home/stemweb/Stemweb/algorithms/rhm
#RUN gcc -I/usr/local/include/python3.8/ -I/usr/include/python3.8 -lpython3.8 -I/usr/local/include -L/usr/local/lib -fPIC -g -Wall -c binarysankoff_linux.c
#RUN gcc -I/usr/local/include/python3.7/ -I/usr/include/python3.7 -lpython3.7 -I/usr/local/include -L/usr/local/lib -fPIC -g -Wall -c binarysankoff_linux.c
#RUN gcc -shared -fPIC -Wall -I/usr/local/include -L/usr/local/lib binarysankoff_linux.o -o binarysankoff.so -lz

RUN python setup_c_binarysankoff.py build
RUN python setup_c_binarysankoff.py install

#=====  compile & build the c-extension "adding" for python ============
#== "adding" is a  toy app used to test implementation of c-extension ==

WORKDIR /home/stemweb/Stemweb/algorithms
#RUN gcc -I/usr/local/include/python3.7/ -I/usr/include/python3.7 -lpython3.7 -I/usr/local/include -L/usr/local/lib -fPIC -g -Wall -c addingmodule.c
#RUN gcc -shared -fPIC -Wall -I/usr/local/include -L/usr/local/lib addingmodule.o -o adding.so

RUN python setup_c_addingmodule.py build
# special build for debugging:
#RUN python setup_c_addingmodule.py build_ext --inplace -j4 --with-debugging-symbols

RUN python setup_c_addingmodule.py install

#============ make the log directory and set permissions ===============
WORKDIR /home/stemweb
RUN mkdir Stemweb/logs && chown -R stemweb:stemweb .

#============ for reporting errors in c-code ===========================
ENV PYTHONFAULTHANDLER=1

#====================== start the server ===============================
# EXPOSE port 3000 for debugging access from outside of the docker container,
# EXPOSE port 8000 for the web site
# EXPOSE port 51000 as fixed http-request outbound src-port
#EXPOSE 3000 8000 51000
EXPOSE 8000 51000
USER stemweb
ENTRYPOINT ["./docker-entrypoint.sh"]
