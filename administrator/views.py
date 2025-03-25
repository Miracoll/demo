from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from configuration.models import Role, Config
from lms.models import Profile
from django.contrib import messages

# Create your views here.

def superadmin(request):
    if request.method == 'POST':
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        username = request.POST.get('username').upper()
        password = request.POST.get('password')

        user = User.objects.create_user(username,email,password)
        user.is_staff = True
        user.is_superuser = True
        user.last_name = last_name
        user.first_name = first_name
        user.save()
        getuser = user.id

        role = Role.objects.filter(keyword = 'admin')
        if len(role) == 0:
            Role.objects.create(role='admin',added_by=user)
            Group.objects.create(name='admin')

        getroleid = Role.objects.get(role = 'admin').id
        Profile.objects.filter(user_id = getuser).update(role_id = getroleid)
        Profile.objects.filter(user_id = getuser).update(passport = 'passport.jpg')
            
        userid = User.objects.get(username=username).id
        getgroup = Group.objects.get(name='admin')
        getgroup.user_set.add(userid)

        if not Config.objects.all().exists():
            Config.objects.create(added_by = user)

        messages.success(request, 'Creation successful')
        return redirect('logout')
    return render(request, 'administrator/superadmin.html')