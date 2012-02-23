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

from django import forms

from recaptcha_works.widgets import RecaptchaWidget
from recaptcha_works import settings
from recaptcha_works.exceptions import RecaptchaError
from recaptcha_works.utils import validate_recaptcha


class RecaptchaField(forms.Field):
    
    default_error_messages = {
        'required': u'Please enter the CAPTCHA solution.',
        'invalid': u'An incorrect CAPTCHA solution was entered.',
        'no-remote-ip': u'CAPTCHA failed due to no visible IP address.',
        'challenge-error': u'An error occurred with the CAPTCHA service - try '
            'refreshing.',
        'unknown-error': u'The CAPTCHA service returned the following error: '
            '%(code)s.',
    }

    def __init__(self, private_key=None, public_key=None, use_ssl=False,
                recaptcha_options=None, *args, **kwargs):
        """Field constructor
        
        The optional ``public_key`` argument can be used to override the
        default use of the project-wide ``RECAPTCHA_PUBLIC_KEY`` setting.
        
        The optional ``private_key`` argument can be used to override the
        default use of the project-wide ``RECAPTCHA_PRIVATE_KEY`` setting.
        
        The optional ``use_ssl`` argument can be used to override the default
        use of the project-wide ``RECAPTCHA_USE_SSL`` setting.
        
        The optional ``recaptcha_options`` argument can be used to override
        the default project wide ``RECAPTCHA_OPTIONS`` setting.
        
        """
        self.private_key = private_key or settings.RECAPTCHA_PRIVATE_KEY
        self.use_ssl = use_ssl or settings.RECAPTCHA_USE_SSL
        kwargs['widget'] = RecaptchaWidget(public_key, use_ssl, recaptcha_options)
        super(RecaptchaField, self).__init__(*args, **kwargs)

    def clean(self, value):
        
        value = super(RecaptchaField, self).clean(value)
        challenge, response, remote_ip = value
        
        # Validation overrides
        if settings.RECAPTCHA_VALIDATION_OVERRIDE:
            return value
        if not response and not self.required:
            return value
        
        if not challenge:
            raise forms.ValidationError(self.error_messages['challenge-error'])
        if not response:
            raise forms.ValidationError(self.error_messages['required'])
        if not remote_ip:
            raise forms.ValidationError(self.error_messages['no-remote-ip'])
        try:
            value = validate_recaptcha(remote_ip, challenge, response,
                                       self.private_key, self.use_ssl)
        except RecaptchaError, e:
            if e.code == 'incorrect-captcha-sol':
                raise forms.ValidationError(self.error_messages['invalid'])
            raise forms.ValidationError(self.error_messages['unknown-error'] %
                                        {'code': e.code})
        return value

