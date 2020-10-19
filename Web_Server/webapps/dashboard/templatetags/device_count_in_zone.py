# -*- coding: utf-8 -*-
'''
Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''
from django.contrib.auth.models import User
from django import template

register = template.Library()


@register.simple_tag
def get_value_with_default(my_dict, *my_keys):
    x = my_dict
    default = my_keys[-1]
    my_keys = my_keys[:-1]
    try:
        for my_key in my_keys:
            x = x[my_key]
    except KeyError as er:
        print 'Cannot access the value, returning default: ' + str(default)
        return default  # the last value is the default value
    except Exception as er:
        print 'Cannot access dict value: ' + str(er)
        print my_dict
        print my_keys
        raise

    return x


@register.simple_tag
def get_value(my_dict, *my_keys):

    x = my_dict

    try:
        for my_key in my_keys:
            x = x[my_key]
    except KeyError as er:
        print 'Cannot access dict value: ' + str(er)
        print my_dict
        print my_keys
        return my_keys[-1] #the last value is the default value
    except Exception as er:
        print 'Cannot access dict value: ' + str(er)
        print my_dict
        print my_keys
        raise

    return x


@register.simple_tag
def get_keys(device_list, *args):
    x = device_list
    try:
        for arg in args:
            x = x[arg]
        x=x.keys()
        if 'all' in x:
            x.remove('all')
        return x
    except KeyError:
        return None

@register.simple_tag
def get_values(device_list, *args):
    x = device_list
    try:
        for arg in args:
            x = x[arg]
        x=x.values()
        if 'all' in x:
            x.remove('all')
        return x
    except KeyError:
        return None

@register.simple_tag
def make_list(*args):
    return args


@register.filter
def translate_appstat(status):
    all_stat = {'APR': 'Approved', 'PND': 'Pending', 'NBD': 'Non-BEMOSS'}
    return all_stat[status]


@register.filter
def new_users(users):
    nusers = User.objects.filter(is_active=False).count()
    return nusers

@register.filter
def lower_lookup(my_dict,key):
    return str(my_dict[key]).lower()


@register.filter
def upper_lookup(my_dict,key):
    return str(my_dict[key]).upper()


@register.filter
def lookup(my_dict,key):
    return my_dict[key]

@register.filter
def times(count):
    return range(1,int(count+1))

@register.filter
def list_if_none(l):
    if not l:
        return []
    else:
        return l
        
@register.filter
def rangefromto(start,end):
    return range(start,end)
        