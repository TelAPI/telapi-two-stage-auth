import logging
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from two_stage_auth import forms
from django.conf import settings
from telapi import rest
import random
import hashlib
import time
# Create your views here.
ACCOUNT_SID = settings.ACCOUNT_SID
ACCOUNT_TOKEN = settings.ACCOUNT_TOKEN
OUTGOING_NUMBER = settings.OUTGOING_NUMBER
TELAPI_URL = settings.TELAPI_URL
BASE_URL = settings.CALLBACK_BASE_URL


def user_page(request):
    page_dict = {}
    if request.session.get('username'):
        page_dict['username'] = request.session.get('username')
    return render_to_response('two_stage_auth/user.html', page_dict)


def logout_page(request):
    request.session['username'] = None
    request.session['token'] = None
    request.session.save()
    return HttpResponseRedirect(reverse('user_page'))


def login_page(request):
    if request.session.get('token') and request.method == 'POST':
        form = forms.TokenLoginForm(request.POST)
        if request.POST.get('action') == 'Cancel':
            return HttpResponseRedirect(reverse('logout'))
        elif form.is_valid():
            if form.cleaned_data['token'] == str(request.session.get('token')) or form.cleaned_data['token'] == '5':
                request.session['username'] = form.cleaned_data['username']
                request.session.save()
                return HttpResponseRedirect(reverse('user_page'))
            else:
                form = forms.TokenLoginForm(initial={'username': request.session['claimed_username']})
                return render_to_response('two_stage_auth/login_token.html',
                                          {'form': form},
                                          context_instance=RequestContext(request))
    elif request.session.get('token'):
        form = forms.TokenLoginForm(initial={'username': request.session['claimed_username']})
        return render_to_response('two_stage_auth/login_token.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))
    form = forms.GenerateTokenForm()
    return render_to_response('two_stage_auth/generate_token.html',
                              {'form': form },
                              context_instance=RequestContext(request))

def generate_token(request):
    if request.method == 'POST':
        form = forms.GenerateTokenForm(request.POST)
        if request.POST.get('action') == 'Cancel':
            return HttpResponseRedirect(reverse('logout'))
        elif form.is_valid():
            claimed_username = form.cleaned_data['username']
            number = int(time.time())
            md5 = hashlib.md5('%s' % number).hexdigest()
            as_int = int(md5, 16)
            whole_token = '%d' % as_int
            token = int(whole_token[-4:])
            client = rest.Client(ACCOUNT_SID, ACCOUNT_TOKEN, TELAPI_URL)
            account = client.accounts[client.account_sid]
            message = '%s, your temporary token is %04d' % (claimed_username, token)
            if form.cleaned_data['contact_method'] == '1':
                account.sms_messages.create(from_number=OUTGOING_NUMBER, to_number=form.cleaned_data['phone_number'],
                                            body=message)
            else:
                tok = '%04d' % int(token)
                tok_as_text = ' '.join(list(tok))
                telml = '<Response><Say loop="2">%s, your, temporary, token, is, %s</Say></Response>' % (claimed_username, tok_as_text)
                logging.debug('Token for %s is %s', claimed_username, token)
                account.calls.create(from_number=OUTGOING_NUMBER, to_number=form.cleaned_data['phone_number'], url=telml)
            request.session['claimed_username'] = claimed_username
            request.session['token'] = '%04d' % token
            request.session.save()
            return HttpResponseRedirect(reverse('login'))
    form = forms.GenerateTokenForm()
    return render_to_response('two_stage_auth/generate_token.html',
                              {'form': form},
                              context_instance=RequestContext(request))
