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

import httplib
from django.utils.http import urlencode

from recaptcha_works.exceptions import RecaptchaError


def validate_recaptcha(remote_ip, challenge, response, private_key, use_ssl):
    assert challenge, 'No challenge was provided for reCaptcha validation'
    # Request validation from recaptcha.net
    params = dict(privatekey=private_key, remoteip=remote_ip,
                  challenge=challenge, response=response)
    params = urlencode(params)
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    if use_ssl:
        conn = httplib.HTTPSConnection("www.google.com")
    else:
        conn = httplib.HTTPConnection("www.google.com")
    conn.request("POST", "/recaptcha/api/verify", params, headers)
    response = conn.getresponse()
    if response.status == 200:
        data = response.read()
    else:
        data = ''
    conn.close()
    # Validate based on response data
    result = data.startswith('true')
    if not result:
        bits = data.split('\n', 2)
        error_code = ''
        if len(bits) > 1:
            error_code = bits[1]
        raise RecaptchaError(error_code)
    # Return dictionary
    return result


def post_payload_add_recaptcha_remote_ip_field(request):
    if request.method == 'POST':
        if 'recaptcha_challenge_field' in request.POST and 'recaptcha_response_field' in request.POST:
            # This is a recaptcha protected form
            data = request.POST.copy()
            data['recaptcha_remote_ip_field'] = request.META['REMOTE_ADDR']
            request.POST = data
    return request

