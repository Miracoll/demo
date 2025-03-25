from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from lms.decorators import allowed_users
from configuration.models import Config, Role
from lms.models import Profile
from staff.models import Staff
from django.contrib.auth.models import User, Group
from django.core.files.storage import FileSystemStorage
from random import randrange
from PIL import Image
from lms.functions import generateStaffRegNumber

# Create your views here.

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice_principal','controller'])
def registerstaff(request):
    sch_init = Config.objects.get(id=1).school_initial
    unique = Config.objects.get(id=1).staff_unique
    staff = Role.objects.filter(active = 1).exclude(role__in = ['admin','student','class teacher','parent'])
    if 'submit' in request.POST and request.FILES['myfile']:
        upload = request.FILES['myfile']
        fss = FileSystemStorage(location='media/teacher_passport')
        file = fss.save(upload.name, upload)
        upload_url = fss.url(file)
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        other_name = request.POST.get('other_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        dob = request.POST.get('dob')
        sex = request.POST.get('sex')
        role = request.POST.get('role')
        title = request.POST.get('title')

        if not Role.objects.filter(role=role).exists():
            user = request.user
            user.is_active = False 
            messages.error(request, 'Self destruction activated')
            return redirect('register_teacher')
        
        
        rand = generateStaffRegNumber(role)
        # rand = sch_init.upper() + str(unique) + str(randrange(123456,987654,5))
        # TODO: Check if app number already exist

        relate = request.POST.get('relate')
        full_name = request.POST.get('full_name')
        address1 = request.POST.get('address1')
        email1 = request.POST.get('email1')
        mobile1 = request.POST.get('mobile1')

        getstaff=Staff.objects.create(last_name=last_name,first_name=first_name,other_name=other_name,email=email,mobile=mobile,
        address=address,dob=dob,sex=sex,passport='teacher_passport/'+file,registration_number=rand,added_by=request.user,nok_title=title,
        nok_relationship=relate,nok_full_name=full_name,nok_address=address1,nok_mobile=mobile1,nok_email=email1)
        # addtoteacher.save()

        user = User.objects.create_user(rand,email,mobile)
        user.is_staff = False
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        getuser = user.id
        getroleid = Role.objects.get(role = role).id
        Profile.objects.filter(user_id = getuser).update(role_id = getroleid)
        Profile.objects.filter(user_id = getuser).update(passport = 'teacher_passport/'+file)

        getkeyword = Role.objects.get(role = role).keyword
        userid = User.objects.get(username=rand).id
        getgroup = Group.objects.get(name=getkeyword)
        getgroup.user_set.add(userid)

        # return redirect('register_teacher')
        return redirect('printstaff',getstaff.ref)
    context = {'staff':staff}
    return render(request, 'staff/staffregister.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def disablestaff(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        staff = Staff.objects.filter(registration_number=reg)
        active = User.objects.filter(username = reg)
        staff.update(active=0)
        active.update(is_active = 0)
        messages.success(request,'Update successful')
        return redirect('disable_staff')
    return render(request, 'staff/staffdisable.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def enablestaff(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        staff = Staff.objects.filter(registration_number=reg)
        active = User.objects.filter(username = reg)
        staff.update(active=1)
        active.update(is_active = 1)
        messages.success(request,'Update successful')
        return redirect('enable_staff')
    return render(request, 'staff/staffenable.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','subject-teacher','controller'])
def getstaff(request):
    errormsg = False
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        try:
            staff = Staff.objects.get(registration_number=reg).id
            return redirect('manage_staff',staff)
        except Staff.DoesNotExist:
            errormsg = True
    return render(request, 'staff/staffget.html',{'errormsg':errormsg})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','subject-teacher','controller'])
def managestaff(request,pk):
    staff = Staff.objects.filter(id=pk)
    reg = Staff.objects.get(id=pk).registration_number
    if 'submit1' in request.POST:
        last_name = request.POST.get('last_name1')
        first_name = request.POST.get('first_name1')
        other_name = request.POST.get('other_name1')
        address = request.POST.get('address1')
        phone = request.POST.get('phone1')
        email = request.POST.get('email1')
        # twitter = request.POST.get('twitter')
        # facebook = request.POST.get('facebook')
        # insta = request.POST.get('instagram')
        # linked = request.POST.get('linkedin')
        staff.update(last_name=last_name,first_name=first_name,other_name=other_name,address=address,mobile=phone,
        email=email
        )
        messages.success(request,'Update successful')
        return redirect('manage_staff',pk)

    context = {'staff':staff}
    return render(request, 'staff/staffmanage.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def editstaffreg(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        new_reg = request.POST.get('new_reg_num')
        if not Staff.objects.filter(registration_number=reg).exists() or not User.objects.filter(username=new_reg).exists():
            staff = Staff.objects.filter(registration_number=reg)
            staff.update(registration_number=new_reg)
            User.objects.filter(username = reg).update(username = new_reg)
            messages.success(request,'Update successful')
            return redirect('edit_staff_reg')
        else:
            messages.error(request,'Registration number already taken')
            return redirect('edit_staff_reg')
    return render(request, 'staff/staffregedit.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def printstaff(request, reference):
    staff = Staff.objects.get(ref=reference)
    context = {'student':staff}
    return render(request, 'staff/registerprint.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','controller'])
def resetstaffpassword(request):
    if request.method == 'POST':
        reg = request.POST.get('reg')
        user = User.objects.get(username=reg)
        user.set_password('staff')
        user.save()
        Profile.objects.filter(user=user).update(set_password=True)
        messages.success(request, 'Password changed successfully')
        return redirect('staffpasswordreset')
    return render(request,'staff/resetpassword.html')