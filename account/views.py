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

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import FormView

from forms import CreationForm
from forms import PasswordResetForm
from forms import PreferencesForm
from forms import ProfileForm

from xmpplist.confirm.models import UserConfirmationKey
from xmpplist.confirm.models import UserPasswordResetKey


@login_required
def index(request):
    return render(request, 'account/index.html')


def create(request):
    if request.method == 'POST':
        user_form = CreationForm(request.POST, prefix='user')
        profile_form = ProfileForm(request.POST, prefix='profile')
        if user_form.is_valid() and profile_form.is_valid():
            # create user
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            # create confirmations:
            ekey = UserConfirmationKey.objects.create(user=user, type='E')
            ekey.send()
            jkey = UserConfirmationKey.objects.create(user=user, type='J')
            jkey.send()

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            return redirect('account')
    else:
        user_form = CreationForm(prefix='user')
        profile_form = ProfileForm(prefix='profile')

    return render(request, 'account/create.html',
                  {'user_form': user_form, 'profile_form': profile_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = PreferencesForm(request.POST, instance=request.user,
                                    prefix='user')
        profile_form = ProfileForm(request.POST, instance=request.user.profile,
                                   prefix='profile')

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save()

            if 'email' in user_form.changed_data:
                profile.email_confirmed = False
                profile.save()
                UserConfirmationKey.objects.filter(
                    user=user, type='E').delete()
                key = UserConfirmationKey.objects.create(user=user, type='E')
                key.send()
            if 'jid' in profile_form.changed_data:
                profile.jid_confirmed = False
                profile.save()
                UserConfirmationKey.objects.filter(
                    user=user, type='J').delete()
                key = UserConfirmationKey.objects.create(user=user, type='J')
                key.send()

            return redirect('account')
    else:
        user_form = PreferencesForm(instance=request.user, prefix='user')
        profile_form = ProfileForm(instance=request.user.profile,
                                   prefix='profile')

    return render(request, 'account/edit.html',
                  {'user_form': user_form, 'profile_form': profile_form})


class ResetPassword(FormView):
    template_name = 'account/reset_password.html'
    form_class = PasswordResetForm

    def get_success_url(self):
        return reverse('account_reset_password_ok')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect('account_set_password')

        return super(ResetPassword, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        key = UserPasswordResetKey(user=form.user)
        key.save()
        key.send()

        return super(ResetPassword, self).form_valid(form)


def reset_password_ok(request):
    return render(request, 'account/reset_password_ok.html')


@login_required
def resend_confirmation(request):
    if not request.user.profile.email_confirmed:
        key = UserConfirmationKey.objects.create(user=request.user, type='E')
        key.send()
    if not request.user.profile.jid_confirmed:
        key = UserConfirmationKey.objects.create(user=request.user, type='J')
        key.send()
    return render(request, 'account/resend_confirmation.html',
                  {'jid': settings.XMPP['default']['jid']})
