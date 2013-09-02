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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url

from xmpplist.server.views import IndexView
from xmpplist.server.views import ModerateView


urlpatterns = patterns(
    'server.views',
    url(r'^$', login_required(IndexView.as_view()), name='server'),
    url(r'^moderate/$', permission_required('server.moderate')(
        ModerateView.as_view()), name='server_moderate'),
    url(r'^(?P<server_id>\w+)/report/$', 'report', name='server_report'),

    url(r'^ajax/$', 'ajax', name='servers_ajax'),
    url(r'^ajax/moderate/$', 'ajax_moderate', name='server_ajax_moderate'),
    url(r'^ajax/(?P<server_id>\w+)/$', 'ajax_id', name='servers_ajax_id'),
)
