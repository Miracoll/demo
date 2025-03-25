from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from lms.decorators import allowed_users
from lms.models import Profile
from configuration.models import Class, Arm, AllClass, Config, Term, Role, Session
from payment.models import Payment
from .models import Applicant, Paid_Applicant
from student.models import Student
from attendance.models import Attendance
from random import randrange
from datetime import date, datetime
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth.models import User, Group
import os
from secrets import token_hex
from django.conf import settings
from lms.functions import generatePassword, generateStudentRegNumber

# Create your views here.

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def preregstudent(request):
    if Config.objects.get(id=1).entry == 0:
        messages.warning(request, 'Registration is disabled')
        return redirect('continue_reg')
    group = Class.objects.all()
    arm = Arm.objects.all()
    term = Term.objects.get(active = 1).term
    # Uncomment if not using temporary code
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year

    if request.method == 'POST':
        last_name = request.POST.get('last_name').capitalize()
        first_name = request.POST.get('first_name').capitalize()
        other_name = request.POST.get('other_name').capitalize()
        email = request.POST.get('email').lower()
        mobile = request.POST.get('mobile')
        getgroup = request.POST.get('group')
        getarm = request.POST.get('arm')

        # if Applicant.objects.filter(email = email).exists():
        #     messages.warning(request, 'Email address already exist')
        #     return redirect('pre_register_student')
        try:
            payment = Payment.objects.get(category='application')
        except Payment.DoesNotExist:
            messages.error(request, 'Payment setup not found')
            return redirect('payment_setup')

        group_instance = Class.objects.get(group=getgroup)
        app_number = len(Applicant.objects.filter(session=session))
        applicant = Applicant.objects.create(
            last_name=last_name, first_name=first_name,other_name=other_name,email=email,mobile=mobile,group=getgroup,registered=False,
            arm=getarm, session=session, term=term, year=year, category=group_instance.category,applicant_number='APP_'+str(app_number+1).zfill(5)
        )
        pay = token_hex(16)
        while Paid_Applicant.objects.filter(payment_ref=pay).exists():
            pay = token_hex(16)
        pay_app=Paid_Applicant.objects.create(
            email=email,payment_ref=pay,year=year,term=term,session=session,amount=payment.amount,applicant=applicant
        )
        return redirect('print_rrr',pay_app.ref)
            
    context = {
        'group':group,
        'arm':arm,
    }
    return render(request, 'applicant/applicant.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def printrrr(request,pk):
    paystack_public_key = os.environ.get('PAYSTACK_PUBLIC_KEY')
    # paystack_public_key = os.getenv("PAYSTACK_PUBLIC_KEY")
    school_name = Config.objects.get(id = 1).school_name
    payment = Paid_Applicant.objects.get(ref=pk)
    applicant = Applicant.objects.get(ref = payment.applicant.ref)
    # Manually clear fee for unpaid application
    if request.method == 'POST':
        if Applicant.objects.filter(ref=applicant.ref,year=applicant.year,term=applicant.term,session=applicant.session).exists():
            # pemail = Applicant.objects.get(email=email).email
            pamount = Payment.objects.get(category='application').amount
            level = Class.objects.get(group=applicant.group)

            if Paid_Applicant.objects.filter(ref=payment.ref,year=applicant.year,term=applicant.term,session=applicant.session).exists():
                Paid_Applicant.objects.filter(ref=payment.ref,year=applicant.year,term=applicant.term,session=applicant.session).update(
                    status = 1,amount=pamount,cleared_by=request.user,manual_cleared = True
                )
            else:
                ref = token_hex(16)
                while Paid_Applicant.objects.filter(ref=ref).exists():
                    ref = token_hex(16)
                Paid_Applicant.objects.create(ref=payment.ref,amount=pamount,status=1,
                    cleared_by=request.user,manual_cleared = True
                )

            # if not Student.objects.filter(ref=payment.ref,year=applicant.year,term=applicant.term,session=applicant.session).exists():
            #     # Generate registration number here
            #     rand = generateStudentRegNumber(applicant.category, applicant.year,applicant.session)

            # student=Student.objects.create(
            #     last_name=applicant.last_name,first_name=applicant.first_name,other_name=applicant.other_name,email=applicant.email,mobile=applicant.mobile,
            #     group=applicant.group,arm=applicant.arm,year=applicant.year,term=applicant.term,session=applicant.session,level = level.level,category=applicant.category
            # )
            messages.success(request, 'Cleared')
            return redirect('register_student',applicant.ref)
        else:
            messages.warning(request, 'Such applicant does not exist')
            return redirect('clear_application')
    context = {
        'payment':payment,
        'name':school_name,
        'public':paystack_public_key,
        'applicant':applicant
    }
    return render(request, 'applicant/applicantprint.html', context)

def applicantreceipt(request, pk):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year

    category = Applicant.objects.get(email=getemail,year=year,term=term,session=session).category
    getemail = Paid_Applicant.objects.get(ref=pk).email
    last_name = Applicant.objects.get(email=getemail,year=year,term=term,session=session).last_name
    first_name = Applicant.objects.get(email=getemail,year=year,term=term,session=session).first_name
    other_name = Applicant.objects.get(email=getemail,year=year,term=term,session=session).other_name
    email = Applicant.objects.get(email=getemail,year=year,term=term,session=session).email
    mobile = Applicant.objects.get(email=getemail,year=year,term=term,session=session).mobile
    applicant = Applicant.objects.get(email=getemail,year=year,term=term,session=session).id
    getgroup = Applicant.objects.get(email=getemail,year=year,term=term,session=session).group
    getarm = Applicant.objects.get(email=getemail,year=year,term=term,session=session).arm
    
    level = Class.objects.get(group=applicant.group)
    payment = Paid_Applicant.objects.get(ref=pk)
    Paid_Applicant.objects.filter(ref=pk).update(
        status = 1,cleared_by = request.user
    )
    if not Student.objects.filter(email=email,year=year,term=term,session=session).exists():
        # Generate registration number here
        # try:
        #     sch_init = Config.objects.get(id=1).school_initial
        #     unique = Config.objects.get(id=1).student_unique
        # except Config.DoesNotExist:
        #     return redirect('configerror')
        # rand = sch_init.upper() + str(unique) + str(randrange(123456,987654,5))
        # while Student.objects.filter(registration_number=rand).exists():
        #     rand = sch_init.upper() + str(unique) + str(randrange(123456,987654,6))
        rand = generateStudentRegNumber(category)
        Student.objects.create(
            last_name=last_name,first_name=first_name,other_name=other_name,email=email,mobile=mobile,
            group=getgroup,arm=getarm,year=year,term=term,session=session,registration_number=rand,
            level = level.level,category=level.category
        )
    getstudentid = Student.objects.get(email=email,year=year,term=term,session=session).ref
    context = {'payment':payment,'student':getstudentid,'applicant':applicant}
    return render(request, 'applicant/applicantpaid.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def continuereg(request):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    if 'submit' in request.POST:
        email = request.POST.get('email')
        try:
            applicant = Applicant.objects.get(applicant_number=email,session=session)
        except Applicant.DoesNotExist:
            messages.error(request, 'Invalid applicant number')
            return redirect('continue_reg')
        paidApplicant = Paid_Applicant.objects.get(applicant_id=applicant,year=year,term=term,session=session)
        if paidApplicant.status == 1:
            if applicant.registered:
                appNum = Student.objects.get(applicant_number=email)
                messages.info(request, 'Applicant already registered')
                return redirect('print', appNum.ref)
            else:
                return redirect('register_student',applicant.ref)
        else:
            messages.error(request,'This applicant have not pay application fee yet')
            return redirect('print_rrr',paidApplicant.ref)
    return render(request, 'applicant/continuereg.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def registerstudent(request,pk):
    today = date.today()
    pat = today.strftime("%Y-%m-%d")

    group = Class.objects.all()
    arm = Arm.objects.all()
    student = Applicant.objects.get(ref=pk)
    try:
        term = Term.objects.get(active=1).term
        session = Session.objects.get(active=1).session
        year = Session.objects.get(active=1).year
    except Term.DoesNotExist:
        return redirect('termerror')

    if 'register-student' in request.POST:
        upload = request.FILES.get('myfile')
        fss = FileSystemStorage(location='media/passport')
        file = fss.save(upload.name, upload)
        # upload_url = fss.url(file)
        # email = Student.objects.get(ref=pk).email
        address = request.POST.get('address')
        dob = request.POST.get('dob')
        sex = request.POST.get('sex')
        gtitle = request.POST.get('title')
        glast = request.POST.get('glast')
        gfirst = request.POST.get('gfirst')
        gemail = request.POST.get('gemail')
        gmobile = request.POST.get('gmobile')
        gaddress = request.POST.get('gaddress')
        check_gaddr = request.POST.get('check_addr')
        print(check_gaddr, type(check_gaddr))

        student.address = address
        student.dob = dob
        student.sex = sex
        student.passport = f'passport/{file}'
        student.added_by = request.user
        student.guardian_title = gtitle
        student.guardian_last_name = glast
        student.guardian_first_name = gfirst
        student.guardian_mobile = gmobile
        student.guardian_email = gemail
        date_object = datetime.strptime(dob, '%Y-%m-%d')
        student.birth_day=str(date_object.day)
        student.birth_month=str(date_object.month)
        student.birth_year = str(date_object.year)
        student.registered = True
        if check_gaddr:
            gaddress = address
        student.guardian_address = gaddress
        student.save()

        level = Class.objects.get(group=student.group)
        rand = generateStudentRegNumber(student.category)
        passy = generatePassword()
        registeredStudent = Student.objects.create(
            last_name=student.last_name,first_name=student.first_name,other_name=student.other_name,email=student.email,mobile=student.mobile,
            group=student.group,arm=student.arm,year=year,term=term,session=session,registration_number=rand,applicant_number=student.applicant_number,
            level = level.level,category=level.category,address=address,dob=dob,sex=sex,passport=f'passport/{file}',added_by=request.user,
            guardian_title=gtitle,guardian_last_name=glast,guardian_first_name=gfirst,guardian_mobile=gmobile,guardian_email=gemail,
            birth_day=str(date_object.day),birth_month=str(date_object.month),birth_year=str(date_object.year),guardian_address=gaddress,token=passy
        )

        user = User.objects.create_user(rand,student.email,passy)
        user.is_staff = False
        user.first_name = student.first_name
        user.last_name = student.last_name
        user.save()
        getuser = user.id

        role = Role.objects.filter(role  = 'student').exists()
        if not role:
            Role.objects.create(role='student',added_by=request.user)

        getroleid = Role.objects.get(role = 'student')
        Profile.objects.filter(user_id = getuser).update(role_id = getroleid)
        Profile.objects.filter(user_id = getuser).update(passport = f'passport/{file}')

        person = User.objects.get(username=rand)
        getusergroup = Group.objects.get(name='student')
        getusergroup.user_set.add(person.id)

        # Lock student registration
        Student.objects.filter(ref=registeredStudent.ref).update(lock = 1)

        # # Create parent record
        # guardian = StudentGuardian.objects.create(user=person)
        # student.parent = guardian
        # student.save()

        nos = len(Student.objects.filter(group = student.group, arm = student.arm, active = 1))
        AllClass.objects.filter(group=student.group, arm=student.arm).update(number_of_student = nos)

        # Transfer to attendance table
        Attendance.objects.create(
            date=pat,student=rand,status=1,term=term,teacher=student.group+student.arm,lock=1,added_by=request.user,
            session = session, year=year,group=student.group,arm=student.arm
        )

        return redirect('print',registeredStudent.ref)
    context = {'group':group, 'arm':arm,'student':student}
    return render(request, 'applicant/studentregister.html',context)

# @login_required(login_url='login')
# @allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher'])
# def parentInfo(request, ref):
#     student = Student.objects.get(ref=ref)
#     person = User.objects.get(username = student.registration_number)
#     # parent = StudentGuardian.objects.get(user=person)
#     if request.method == 'POST':
#         # upload_url = fss.url(file)
#         last_name = request.POST.get('last_name')
#         first_name = request.POST.get('first_name')
#         email = request.POST.get('email')
#         address = request.POST.get('address')
#         mobile = request.POST.get('mobile')

#         # parent.last_name = last_name
#         # parent.first_name = first_name
#         # parent.address = address
#         # parent.mobile = mobile
#         # parent.email = email
#         # parent.save()

#         student.lock = 2
#         student.save()

#         messages.success(request, 'Guardian info added successfully')
#         return redirect('print',student.ref)

#     context = {}
#     return render(request, 'applicant/parentinfo.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def printregister(request, pk):
    student = Student.objects.get(ref=pk)
    context = {'student':student}
    return render(request, 'applicant/registerprint.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def startstopreg(request):
    if 'start' in request.POST:
        # Start applicant entry
        Config.objects.filter(id=1).update(entry=1)
        # Stop result computation
        Config.objects.filter(id=1).update(start_result=0)
        messages.success(request, 'Done')
        return redirect('startstopreg')
    if 'stop' in request.POST:
        Config.objects.filter(id=1).update(entry=0)
        messages.success(request, 'Done')
        return redirect('startstopreg')
    context = {}
    return render(request, 'applicant/startstopreg.html', context)