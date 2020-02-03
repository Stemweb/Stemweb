#!/usr/bin/env python
import os, sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Stemweb.settings")

    from django.core.management import execute_from_command_line

    from django.conf import settings

    if settings.DEBUG:
         if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
              import ptvsd
              ptvsd.enable_attach(address = ('0.0.0.0', 3000))
              #ptvsd.wait_for_attach()
              print " hopefully Attached remote debugger"
              #ptvsd.break_into_debugger()  

    execute_from_command_line(sys.argv)
