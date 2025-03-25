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
from student.models import Student
from .models import Parent, ParentStudent
from .forms import ParentUpadateForm

# Create your views here.

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice_principal','controller'])
def getStudent(request):
    if request.method == 'POST':
        try:
            student = Student.objects.get(registration_number=request.POST.get('reg_num'))
        except Student.DoesNotExist:
            messages.error(request, "Sorry, i can't find this student")
            return redirect('parent-get-student')
        return redirect('parent-register', student.ref)
    context = {}
    return render(request, 'parent/getstudent.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice_principal','controller'])
def registerParent(request, ref):
    student = Student.objects.get(ref=ref)
    if request.method == 'POST':
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        # Generate parent unique number
        try:
            config = Config.objects.get(id=1)
        except Config.DoesNotExist:
            return redirect('configerror')
        rand = config.school_initial.upper() + str(config.parent_unique) + str(randrange(123456,987654,5))
        while Student.objects.filter(registration_number=rand).exists():
            rand = config.school_initial.upper() + str(config.parent_unique) + str(randrange(123456,987654,6))

        # Create parent instance
        parent = Parent.objects.create(
            last_name=last_name,first_name=first_name,email=email,address=address,mobile=mobile,
            added_by=request.user,unique_number = rand, current_student = student.registration_number,title=student.guardian_title
        )

        # Add parent-student to group
        student_user = User.objects.get(username=student.registration_number)
        if not ParentStudent.objects.filter(student=student_user).exists():
            ParentStudent.objects.create(
            student=student_user, parent=parent,added_by=request.user
        )
        else:
            messages.error(request, f'Student already assigned to a parent')
            return redirect('parent-register', student.ref)

        # Create parent as user instance
        user = User.objects.create_user(parent.unique_number,email,'parent')
        user.is_staff = False
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        getuser = user.id
        role = 'parent'

        if not Role.objects.filter(role  = role).exists():
            Role.objects.create(role=role,added_by=request.user)

        getroleid = Role.objects.get(role = role)
        Profile.objects.filter(user_id = getuser).update(role_id = getroleid)

        person = User.objects.get(username=student.registration_number)
        getusergroup = Group.objects.get(name=role)
        getusergroup.user_set.add(person.id)

        messages.success(request, 'Account created')
        return redirect('parent-print', parent.ref, student.ref)

    context = {'student':student}
    return render(request, 'parent/parentregister.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice_principal','controller'])
def parentPrint(request, pref, sref):
    parent = Parent.objects.get(ref=pref)
    student = Student.objects.get(ref=sref)
    assigned = ParentStudent.objects.filter(parent=parent)
    context = {'parent':parent,'student':student,'assigned':assigned}
    return render(request, 'parent/parentprint.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice_principal','controller'])
def assignStudent2Parent(request):
    if request.method == 'POST':
        sreg = request.POST.get('sreg')
        preg = request.POST.get('preg')
        student_user = User.objects.get(username=sreg)

        try:
            student = Student.objects.get(registration_number=student_user.username)
        except Student.DoesNotExist:
            messages.error(request, 'The identity for student does not exist')
            return redirect('parent-assign')
        try:
            parent = Parent.objects.get(unique_number=preg)
        except Parent.DoesNotExist:
            messages.error(request, 'The identity for parent does not exist')
            return redirect('parent-assign')
        
        return redirect('parent-student', student.ref, parent.ref)
    context = {}
    return render(request, 'parent/parentstudent.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice_principal','controller'])
def getParentStudent(request):
    if request.method == 'POST':
        try:
            student = Student.objects.get(registration_number=request.POST.get('snum'))
        except Student.DoesNotExist:
            messages.error(request, "Sorry, i can't find this student")
            return redirect('parent-get-parent-student')
        try:
            parent = Parent.objects.get(unique_number=request.POST.get('pnum'))
        except Student.DoesNotExist:
            messages.error(request, "Sorry, i can't find this parent")
            return redirect('parent-get-parent-student')
    
        return redirect('parent-student', student.ref, parent.ref)
    context = {}
    return render(request, 'parent/getparentstudent.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice_principal','controller'])
def parentStudent(request, sref, pref):
    student = Student.objects.get(ref=sref)
    parent = Parent.objects.get(ref=pref)
    if request.method == 'POST':
        # Add parent-student to group
        student_user = User.objects.get(username=student.registration_number)
        if not ParentStudent.objects.filter(student=student_user).exists():
            ParentStudent.objects.create(
            student=student_user, parent=parent,added_by=request.user
        )
        else:
            messages.error(request, f'Student already assigned to a parent')
            return redirect('parent-student',student.ref,parent.ref)
        messages.success(request, 'Successful')
        return redirect('parent-print',parent.ref,student.ref)
    context = {
        'student':student,
        'parent':parent
    }
    return render(request, 'parent/parentstudent.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def getParent(request):
    if request.method == 'POST':
        try:
            parent = Parent.objects.get(unique_number=request.POST.get('pnum'))
        except Parent.DoesNotExist:
            messages.error(request, 'Such parent does not exist')
            return render('parent-get')
        return redirect('parent-manage', parent.ref)
    context = {}
    return render(request, 'parent/getparent.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def manageParent(request, ref):
    parent = Parent.objects.get(ref=ref)
    form = ParentUpadateForm(instance=parent)
    if request.method == 'POST':
        form = ParentUpadateForm(request.POST, instance=parent)
        if form.is_valid():
            form.save()
            messages.success(request, 'saved')
            return redirect('parent-manage', ref)
    context = {'parent':parent,'form':form}
    return render(request, 'parent/parentmanager.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def disableParent(request, ref):
    parent = Parent.objects.get(ref=ref)
    parent.active = False
    parent.save()
    parent_user = User.objects.get(username = parent.unique_number)
    parent_user.is_active = False
    parent_user.save()
    messages.success(request,'Update successful')
    return redirect('parent-manage', ref)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def enableParent(request, ref):
    parent = Parent.objects.get(ref=ref)
    parent.active = True
    parent.save()
    parent_user = User.objects.get(username = parent.unique_number)
    parent_user.is_active = True
    parent_user.save()
    messages.success(request,'Update successful')
    return redirect('parent-manage', ref)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','controller'])
def resetParentPassword(request, ref):
    parent = Parent.objects.get(ref=ref)
    user = User.objects.get(username=parent.unique_number)
    user.set_password('parent')
    user.save()
    messages.success(request, 'Password changed successfully')
    return redirect('parent-manage', ref)