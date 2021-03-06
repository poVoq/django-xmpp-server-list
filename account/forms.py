# This file is part of django-xmpp-server-list
# (https://github.com/mathiasertl/django-xmpp-server-list)
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

from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.template import loader
from django.utils.translation import ugettext_lazy as _

from xmpp.backends import default_xmpp_backend

UserModel = get_user_model()


class UserCreationForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'jid',)

    def clean_username(self):
        """Override to make the form compatible with custom user models."""

        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            UserModel._default_manager.get(username=username)
        except UserModel.DoesNotExist:
            return username
        raise forms.ValidationError(_('Username already exists.'))


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password2'].label = _('Confirm')  # Shorten text to improve wrapping of label


class PasswordResetForm(auth_forms.PasswordResetForm):
    """Override the default form class to also send XMPP messages to JIDs."""

    email = forms.EmailField(label=_("JID or email"), max_length=254)

    def get_users(self, email):
        """Override parent class so we also match the JID of users."""

        active_users = UserModel.objects.jid_or_email(email).filter(is_active=True)
        return (u for u in active_users if u.has_usable_password())

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """Override so we can also send a message via XMPP.

        Note that we do not override the save() method, where we could generate an independent token,
        but this would create a lot of additional code. Here we can just render the same message again.
        """

        super().send_mail(subject_template_name, email_template_name,
                          context, from_email, to_email, html_email_template_name)

        xmpp_template_name = 'account/password_reset_xmpp.txt'
        message = loader.render_to_string(xmpp_template_name, context).strip()
        default_xmpp_backend.send_chat_message(context['user'], message)
