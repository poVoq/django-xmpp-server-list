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

from django.db import models

from querysets import ConfirmationKeyQuerySet
from querysets import ServerConfirmationKeyQuerySet


class ConfirmationKeyManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return ConfirmationKeyQuerySet(self.model)

    def for_user(self, user):
        return self.get_query_set().for_user(user=user)

    def valid(self):
        return self.get_query_set().invalid()

    def invalid(self):
        return self.get_query_set().valid()

    def invalidate_outdated(self):
        return self.get_query_set().invalidate_outdated()

    def invalidate(self, subject):
        return self.get_query_set().invalidate(subject=subject)


class ServerConfirmationKeyManager(ConfirmationKeyManager):
    def get_query_set(self):
        return ServerConfirmationKeyQuerySet(self.model)
