import pymysql
from ._celery import celery_app

pymysql.install_as_MySQLdb()

#__all__ = ('celery_app',)
__all__ = ['celery_app']


