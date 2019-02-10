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

from threading import Thread

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from server.forms import ServerForm
from server.models import Features
from server.models import Server


class MyServerMixin(LoginRequiredMixin):
    """Makes sure that a ModelView is only called with servers the user owns."""

    queryset = Server.objects.order_by('domain')

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class MyServerFormMixin(MyServerMixin):
    """Set the form prefix to the servers id."""
    def get_prefix(self):
        return self.object.id


class IndexView(ListView):
    queryset = Server.objects.moderated().verified().order_by('domain')


class MyServerListView(MyServerMixin, ListView):
    template_name = 'server/my_server_list.html'


class ServerCreateView(LoginRequiredMixin, CreateView):
    model = Server
    form_class = ServerForm
    queryset = Server.objects.all()

    def form_invalid(self, form):
        print('invalid')
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ServerUpdateView(MyServerMixin, UpdateView):
    form_class = ServerForm


class ServerDetailView(DetailView):
    queryset = Server.objects.all()


class ModerateView(PermissionRequiredMixin, ListView):
    permission_required = 'server.moderate'
    template_name = 'server/moderate.html'
    queryset = Server.objects.for_moderation()


class ReportView(MyServerMixin, DetailView):
    queryset = Server.objects.all()
    template_name = 'server/ajax/report.html'


class AjaxServerCreateView(LoginRequiredMixin, CreateView):
    form_class = ServerForm
    http_method_names = ('post', )
    template_name = 'server/ajax/new_server.html'

    def form_valid(self, form):
        server = form.save(commit=False)
        server.user = self.request.user
        server.features = Features.objects.create()
        server.save()  # TODO: required? (maybe for a valid pk?)

        server.do_contact_verification(self.request)
        server.save()

        # start verification in a separate thread:
        t = Thread(target=server.verify)
        t.start()

        context = self.get_context_data(form=form)
        context['new_server_form'] = ServerForm()
        return self.render_to_response(context)


class AjaxServerUpdateView(MyServerFormMixin, UpdateView):
    model = Server
    form_class = ServerForm
    http_method_names = ('post', )
    template_name = 'server/ajax/server_table_row.html'

    def form_valid(self, form):
        server = self.object
        changed = set(form.changed_data)
        moderate_properties = {
            'contact',
            'contact_name',
            'contact_type',
            'website',
        }
        if 'domain' in changed:
            server.moderated = None
            server.moderators_notified = False
            server.verified = None
        if moderate_properties & changed:
            typ = form.cleaned_data['contact_type']
            contact = form.cleaned_data['contact']
            if 'website' not in changed and server.autoconfirmed(typ, contact):
                print('autoconfirmed!')
                pass
            else:
                server.moderated = None
                server.moderators_notified = False
                server.contact_verified = False

        # We have special treatment if contact was JID or email:
        if form.contact_changed():
            server.confirmations.all().delete()
            server.do_contact_verification(self.request)
        server.save()
        return self.render_to_response(self.get_context_data(form=form))


class AjaxServerDeleteView(MyServerMixin, DeleteView):
    model = Server
    http_method_names = ('delete', )

    def delete(self, request, *args, **kwargs):
        """Omit success_url etc."""
        self.get_object().delete()
        return HttpResponse()


class AjaxServerResendView(MyServerMixin, SingleObjectMixin, View):
    queryset = Server.objects.filter(contact_verified=False)
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        server = self.get_object()
        server.do_contact_verification(request)
        return HttpResponse()


class AjaxServerResubmitView(MyServerFormMixin, UpdateView):
    model = Server
    form_class = ServerForm
    http_method_names = ('post', )
    template_name = 'server/ajax/server_table_row.html'

    def form_valid(self, form):
        server = form.save(commit=False)
        server.moderated = None
        server.moderation_message = ''
        server.moderators_notified = False
        server.save()
        return self.render_to_response(self.get_context_data(form=form))


class AjaxServerModerateView(PermissionRequiredMixin, SingleObjectMixin, View):
    queryset = Server.objects.for_moderation()
    permission_required = 'server.moderate'
    http_method_names = ('post', )

    def post(self, request, *args, **kwargs):
        server = self.get_object()
        if request.POST['moderate'] == 'true':
            server.moderated = True
            server.moderation_message = ''
            server.contact_verified = True
        else:
            server.moderated = False
            server.moderation_message = request.POST['message']
        server.save()
        return HttpResponse()
