#!/usr/bin/env python
# -*- coding: utf-8 -*-

# First copy this file as lstring.py then
# add information of your own local database and 
# other settings here.
 
# These are locally relevant database and other settings
# strings from settings.py. These need to be in the same 
# folder as settings.py.

# IMPORTANT: DO NOT COMMIT lstrings.py INTO REPOSITORY
# NOR DO NOT REMOVE lstring.py FROM .gitignore IN ANY
# CIRCUMSTANCES. 

# Local db admin name and email. Don't really need these
# in local testing.
db_admin = ''
db_email = ''

# Local db engine (mysql, sqlite3 or postgresql_psycopg2)
# postgresql_psycopg2 needs psycopg2-packet installed to 
# work. Add the name of the engine after already filled text.
db_engine = 'django.db.backends.'

# Name of your db. In sqlite3 this is absolute path for
# your database-file.
db_name = ''

# Your db user. Not needed in sqlite3
db_user = ''

# Your db password. Not needed in sqlite3
db_pwd = ''

# Host, leave blank if db is on local computer.
db_host = ''

# Port to your db. Can be left blank
db_port = ''

# name of your ROOT_URLCONF. Needs to be in here, because
# of some inconsisties in package naming on linux vs. mac.
# This is most likely stemweb.urls or Stemweb.urls.
root_urls = ''

# Veeerry secret key.
secret_key = ''