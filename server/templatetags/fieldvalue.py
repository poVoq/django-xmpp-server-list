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

from django import template
from django.forms.fields import DateField

register = template.Library()

@register.filter
def fieldvalue(field):
    if hasattr(field.field, 'choices'):
        for k, v in field.field.choices:
            if k == field.value():
                return v
        return 'key not found'
    elif type(field.field) == DateField:
        val = field.value()
        if val.__class__ == unicode:
            return val
        return field.value().strftime('%Y-%m-%d')
    else:
        return field.value()
