# Copyright (C) 2014-2015 Project Hatohol
#
# This file is part of Hatohol.
#
# Hatohol is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License, version 3
# as published by the Free Software Foundation.
#
# Hatohol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Hatohol. If not, see
# <http://www.gnu.org/licenses/>.

import json

from django import http
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import models
from django.forms import ModelForm

from hatohol.models import LogSearchSystem
from hatohol import hatoholserver
from viewer.userconfig import get_user_id_from_hatohol_server


def format_models(models):
    records = serializers.serialize('python', models)
    flatten_records = []
    for record in records:
        flatten_record = dict({'id': record['pk']}, **record['fields'])
        flatten_records.append(flatten_record)
    return flatten_records


def to_json(object):
    if hasattr(object, '__iter__'):
        return json.dumps(format_models(object))
    elif isinstance(object, models.Model):
        formatted_model = format_models([object])[0]
        return json.dumps(formatted_model)
    else:
        return json.dumps(object)


class LogSearchSystemForm(ModelForm):
    class Meta:
        model = LogSearchSystem


def is_valid_session(request):
    try:
        user_id = get_user_id_from_hatohol_server(request)
        return True
    except:
        return False


def log_search_systems(request, id):
    content_type = 'application/json'

    if not is_valid_session(request):
        return http.HttpResponseForbidden(content_type=content_type)

    if request.method == 'POST':
        form = LogSearchSystemForm(request.POST)
        system = form.save()
        response = http.HttpResponse(to_json(system),
                                     content_type=content_type,
                                     status=201)
        response['Location'] = reverse('hatohol.views.log_search_systems',
                                       args=[system.id])
        return response
    elif request.method == 'PUT':
        if id is None:
            message = 'id is required'
            return http.HttpResponseBadRequest(to_json(message),
                                               content_type=content_type)
        try:
            system = LogSearchSystem.objects.get(id=id)
        except LogSearchSystem.DoesNotExist:
            return http.HttpResponseNotFound(content_type=content_type)
        else:
            record = http.QueryDict(request.body, encoding=request.encoding)
            form = LogSearchSystemForm(record, instance=system)
            form.save()
            return http.HttpResponse(to_json(system),
                                     content_type=content_type)
    elif request.method == 'DELETE':
        if id is None:
            message = 'id is required'
            return http.HttpResponseBadRequest(to_json(message),
                                               content_type=content_type)
        try:
            system = LogSearchSystem.objects.get(id=id)
        except LogSearchSystem.DoesNotExist:
            return http.HttpResponseNotFound()
        else:
            system.delete()
            return http.HttpResponse()
    else:
        if id:
            try:
                system = LogSearchSystem.objects.get(id=id)
            except LogSearchSystem.DoesNotExist:
                return http.HttpResponseNotFound()
            response = system
        else:
            systems = LogSearchSystem.objects.all().order_by('id')
            response = systems
        return http.HttpResponse(to_json(response), content_type=content_type)
