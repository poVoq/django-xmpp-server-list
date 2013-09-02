# -*- coding: utf-8 -*-
#
# This file is part of xmpplist (https://list.jabber.at).
#
# xmpplist is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppllist is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xmpplist.  If not, see <http://www.gnu.org/licenses/>.

import json

from lxml import etree

from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.shortcuts import render

from xmpplist.server.models import Server


def index(request):
    # get request format
    request_format = 'json'
    if 'format' in request.GET:
        request_format = request.GET['format']

    # initial query-set:
    servers = Server.objects.filter(
        verified=True, moderated=True, user__profile__email_confirmed=True)

    # filter by required features:
    if 'features' in request.GET:
        features = request.GET['features'].split(',')
        if 'plain' in features:
            servers = servers.filter(features__has_plain=True)
        if 'ssl' in features:
            servers = servers.filter(features__has_ssl=True)
        if 'tls' in features:
            servers = servers.filter(features__has_tls=True)
        if 'ipv6' in features:
            servers = servers.filter(features__has_ipv6=True)

    # filter by country
#TODO: re-enable country filtering functionality? Was removed during location.
#    if 'country' in request.GET:
#        country = request.GET['country']
#        servers = servers.filter(location__within=country.geom)

    fields = ['domain']

    # http://xmpp.org/services/services.xml and
    # http://xmpp.org/services/services-full.xml formats already deprecated, i
    # hope :)
    # does fetching + serialization in one step
    if request_format == 'services.xml' \
            or request_format == 'services-full.xml':
        root_element = etree.Element('query')

        if request_format == 'services-full.xml':
            fields += ['software__name', 'contact', 'contact_type', 'website',
                       'location', ]

        contact_prefixes = {'M': 'xmpp:', 'J': 'xmpp:', 'E': 'mailto:'}

        values = list(servers.values(*fields))

        for item in values:
            item_element = etree.SubElement(root_element, 'item')
            item_element.set('jid', item['domain'])

            if request_format == 'services-full.xml':
                etree.SubElement(item_element, 'server-software').text = item['software__name']
                etree.SubElement(item_element, 'domain').text = item['domain']
                etree.SubElement(item_element, 'homepage').text = item['website']

                contact_prefix = ''
                if item['contact_type'] in contact_prefixes:
                    contact_prefix = contact_prefixes[item['contact_type']]

                etree.SubElement(item_element, 'primary-admin').text = contact_prefix + item['contact']
                etree.SubElement(item_element, 'longitude').text = str(item['location'].x)
                etree.SubElement(item_element, 'latitude').text = str(item['location'].y)
                etree.SubElement(item_element, 'description').text = None

        return HttpResponse(etree.tostring(root_element, pretty_print=True), mimetype='text/xml')

    # we now continue by parsing the fields parameter
    if 'fields' in request.GET:
        custom_fields = request.GET['fields'].split(',')
        valid_fields = ['launched', 'location', 'website', 'ca', 'software',
                        'software_version', 'contact']
        if set(custom_fields) - set(valid_fields):
            return HttpResponseForbidden("tried to retrieve forbidden fields.")

        if 'ca' in custom_fields:
            custom_fields.remove('ca')
            custom_fields.append('ca__name')
        if 'software' in custom_fields:
            custom_fields.remove('software')
            custom_fields.append('software__name')
        if 'contact' in custom_fields:
            custom_fields.remove('contact')
            custom_fields += ['contact', 'contact_type']

        fields += custom_fields

    if len(fields) == 1:
        values = list(servers.values_list(*fields, flat=True))
    else:
        tmp_values = list(servers.values(*fields))
        values = {}
        for value in tmp_values:
            domain = value.pop('domain')

            if 'ca__name' in value:
                ca = value.pop('ca__name')
                value['ca'] = ca
            if 'software__name' in value:
                software = value.pop('software__name')
                value['software'] = software
            if 'contact' in value:
                contact = value.pop('contact')
                contact_type = value.pop('contact_type')
                value['contact'] = (contact, contact_type)
            if 'location' in value:
                location = value.pop('location')
                value['location'] = '%s,%s' % (location.x, location.y)
            if 'launched' in value:
                launched = value.pop('launched')
                value['launched'] = launched.strftime('%Y-%m-%d')

            values[domain] = value

    if request_format == 'json':
        return HttpResponse(json.dumps(values))
    else:
        return HttpResponseBadRequest('unknown request format: try "services.xml", "services-full.xml" or "json"')


def help(request):
    return render(request, 'api/help.html')
