import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext

from webapps.buildinginfos.models import BuildingInfo
from _utils.device_list_utils import get_device_list_and_count

@login_required(login_url='/login/')
def buildinginfos_display(request):
    print 'Device status page load'
    context = RequestContext(request)

    if request.user.groups.filter(name__iexact = 'admin').exists():
        return render(request, 'buildinginfos/building_info.html', get_device_list_and_count(request))
    else:
        return HttpResponseRedirect('/home/')

def change_setting(request):
    if request.body:
        _data = request.body
        _data = json.loads(_data)
        building_id = _data.pop('building_id')
        info_changed = _data.keys()
        building_info = BuildingInfo.objects.get(building_id=building_id)
        if building_info in request.user.userprofile.authorized_buildings():
            if 'name' in info_changed:
                building_info.name = _data['name']
            if 'zip_code' in info_changed:
                building_info.zip_code = _data['zip_code']
            if 'description' in info_changed:
                building_info.description = _data['description']
            if 'location' in info_changed:
                building_info.building_settings['location'] = _data['location']

            building_info.save()
            message = 'success'
        else:
            message = 'error'

        if request.is_ajax():
            return HttpResponse(json.dumps(message))
