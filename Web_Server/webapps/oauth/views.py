from django.shortcuts import render, redirect
from Crypto.PublicKey import RSA
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import json
from django.middleware.csrf import get_token
from django.template import RequestContext
from datetime import datetime
import requests
import os

import oauth_credentials

from _utils.device_list_utils import get_device_list_and_count
from webapps.oauth.models import oauthToken
from webapps.buildinginfos.models import BuildingInfo
from settings import OauthKey_DIR


@login_required()
def oauth_main_page(request):
    if request.method == 'GET':
        device_list_side_nav = get_device_list_and_count(request)
        return_data = device_list_side_nav
        token_info = oauthToken.objects.all()
        return_data.update({'tokens': token_info})
        return render(request, "oauth/takeme2oauth.html", return_data)


@login_required()
def start_oauth(request):
    if request.method == "POST":
        _data = request.body
        _data = json.loads(str(_data))
        service_provider = _data['service_provider']
        building = _data['building']

        state = str(building)
        if service_provider == 'neurio':
            url = oauth_credentials.OauthInfo.Neurio.oauth_entry + state
        elif service_provider == 'nest':
            redirect_uri="http://localhost:8082/oauth/nest"
            url = oauth_credentials.OauthInfo.Nest.oauth_entry + state+"&redirect_uri="+redirect_uri
        elif service_provider == 'smartthings':
            url = oauth_credentials.OauthInfo.SmartThings.oauth_entry + state
        context = {'redirect_uri': url}

        if request.is_ajax():
            return HttpResponse(json.dumps(context))


def token_acquisition(request):
    with open(OauthKey_DIR + 'prikey.pem') as prifile:
        prikey = prifile.read()
    user_building = request.user.userprofile.authorized_buildings()[0]
    if request.method == 'POST':
        enc_token = request.POST['token']
        sp = request.POST['service_provider']
        private_key = RSA.importKey(prikey)
        token = private_key.decrypt((enc_token.encode('ISO-8859-1').strip(),))
        token_info = oauthToken(service_provider=sp, token=token, building=user_building, obtained_time=datetime.now())
        token_info.save()
        return HttpResponse(status=200)
    elif request.method == 'GET':
        context = RequestContext(request)
        get_token(request)
        return render(request, "callback/test.html")

def neurio_callback(request):

    client_id = oauth_credentials.OauthInfo.Neurio.client_id
    client_secret = oauth_credentials.OauthInfo.Neurio.client_secret
    callback_url = oauth_credentials.OauthInfo.Neurio.callback_url
    url = oauth_credentials.OauthInfo.Neurio.token_request_url

    process_callback(request, 'neurio', client_id, client_secret, callback_url, url)
    return redirect('/oauth')

def smartthings_callback(request):
    client_id = oauth_credentials.OauthInfo.SmartThings.client_id
    client_secret = oauth_credentials.OauthInfo.SmartThings.client_secret
    callback_url = oauth_credentials.OauthInfo.SmartThings.callback_url
    url = oauth_credentials.OauthInfo.SmartThings.token_request_url

    process_callback(request, 'smartthings', client_id, client_secret, callback_url, url)
    return redirect('/oauth')

def nest_callback(request):
    client_id = oauth_credentials.OauthInfo.Nest.client_id
    client_secret = oauth_credentials.OauthInfo.Nest.client_secret
    callback_url = oauth_credentials.OauthInfo.Nest.callback_url
    url = oauth_credentials.OauthInfo.Nest.token_request_url

    process_callback(request, 'nest', client_id, client_secret, callback_url, url)
    return redirect('/oauth')

def process_callback(request, service, client_id, client_secret, callback_url, url):
    if 'code' in request.GET.keys():
        code = request.GET['code']
        state = request.GET['state']
        data = 'grant_type=authorization_code&client_id=' + client_id + \
               '&client_secret=' + client_secret + '&redirect_uri=' + callback_url + \
               '&state=' + state + '&code=' + str(code)
        headers = {'Content-Type':'application/x-www-form-urlencoded'}
        response = requests.post(url, data, headers=headers)
        if response.status_code == 200:
            result = json.loads(response.content)
            access_token = result['access_token']

            building = BuildingInfo.objects.get(building_id=int(state))
            token_info = oauthToken(service_provider=service, token=access_token, building=building,
                                    obtained_time=datetime.now())
            token_info.save()
    elif 'error' in request.GET.keys():
        return HttpResponse(str(request.GET['error']))


def token_delete(request, sp, building_id):
    # TODO: Change the HTML file of this function, current model exist critical vulnerability
    token = oauthToken.objects.filter(service_provider=sp, building_id=building_id)
    token.delete()
    device_list_side_nav = get_device_list_and_count(request)
    return_data = device_list_side_nav
    return redirect('/oauth')
