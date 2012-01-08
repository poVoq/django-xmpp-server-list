from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from forms import CreationForm, PreferencesForm, PasswordForm, PasswordResetForm

from xmpplist.confirm.models import UserConfirmationKey, UserPasswordResetKey

@login_required
def index(request):
    return render(request, 'account/index.html')
    
def create(request):
    if request.method == 'POST':
        form = CreationForm(request.POST)
        if form.is_valid():
            # create user
            user = form.save()
            
            # create email confirmation:
            key = UserConfirmationKey.objects.create(user=user)
            key.send(request, typ='E') # send to email address (for now)
            
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return redirect('account')
    else:
        form = CreationForm()
        
    return render(request, 'account/create.html', {'form': form})

@login_required
def edit(request):
    if request.method == 'POST':
        form = PreferencesForm(request.POST, instance=request.user)
        
        if form.is_valid():
            user = form.save()
            
            if 'email' in form.changed_data:
                print('changed email!')
                user.profile.email_confirmed = False
                user.profile.save()
                
                # TODO: resend confirmation
    else:
        form = PreferencesForm(instance=request.user)
        
    return render(request, 'account/edit.html', {'form': form})
    
@login_required
def set_password(request):
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password'])
            request.user.save()
    else:        
        form = PasswordForm()
        
    return render(request, 'account/set_password.html', {'form': form})
    
def reset_password(request):
    if request.user.is_authenticated():
        return redirect('account_set_password')
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            
            # send reset-key:
            key = UserPasswordResetKey(user=user)
            key.save()
            key.send(request)
    else:
        form = PasswordResetForm()
        
    return render(request, 'account/reset_password.html', {'form': form})