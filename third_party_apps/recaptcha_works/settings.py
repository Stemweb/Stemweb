# -*- coding: utf-8 -*-
#
#  This file is part of django-recaptcha-works.
#
#  django-recaptcha-works provides a Django form field that integrates the
#  reCaptcha service.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-recaptcha-works
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-recaptcha-works
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
#
#  Based on the code snippet #1644 as published on:
#    - http://djangosnippets.org/snippets/1644/
#
#  Copyright 2009-2010 Chris Beaven, http://smileychris.com/
#
#  Licensed under the BSD License.
#
#  Redistribution and use in source and binary forms, with or without modification,
#  are permitted provided that the following conditions are met:
#
#      1. Redistributions of source code must retain the above copyright notice, 
#         this list of conditions and the following disclaimer.
#      
#      2. Redistributions in binary form must reproduce the above copyright 
#         notice, this list of conditions and the following disclaimer in the
#         documentation and/or other materials provided with the distribution.
#
#      3. Neither the name of Django nor the names of its contributors may be used
#         to endorse or promote products derived from this software without
#         specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#  ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from django.conf import settings


RECAPTCHA_PRIVATE_KEY = getattr(settings, 'RECAPTCHA_PRIVATE_KEY', '')
RECAPTCHA_PUBLIC_KEY = getattr(settings, 'RECAPTCHA_PUBLIC_KEY', '')
RECAPTCHA_USE_SSL = getattr(settings, 'RECAPTCHA_USE_SSL', True)

# See the following page for valid options:
# http://code.google.com/apis/recaptcha/docs/customization.html
_RECAPTCHA_OPTIONS = {
    'theme': 'red',
    'lang': 'en',
    'tabindex': 0,
    #'custom_translations': {},
    #'custom_theme_widget': None
    }
RECAPTCHA_OPTIONS = getattr(settings, 'RECAPTCHA_OPTIONS', _RECAPTCHA_OPTIONS)

_RECAPTCHA_HTML = u'''
%(options)s
<script type="text/javascript"
   src="%(proto)s://www.google.com/recaptcha/api/challenge?k=%(public_key)s">
</script>
<noscript>
   <iframe src="%(proto)s://www.google.com/recaptcha/api/noscript?k=%(public_key)s"
       height="300" width="500" frameborder="0"></iframe><br>
   <textarea name="recaptcha_challenge_field" rows="3" cols="40">
   </textarea>
   <input type="hidden" name="recaptcha_response_field" value="manual_challenge">
</noscript>
'''
RECAPTCHA_HTML = getattr(settings, 'RECAPTCHA_HTML', _RECAPTCHA_HTML)

# RECAPTCHA_VALIDATION_OVERRIDE, if set to True, makes it possible to override
# the validation of the reCaptcha field. This is supposed to be used when
# testing forms.
RECAPTCHA_VALIDATION_OVERRIDE = getattr(settings, 'RECAPTCHA_VALIDATION_OVERRIDE', False)

