# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list).
#
# django-xmpp-server-list is free software: you can redistribute it and/or modify
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
# along with django-xmpp-server-list.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from server.views import IndexView

admin.autodiscover()

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^user/', include('account.urls')),
    url(r'^user/', include('account.auth_urls')),
    url(r'^server/', include('server.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^confirm/', include('confirm.urls')),

    url(r'^admin/', admin.site.urls),

]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
