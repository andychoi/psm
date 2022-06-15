from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        p_form = ProfileUpdateForm(request.POST)
        if form.is_valid() and p_form.is_valid():
            # always use lowercase
            u = form.save()

            #https://stackoverflow.com/questions/3063935/django-how-to-make-one-form-from-multiple-models-containing-foreignkeys
            p = p_form.save(commit=False)
            # p.user = u    -> it is created by signals
            p.save()


            # if user belongs to internal company, then assign staff role automatically
            if u.email[u.email.index('@') + 1 : ] == settings.DOMAIN:
                User.objects.filter(id=u.id).update(is_staff=True)
                user_group = Group.objects.get(name='staff')
                u.groups.add(user_group) 

            messages.success(
                request, "Your account has been created with %s!. You are now able to login." % u.username)
            return redirect('login')
    else:
        form = UserRegisterForm()
        p_form = ProfileUpdateForm()
        
    return render(request, 'users/register.html', {'form': form, 'p_form': p_form} )


@login_required
def profile(request):
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated!")
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        try:
            p_form = ProfileUpdateForm(instance=request.user.profile)
        except:
            p_form = None

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)
