from django.http import HttpResponse
from server.models import Server
from django.shortcuts import render

def home(request):
    servers = Server.objects.filter(
        verified=True, moderated=True, user__profile__email_confirmed=True)

    return render(request, 'index.html', {'servers': servers})