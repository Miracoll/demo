from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from lms.decorators import allowed_users
from configuration.models import AllClass, Term, Session, Class, Arm
from student.models import Student
from attendance.models import Attendance
from django.contrib import messages
from datetime import date

# Create your views here.

today = date.today()
pat = today.strftime("%Y-%m-%d")

@login_required(login_url='login')
@allowed_users(allowed_roles=['class-teacher'])
def attendance(request):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    allstudent = []
    print(pat)
    try:
        getuser = request.user.username
        if AllClass.objects.filter(owner=getuser).exists() or AllClass.objects.filter(teacher=getuser).exists():
            getclass = AllClass.objects.get(teacher = getuser).group
            getarm = AllClass.objects.get(teacher = getuser).arm
            student = Student.objects.filter(group=getclass,arm=getarm,active=1)
            attendance = Attendance.objects.filter(
                group=getclass,arm=getarm,date=pat,term=term,session=session,year=year
            ).values_list('student')
            for i in attendance:
                allstudent.extend(i)

    except AllClass.DoesNotExist:
        return redirect('error404')
    context = {'student':student,'attendance':allstudent}
    return render(request, 'attendance/attendance.html', context)

def before_attendance(request):
    group = Class.objects.all()
    arm = Arm.objects.all()
    if request.method == 'POST':
        getgroup = request.POST.get('group')
        getarm = request.POST.get('arm')
        return redirect(admin_attendance,getgroup,getarm)
    context = {
        'group':group,
        'arm':arm
    }
    return render(request, 'attendance/getattendance.html', context)



@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def admin_attendance(request,group,arm):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    # student = ''
    allstudent = []
    if not AllClass.objects.filter(group=group, arm=arm).exists():
        messages.error(request, 'Class does not exist')
        return redirect('home')
    
    student = Student.objects.filter(group=group,arm=arm,active=1)
    attendance = Attendance.objects.filter(
        group=group,arm=arm,date=pat,term=term,session=session,year=year
    ).values_list('student')
    for i in attendance:
        allstudent.extend(i)
        
    context = {'student':student,'attendance':allstudent}
    return render(request, 'attendance/attendance.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','class-teacher'])
def present(request, id):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    getclass = Student.objects.get(registration_number = id).group
    getarm = Student.objects.get(registration_number = id).arm

    if Attendance.objects.filter(date=pat).exists():
        if not Attendance.objects.filter(student=id,date=pat).exists():
            Attendance.objects.create(
                student=id,date=pat,teacher=request.user,term=term,status=1,lock=1,added_by=request.user,
                year=year,session=session,group=getclass,arm=getarm
            )
            messages.success(request, 'marked')
        else:
            if Attendance.objects.filter(student=id,date=pat,lock=0).exists():
                Attendance.objects.filter(student=id,date=pat,lock=0).update(status=1,lock=1)
                messages.success(request, 'updated')
            else:
                messages.warning(request, 'Student already marked')
    else:
        Attendance.objects.create(
            student=id,date=pat,teacher=request.user,term=term,status=1,lock=1,added_by=request.user,
            year=year,session=session,group=getclass,arm=getarm
        )
        messages.success(request, 'marked')
    if request.user.profile.role.keyword == 'class-teacher':
        return redirect('attendance')
    elif request.user.profile.role.keyword == 'admin' or request.user.profile.role.keyword == 'principal' or request.user.profile.role.keyword == 'vice-principal':
        return redirect('admin_attendance',getclass,getarm)
    else:
        return redirect('home')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','class-teacher'])
def absent(request, id):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    getclass = Student.objects.get(registration_number = id).group
    getarm = Student.objects.get(registration_number = id).arm

    if Attendance.objects.filter(date=pat).exists():
        if not Attendance.objects.filter(student=id,date=pat).exists():
            Attendance.objects.create(
                student=id,date=pat,teacher=request.user,term=term,status=0,lock=1,added_by=request.user,
                year=year,session=session,group=getclass,arm=getarm
            )
            messages.success(request, 'marked')
        else:
            if Attendance.objects.filter(student=id,date=pat,lock=0).exists():
                Attendance.objects.filter(student=id,date=pat,lock=0).update(status=0,lock=1)
                messages.success(request, 'updated')
            else:
                messages.warning(request, 'Student already marked')
    else:
        Attendance.objects.create(
            student=id,date=pat,teacher=request.user,term=term,status=0,lock=1,added_by=request.user,
            year=year,session=session,group=getclass,arm=getarm
        )
        messages.success(request, 'marked')
    if request.user.profile.role.keyword == 'class-teacher':
        return redirect('attendance')
    elif request.user.profile.role.keyword == 'admin' or request.user.profile.role.keyword == 'principal' or request.user.profile.role.keyword == 'vice-principal':
        return redirect('admin_attendance',getclass,getarm)
    else:
        return redirect('home')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','class-teacher'])
def unlockattendance(request):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    if request.method == 'POST':
        reg = request.POST.get('reg_num')
        if not Student.objects.filter(registration_number=reg).exists():
            messages.error(request, 'Incorrect registration number')
        student = Student.objects.get(registration_number = reg)
        if not Attendance.objects.filter(student=reg,group=student.group,arm=student.arm,date=pat).exists():
            messages.warning(request, 'Student does not exist')
            return redirect('before_attendance')
        Attendance.objects.filter(student=reg,term=term,session=session,year=year,date=pat).delete()
        messages.success(request, 'unlock')
        if request.user.profile.role.keyword == 'class-teacher':
            return redirect('attendance')
        elif request.user.profile.role.keyword == 'admin' or request.user.profile.role.keyword == 'principal' or request.user.profile.role.keyword == 'vice-principal':
            return redirect('admin_attendance',student.group,student.arm)
        else:
            return redirect('home')
    return render(request, 'attendance/attendanceunlock.html')