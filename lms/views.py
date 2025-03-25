from django.shortcuts import render, redirect
from student.models import Student, Paid_Student
from configuration.models import Config, Role, Session, Term, Subject, AllClass
from result.models import Result
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from django.db.models import Sum
from .models import Contact, Profile
from applicant.models import Paid_Applicant, Applicant
import requests
from django.conf import settings
from django.core.mail import send_mail
from datetime import date
from attendance.models import Attendance
from staff.models import Staff
from datetime import datetime

# Create your views here.

@login_required(login_url='login')
def home(request):
    user = request.user
    # if user.is_authenticated:
    #     logout(user)
    #     return redirect('logout')
    today = date.today()
    pat = today.strftime("%Y-%m-%d")
    day_pat = today.strftime('%d').lstrip('0')
    month_pat = today.strftime('%m').lstrip('0')
    student_dob = Student.objects.filter(birth_day=day_pat, birth_month=month_pat,active=1)
    staff_dob = Staff.objects.filter(birth_day=day_pat, birth_month=month_pat)
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    subject = Subject.objects.filter(approve_result=1,year=year,session=session,term=term)
    student = len(Student.objects.filter(active = 1))
    staff = len(Staff.objects.filter(active = 1))
    applicant = len(Applicant.objects.filter(session=session))
    result = Result.objects.filter(active = 1)
    payment = Paid_Student.objects.filter(term=term, session=session, year=year).aggregate(Sum('amount_paid'))
    payment_len = len(Paid_Student.objects.filter(term=term, session=session, status=1))
    application_payment = Paid_Applicant.objects.filter(session=session).aggregate(Sum('amount'))
    allstudent = len(Student.objects.all())
    iuser = Profile.objects.get(user=request.user.id).role
    present = len(Attendance.objects.filter(date=pat, status=1))
    absent = len(Attendance.objects.filter(date=pat, status=0))
    class_student = None
    class_info = None
    class_payment = None
    if iuser.role == 'class teacher':
        person = request.user
        class_student = Student.objects.filter(group=person.first_name,arm=person.last_name,graduated=0,active=1).order_by('last_name')
        class_info = AllClass.objects.get(teacher=person.username)
        class_payment = Paid_Student.objects.filter(term=term, session=session, year=year, group=person.first_name,arm=person.last_name)
    context = {
        'student':student,
        'allstudent':allstudent,
        'subject':subject,
        'result':result,
        'payment':payment['amount_paid__sum'],
        'class_student':class_student,
        'class_info':class_info,
        'application_payment':application_payment['amount__sum'],
        'applicant':applicant,
        'class_payment':class_payment,
        'present':present,
        'absent':absent,
        'payment_len':payment_len,
        'staff':staff,
        'student_dob':student_dob,
        'staff_dob':staff_dob,
    }
    return render(request, 'lms/home.html', context)

def error404(request):
    return render(request, 'lms/404.html')

def loginuser(request):
    if request.method == 'POST':
        username = request.POST.get('username').upper()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.profile.set_password:
                return redirect('set-password',user.username)
        except User.DoesNotExist:
            messages.error(request,'username does not exist')
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)
        print(user)

        if user is not None:
            login(request,user)
            if user.profile.role.keyword == 'student':
                return redirect('studentdash')
            person = user.profile.role.keyword
            if person == 'subject-teacher' or person == 'principal' or person == 'bursar':
                staff = Staff.objects.get(registration_number=user.username)
                if not staff.complete_registration:
                    return redirect('update-info',user.username)
            return redirect('home')
        else:
            messages.error(request,'password is incorrect')
            return redirect('login')
    return render(request, 'lms/login.html')

def updateInfo(request, ref):
    staff = Staff.objects.get(registration_number=ref)
    if staff.complete_registration:
        User.objects.filter(is_active=False, blocked_reason='Trying to by-pass update info illegally')
        messages.error(request, 'Self destruction activated')
        return redirect('logout')
    if request.method == 'POST':
        dob = request.POST.get('dob')
        nok_title = request.POST.get('title')
        nok_relate = request.POST.get('nok_relate')

        print(nok_title)

        staff.dob = dob
        date_object = datetime.strptime(dob, '%Y-%m-%d')
        staff.birth_day=str(date_object.day)
        staff.birth_month=str(date_object.month)
        staff.birth_year = str(date_object.year)
        staff.nok_title = nok_title
        staff.nok_relationship = nok_relate
        staff.complete_registration = True
        staff.save()
        messages.success(request, 'saved')
        return redirect('home')

    context = {'staff':staff}
    return render(request, 'lms/update-staff-info.html', context)

def setPassword(request, ref):
    if request.method == 'POST':
        getpass = User.objects.get(username=ref)
        profile = Profile.objects.get(user=getpass)
        if profile.set_password:
            pass1 = request.POST.get('pass1')
            pass2 = request.POST.get('pass2')

            if pass1 == pass2:
                u = User.objects.get(username=ref)
                u.set_password(pass1)
                u.save()
                profile.set_password = False
                profile.save()
                User.objects.filter(username=ref)
                user = authenticate(request, username=ref, password=pass1)
                login(request,user)
                messages.success(request, 'successful')
                return redirect('home')
            else:
                messages.error(request, 'Password did not match')
                return redirect('set-password',ref)
        else:
            User.objects.filter(username=request.user.username).update(is_active=0)
            messages.error(request, 'Self destruction activated')
            return redirect('logout')
    return render(request, 'lms/set-password.html')

def logoutuser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','subject-teacher'])
def userprofile(request):
    role = Role.objects.filter(active = 1)
    name = Config.objects.get(id=1).school_name
    context = {'role':role,'name':name}
    return render(request, 'lms/userprofile.html', context)

@login_required(login_url='login')
def changepassword(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.user.username)
        pass0 = request.POST.get('pass0')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if user.check_password(pass0):
            if pass1 == pass2:
                u = User.objects.get(username=request.user.username)
                u.set_password(pass1)
                u.save()
                messages.success(request, 'Password changed successfully')
                return redirect('change_password')
            else:
                messages.warning(request, 'Password did not match')
                return redirect('change_password')
        else:
            messages.warning(request,'incorrect password')
            return redirect('change_password')
    return render(request,'lms/changepassword.html')

@login_required(login_url='login')
def need_help(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        Contact.objects.create(name=name,email=email,subject=subject,message=message,added_by=request.user)
        config = Config.objects.get(id=1)
        get_msg = f'Message from {config.school_name}'
        msg = get_msg.replace(' ','+')
        url = f'https://api.callmebot.com/whatsapp.php?phone=2349034210056&text={msg}&apikey=5043106'
        x = requests.post(url)

        get_sub = subject.replace(' ','+')
        sub = f'https://api.callmebot.com/whatsapp.php?phone=2349034210056&text={get_sub}&apikey=5043106'
        requests.post(sub)

        get_content = message.replace(' ','+')
        content = f'https://api.callmebot.com/whatsapp.php?phone=2349034210056&text={get_content}&apikey=5043106'
        requests.post(content)

        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['obianomiracle2020@gmail.com' ]
        send_mail( subject, message, email_from, recipient_list )

        messages.success(request, 'Your message has been sent, you will receive a feedback shortly')
        return redirect('needhelp')
    return render(request, 'lms/need_help.html')