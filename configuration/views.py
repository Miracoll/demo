from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Config, Term, Session, Arm, AllClass, Role, Class, AllSubject, Subject, Category,RegisteredSubjects
from .forms import ConfigUpdateForm
from .functions import encryptClass, unencryptClass, sendSMS
from staff.models import Staff
from student.models import Student, Paid_Student
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth.models import User, Group
from lms.models import Profile
from django.contrib.auth.decorators import login_required
from lms.decorators import allowed_users
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from random import randrange, choice
from parent.models import ParentStudent
from card.models import Card
from result.models import Result
from academic.models import Record
import csv
from io import StringIO
import subprocess
import os

# Create your views here.

def config(request):
    config = Config.objects.get(id=1)
    form = ConfigUpdateForm(instance=config)
    if request.method == 'POST':
        form = ConfigUpdateForm(request.POST, request.FILES, instance=config)
        password = request.POST.get('psw')
        user = request.user
        if user.check_password(password):
            if form.is_valid():
                get_config = form.save(commit=False)
                get_config.added_by = request.user
                get_config.save()
                messages.success(request,'Configuration updated')
                return redirect('config')
        else:
            messages.error(request,'Incorrect administrative password')
            return redirect('config')

    context = {'form':form}
    return render(request, 'configuration/config.html', context)

def configerror(request):
    return render(request, 'configuration/configerror.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def term(request):
    term = Term.objects.exclude(term='4')
    if not term.exists():
        for i in range(1,4):
            print(i)
            Term.objects.create(term=i, added_by=request.user)
        Term.objects.filter(term=1).update(active=1)
    context = {'term':term}
    return render(request, 'configuration/term.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def switchterm(request, ref):
    config = Config.objects.get(id=1)
    if config.start_result == 1:
        messages.error(request, "Can't switch term while result computation is active")
        return redirect('term')
    if config.entry == 1:
        messages.error(request, "Can't switch session while application is going on")
        return redirect('term')
    Term.objects.filter(active = 1).update(active = 0)
    Term.objects.filter(ref=ref).update(active = 1)
    messages.success(request,'Done')
    return redirect('term')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def termerror(request):
    return render(request, 'configuration/termerror.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def session(request):
    ses = Session.objects.all()
    if request.method == 'POST':
        user = request.user
        session = request.POST.get('session')
        year = request.POST.get('year')
        password = request.POST.get('psw')
        if user.check_password(password):
            if Session.objects.filter(year=year).exists():
                messages.error(request,'Year already exist')
                return redirect('session')
            if Session.objects.filter(session=session).exists():
                messages.error(request,'Session already exist')
                return redirect('session')
            # Get all active and non-graduated students
            allactivestudent = Student.objects.filter(active=1, graduated=False)
            errorstudents = []
            getError = False

            # Check if student passed last session
            lastSession = Session.objects.last()

            # Delete previous SS3 and JS3 from RegisteredSubjects model
            RegisteredSubjects.objects.filter(group__endswith = '3').delete()     #Delete all ss3 and js3 student records from registeredSubject table

            for student in allactivestudent:
                if student.level==3 or student.level>=6:
                    # Deactivate student
                    Student.objects.filter(registration_number = student.registration_number).update(graduated=True, active=0)
                    # Delete student from parent access
                    try:
                        student_user = User.objects.get(username=student.registration_number)
                        ParentStudent.objects.filter(student=student_user).delete()
                    except:
                        getError = True
                        errorstudents.append(student.registration_number)
                    # Deactivate registered courses
                    RegisteredSubjects.objects.filter(student=student.registration_number).update(active=False)
                    continue

                print(lastSession.session,student.registration_number)
                try:
                    studentResult = Result.objects.get(student=student.registration_number,term=4,session=lastSession.session)
                except Result.DoesNotExist:
                    print('DNE')
                    continue
                if studentResult.remark == 'PROMOTED':
                    print('baby mo')
                    # Student.objects.filter(registration_number = student.registration_number).update(level = int(student.level)+1,register_course=False)
                    oldLevel = student.level
                    newLevel = oldLevel+1
                    print(f'i dey level {newLevel}')
                    student.level = newLevel
                    student.register_course = False
                    student.save()
                    group = Class.objects.get(level=newLevel)
                    # Student.objects.filter(registration_number=student.registration_number).update(group=group.group)
                    student.group = group.group
                    student.save()

                    # Update student class in registered course table
                    RegisteredSubjects.objects.filter(student=student.registration_number).update(group=group.group)

            # Stop result computation and start student entry
            Config.objects.filter(id=1).update(start_result=0,entry=1)
            # messages.info(request, 'Activating application...')

            # Deactivate other session
            Session.objects.filter(active=1).update(active=0)
            # messages.info(request, 'Deactivating previous session...')

            # Create new session and activate it
            Session.objects.create(session=session, year=year, added_by=request.user,active=1)
            # messages.info(request, 'Activating new session...')

            # Switch to first term
            Term.objects.filter(active = 1).update(active = 0)
            Term.objects.filter(term=1).update(active = 1)
            # messages.info(request, 'Switching to new term...')

            messages.success(request,'Done')
            if getError:
                response = HttpResponse(content_type='text/plain')
                response['Content-Disposition'] = 'attachment:filename=errorlog.txt'
                response.writelines('This log contain students who did not enter the newly created session\n\n')
                response.writelines('Pls download and send file to developer via systemcog@gmail.com\n\n')
                for line in errorstudents:
                    response.writelines(f'{line}\n\n')
                return response
            return redirect('session')
        else:
            messages.error(request,'Incorrect administrative password')
            return redirect('session')
    context = {'session':ses}
    return render(request, 'configuration/session.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def switchsession(request, ref):
    config = Config.objects.get(id=1)

    if config.start_result == 1:
        messages.error(request, "Can't switch session while result computation is active")
        return redirect('session')
    if config.entry == 1:
        messages.error(request, "Can't switch session while application module is active")
        return redirect('session')

    
    Session.objects.filter(active = 1).update(active = 0)
    Session.objects.filter(ref=ref).update(active = 1)
    messages.success(request,'Done')
    return redirect('session')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def viewclass(request):
    return render(request, 'configuration/classview.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def viewallclass(request):
    group = Class.objects.all()
    # Create a classroom
    if 'submit' in request.POST:
        user = request.user
        password = request.POST.get('psw')
        if not user.check_password(password):
            messages.error(request,'Incorrect administrative password')
            return redirect('viewall')
        role = Role.objects.filter(role='class teacher').exists()
        if not role:
            messages.error(request, "create 'class teacher' role first" )
            return redirect('role')
        getgroup = request.POST.get('group')
        if getgroup[0] == 'J':
            cat = 'junior'
        else:
            cat = 'senior'
        
        if getgroup == 'JS1':
            level = 1
        elif getgroup == 'JS2':
            level = 2
        elif getgroup == 'JS3':
            level = 3
        elif getgroup == 'SS1':
            level = 4
        elif getgroup == 'SS2':
            level = 5
        elif getgroup == 'SS3':
            level = 6

        if Class.objects.filter(group=getgroup).exists():
            messages.error(request, f'{getgroup} already exist')
            return redirect('viewall')
        Class.objects.create(group=getgroup, category=cat, level=level, added_by=request.user)
        # AllClass.objects.create(
        #     group=getgroup, arm=firstarm, teacher=getgroup+firstarm, lock=0, active=1, added_by=request.user,
        #     session=session, term=term, year=year
        # )
        # user = User.objects.create_user(getgroup + firstarm,getgroup+firstarm+'@'+domain_name,'classteacher')

        # # Assign previllage
        # userid = User.objects.get(username=getgroup+firstarm).id
        # getusergroup = Group.objects.get(name='class-teacher')
        # getusergroup.user_set.add(userid)

        # user.is_staff = False
        # user.first_name = getgroup
        # user.last_name = firstarm
        # user.save()
        # getuser = user.id

        # getroleid = Role.objects.get(role = 'class teacher')
        # Profile.objects.filter(user_id = getuser).update(role_id = getroleid)
        # Profile.objects.filter(user_id = getuser).update(passport = 'passport.jpg')
        # messages.success(request,'Created')
        # return redirect('viewall')
    context = {'class':group}
    return render(request, 'configuration/classall.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def group(request):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year
    school_name = Config.objects.get(id=1).school_name
    domain_name = Config.objects.get(id=1).school_domain_name
    group = AllClass.objects.all()
    allgroup = Class.objects.all()
    arm = Arm.objects.all
    
    # Create a unit class
    if 'submit1' in request.POST:
        password = request.POST.get('psw2')
        group = request.POST.get('allgroup')
        arm = request.POST.get('arm')
        if not request.user.check_password(password):
            messages.error(request, 'Incorrect administrative password')
            return redirect('class')
        armdeaexist = AllClass.objects.filter(group = group,arm=arm,active=0)
        armactexist = AllClass.objects.filter(group = group,arm=arm,active=1).exists()
        if armdeaexist.exists():
            armdeaexist.update(active = 1)
            messages.success(request,'Returned deactivated class')
            return redirect('class')
        
        if armactexist:
            messages.error(request,'Class already exist')
            return redirect('class')
        
        new_password = randrange(100000,999999,3)
        encryt_pass = encryptClass(new_password)
        getgroup = Class.objects.get(group=group)
        AllClass.objects.create(
            group=group,arm=arm,teacher= group+arm,lock=0,active=1,added_by=request.user,access=encryt_pass,category=getgroup.category
        )
        user = User.objects.create_user(group + arm,group+arm+'@'+domain_name,str(new_password))
        user.is_staff = False
        user.first_name = group
        user.last_name = arm
        user.save()
        getuser = user.id

        # # Assign previllage
        user = User.objects.get(username=group+arm)
        getusergroup = Group.objects.get(name='class-teacher')
        getusergroup.user_set.add(user.id)

        getroleid = Role.objects.get(role = 'class teacher')
        Profile.objects.filter(user_id = getuser).update(role_id = getroleid)
        Profile.objects.filter(user_id = getuser).update(passport = 'passport.jpg')
        

        # email = Staff.objects.get(registration_number = teacher).email
        # ln = Staff.objects.get(registration_number = teacher).last_name
        # fn = Staff.objects.get(registration_number = teacher).first_name
        # subject = f'{group}{arm} class login'
        # recipient = [email]
        # text_content = f'{school_name} Hello {fn} {ln} thanks for choosing {school_name}.Your login credential are:Application number:{group+arm} Password:classteacher'
        # html_content = f'<div><h3 style="color:purple">{school_name}</h3></div><div><p>Hello {fn} {ln} thanks for choosing GREEN PARK ACADEMY.</p><p>Your login credential for {group}{arm} class is:</p><p>Class number: {group}{arm}</p><p>Password: classteacher</p></div>'
        # message = EmailMultiAlternatives(subject=subject, body=text_content, to=recipient)
        # message.attach_alternative(html_content, 'text/html')
        # message.send()
        messages.success(request,'Done')
        return redirect('class')

    # Assign class to a staff
    elif 'submit2' in request.POST:
        staff = request.POST.get('reg2')
        group = request.POST.get('allgroup2')
        arm = request.POST.get('arm2')
        password = request.POST.get('psw')
        upload = request.FILES.get('sign')
        fss = FileSystemStorage(location='media/signature')
        file = fss.save(upload.name, upload)
        if request.user.check_password(password):
            messages.error(request, 'Incorrect administrative password')
            return redirect('class')
        getstaff = Staff.objects.filter(registration_number=staff)
        grouprow = AllClass.objects.filter(group=group, arm=arm, active=1)
        alreadyexist = AllClass.objects.filter(owner = staff).exists()
        try:
            get_class = AllClass.objects.get(group=group, arm=arm)
        except AllClass.DoesNotExist:
            messages.error(request, 'Class does not exist')
            return redirect('class')
        if get_class.owner != None:
            messages.error(request,'Class already have a staff')
            return redirect('class')

        if not grouprow.exists():
            messages.error(request,'Such class/arm does not exist or not active')
            return redirect('class')
        
        if alreadyexist:
            messages.error(request,'You have already assign a class to this staff')
            return redirect('class')
        
        if not getstaff.exists():
            messages.error(request,'Sorry i cant recongize this person as a staff')
            return redirect('class')
        
        
        teacher = Staff.objects.get(registration_number=staff)
        new_password = randrange(100000,999999,3)
        encryp_pass = encryptClass(new_password)
        get_class.access = encryp_pass
        get_class.owner = staff
        get_class.class_teacher_signature = f'signature/{file}'
        get_class.class_teacher_name = f'{teacher.last_name} {teacher.first_name}'
        get_class.lock = 0
        get_class.active=1
        get_class.save()
        class_user = User.objects.get(username=f'{group}{arm}')
        class_user.set_password(str(new_password))
        class_user.save()
        
        # Send login details to class teacher
        staffID = Staff.objects.get(registration_number=staff)
        sendSMS(f'Login credential for {group}{arm} is {group}{arm} as username and {str(new_password)} as password', staffID.mobile)
        
        messages.success(request,'Done.')
        return redirect('class')
    context = {'class':group, 'allclass':allgroup, 'arm':arm}
    return render(request, 'configuration/class.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def removeclassteacher(request,pk):
    school_name = Config.objects.get(id=1).school_name
    staff = AllClass.objects.get(id=pk).owner
    group = AllClass.objects.get(id=pk).group
    arm = AllClass.objects.get(id=pk).arm
    if staff == '' or staff == None:
        messages.error(request, f'Teacher not assigned to {group}{arm} yet')

    else:
        AllClass.objects.filter(id = pk).update(owner = None)
        email = Staff.objects.get(registration_number = staff).email
        ln = Staff.objects.get(registration_number = staff).last_name
        fn = Staff.objects.get(registration_number = staff).first_name
        subject = f'{group}{arm} class info'
        recipient = [email]
        text_content = f'{school_name} Hello {fn} {ln} thanks for choosing {school_name}.Your access for {group}{arm} class has been revoked'
        html_content = f'<div><h3 style="color:purple">{school_name}</h3></div><div><p>Hello {fn} {ln} thanks for choosing {school_name}.</p><p>Your access for {group}{arm} class has been revoked</div>'
        message = EmailMultiAlternatives(subject=subject, body=text_content, to=recipient)
        message.attach_alternative(html_content, 'text/html')
        message.send()
        messages.success(request,'Done')
    return redirect('class')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def deactivateclass(request,pk):
    AllClass.objects.filter(id = pk).update(active = 0)
    getuser = AllClass.objects.get(id=pk).teacher
    AllClass.objects.filter(id = pk).update(owner = None)
    User.objects.filter(username = getuser).update(is_active = 0)
    messages.success(request,'Done')
    return redirect('class')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def activateclass(request,pk):
    AllClass.objects.filter(id = pk).update(active = 1)
    getuser = AllClass.objects.get(id=pk).teacher
    User.objects.filter(username = getuser).update(is_active = 1)
    messages.success(request,'Done')
    return redirect('class')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def arm(request):
    arm = Arm.objects.all()
    if request.method == 'POST':
        arm = request.POST.get('arm')
        user = request.user
        password = request.POST.get('psw')
        if not user.check_password(password):
            messages.error(request,'Incorrect administrative password')
            return redirect('arm')
        if len(Arm.objects.filter(arm=arm)) == 0:
            Arm.objects.create(arm=arm, added_by=user)
            messages.success(request,'Created')
        else:
            messages.error(request,'Arm already created')
        return redirect('arm')
    context = {'arm':arm}
    return render(request, 'configuration/arm.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def newrole(request):
    if 'submit' in request.POST:
        role = request.POST.get('role')
        user = request.user
        password = request.POST.get('psw')
        checkrole = Role.objects.filter(role = role)
        if not user.check_password(password):
            messages.error(request,'Incorrect administrative password')
            return redirect('role')
        if not checkrole.exists():
            rand = str(randrange(123,999,5))
            while Role.objects.filter(code=rand).exists():
                rand = str(randrange(123,987,6))
            Role.objects.create(role=role, added_by=request.user, code=rand)
            getkeyword = Role.objects.get(role = role).keyword
            Group.objects.create(name=getkeyword)
            messages.success(request,'Done')
            return redirect('role')
        else:
            messages.error(request,f'{role} already exist')
            return redirect('role')
            
    return render(request, 'configuration/addstaff.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def category(request):
    if 'submit' in request.POST:
        category = request.POST.get('category')
        code = request.POST.get('code')
        checkcat = Category.objects.filter(category = category)
        user = request.user
        password = request.POST.get('psw')
        if not user.check_password(password):
            messages.error(request,'Incorrect administrative password')
            return redirect('role')
        if not checkcat.exists():
            Category.objects.create(category=category,code=code,added_by=request.user)
            messages.success(request,'Craeted')
            return redirect('category')
        else:
            messages.error(request,f'{category} already exist')
            return redirect('category')
            
    return render(request, 'configuration/category.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def subject(request):
    allsubject = AllSubject.objects.all()
    subject = Subject.objects.all()
    group = Class.objects.all()
    arm = Arm.objects.all()
    category = Category.objects.all()
    user = request.user
    # To add new subject
    if 'submit' in request.POST:
        sub = request.POST.get('subject')
        cat = request.POST.get('cat')
        opt_arm = request.POST.get('oarm')
        password = request.POST.get('psw1')
        if not user.check_password(password):
            messages.error(request,'Incorrect administrative password')
            return redirect('subject')
        if not AllSubject.objects.filter(subject = sub,category = cat).exists():
            AllSubject.objects.create(subject=sub, category=cat, added_by = request.user)
            if cat == 'junior':
                group_cat = Class.objects.filter(category='junior').values()
                for specific_cat in group_cat:
                    auto_group = AllClass.objects.filter(group=specific_cat.get('group'))
                    for unit_auto_group in auto_group:
                        print(unit_auto_group)
                        Subject.objects.create(subject=sub, category=cat, group=unit_auto_group.group, arm=unit_auto_group.arm, added_by=user)
            # These block is not generic for all schools
            # Manually make change as need be
            elif cat == 'senior':
                group_cat = Class.objects.filter(category='senior').values()
                for specific_cat in group_cat:
                    if opt_arm != 'BOTH':
                        auto_group = AllClass.objects.filter(group=specific_cat.get('group'),arm=opt_arm)
                        for unit_auto_group in auto_group:
                            print(unit_auto_group)
                            Subject.objects.create(subject=sub, category=cat, group=unit_auto_group.group, arm=unit_auto_group.arm, added_by=user)
                    else:
                        auto_group = AllClass.objects.filter(group=specific_cat.get('group'))
                        for unit_auto_group in auto_group:
                            print(unit_auto_group)
                            Subject.objects.create(subject=sub, category=cat, group=unit_auto_group.group, arm=unit_auto_group.arm, added_by=user)
            
            messages.success(request,"Done: Click on 'view all subject' to see all available subjects")
        else:
            messages.error(request,f'{sub} for {cat} categoty already exist')
        return redirect('subject')
    # To assign subject to a subject teacher
    elif 'submit1' in request.POST:
        subcat = request.POST.get('subject')
        getgroup = request.POST.get('group')
        getarm = request.POST.get('arm')
        staff = request.POST.get('teacher')
        getcat = Class.objects.get(group=getgroup).category
        password = request.POST.get('psw2')
        if not user.check_password(password):
            messages.error(request,'Incorrect administrative password')
            return redirect('subject')

        # Variable holding list of subject and category
        subcatlist = subcat.split(", ")
        sub = str(subcatlist[0])
        cat = str(subcatlist[1])

        if Staff.objects.filter(registration_number = staff).exists():
            if Subject.objects.filter(subject=sub,teacher=None,category=cat,group=getgroup,arm=getarm).exists():
                Subject.objects.filter(subject=sub,teacher=None,category=cat,group=getgroup,arm=getarm).update(teacher=staff)
                messages.success(request,'Updated')
                return redirect('subject')
            if getcat == cat:
                if not Subject.objects.filter(subject=sub,category=cat,group=getgroup,arm=getarm).exists():
                    Subject.objects.create(subject=sub,group=getgroup, arm=getarm, teacher=staff, category=cat, added_by = request.user)
                    messages.success(request,'Done')
                else:
                    messages.error(request,'This subject has been assign to someone else, use the remove assign button first if you want to change the \'Teacher in charge\'')
            else:
                messages.error(request,'category selected did not match the class')
        else:
            messages.error(request,f'Sorry i cant recognise {staff} as a staff')
        return redirect('subject')
    context = {'subject':subject,'allsubject':allsubject,'group':group,'arm':arm,'category':category}
    return render(request, 'configuration/subject.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def removeassign(request,pk):
    Subject.objects.filter(ref = pk).update(teacher = None)
    messages.success(request,'Removed successful')
    return redirect('subject')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def manualUpdate(request):
    school_group = Class.objects.all()
    arm = Arm.objects.all()
    if 'dob' in request.POST:
        students=Student.objects.all().values()
        staffs=Staff.objects.all().values()
        for student in students:
            # print(student)
            dob = student.get('dob')
            if dob is not None:
                person = Student.objects.get(registration_number=student.get('registration_number'))
                person.birth_day=dob.day
                person.birth_month=dob.month
                person.birth_year=dob.year
                person.save()
        for staff in staffs:
            # print(student)
            dob = staff.get('dob')
            if dob is not None:
                print(staff.get('registration_number'))
                person = Staff.objects.get(registration_number=staff.get('registration_number'))
                person.birth_day=dob.day
                person.birth_month=dob.month
                person.birth_year=dob.year
                person.save()
        messages.success(request, 'successful')
        return redirect('secret')

    elif 'class' in request.POST:
        groups = AllClass.objects.all().values()
        for group in groups:
            print(group)
            new_group = group.get('group')
            new_arm = group.get('arm')
            student_len = len(Student.objects.filter(group=new_group, arm=new_arm, active=1))
            group_instance = AllClass.objects.get(group=new_group, arm=new_arm)
            group_instance.number_of_student = student_len
            group_instance.save()
        messages.success(request, 'Done')
        return redirect('secret')

    elif 'reg' in request.POST:
        duplicate_reg = request.POST.get('reg1')
        
    elif 'assign' in request.POST:
        all_staffs = Staff.objects.all()
        staffs_reg = []
        for unit_staff in all_staffs:
            staffs_reg.append(unit_staff.registration_number)
        
        # For subject teacher
        subjects = Subject.objects.all()
        for unit_subject in subjects:
            unit_subject.teacher = choice(staffs_reg)
            unit_subject.save()

        messages.success(request, 'Done')
        return redirect('secret')
    
    elif 'assign_class' in request.POST:
        all_staffs = Staff.objects.all()
        staffs_reg = []
        for unit_staff in all_staffs:
            staffs_reg.append(unit_staff.registration_number)
        
        # For subject teacher
        subjects = AllClass.objects.all()
        for unit_subject in subjects:
            unit_subject.owner = choice(staffs_reg)
            unit_subject.save()

        messages.success(request, 'Done')
        return redirect('secret')
    
    elif 'class_cat' in request.POST:
        all_class = AllClass.objects.all()
        for unit_class in all_class:
            getgroup = Class.objects.get(group=unit_class.group)
            unit_class.category=getgroup.category
            unit_class.save()
            messages.success(request, 'Done')
        return redirect('secret')
    
    elif 'ss3art_subject' in request.POST:
        ss3art_students = Student.objects.filter(group='SS3',arm='ART')
        subjects_list = ['Mathematics','English Language','Civic Education','Biology','Igbo Language','Government','CRS','Literature in English']
        for s in ss3art_students:
            for sub in subjects_list:
                RegisteredSubjects.objects.create(
                    last_name=s.last_name,first_name=s.first_name,student=s.registration_number,subject=sub,group=s.group,arm=s.arm,
                    session='2023/2024',category='senior',added_by=request.user
                )
        messages.success(request, 'Done')
        return redirect('secret')

    elif 'reg_in_card' in request.POST:
        students = Student.objects.all()
        cards = Card.objects.all().order_by('created')
        for count, stu in enumerate(students):
            Card.objects.filter(id=count+1).update(
                student=stu.registration_number,group=stu.group,arm=stu.arm,term='1'
            )
        messages.success(request, 'Success')
        return redirect('secret')

    elif 'rand_pass' in request.POST:
        students = Student.objects.all()
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        counter = 1
        for stud in students:
            random_pass = randrange(1000000,9999999)
            try:
                u = User.objects.get(username=stud.registration_number)
                u.set_password(str(random_pass))
                data = list((stud.registration_number,random_pass))
                writer.writerow(data)
                print(counter,stud.registration_number,random_pass)
                counter+=1
            except User.DoesNotExist:
                continue
        response['Content-Disposition'] = f'attachment; filename="password.csv"'
        return response
    
    elif 'upload_pass' in request.POST:
        csv_file = request.FILES["file"]
        minimum = int(request.POST.get('min'))
        maximum = int(request.POST.get('max'))
        if not csv_file.name.endswith('.csv'):
            messages.warning(request,'File is not CSV type')
            return redirect('secret')
        file = csv_file.read().decode('utf-8')
        csv_data = csv.reader(StringIO(file), delimiter=',')
        # next(csv_data)
        counter = 0
        for line in csv_data:
            if counter >= minimum and counter <= maximum:
                reg = str(line[0])
                psd = str(line[1])
                try:
                    u = User.objects.get(username=reg)
                    u.set_password(psd)
                    u.save()
                except User.DoesNotExist:
                    continue   
                print(counter,reg,psd)
            counter+=1       
        messages.success(request, 'Done')
        return redirect('secret')
    
    elif 'clear_all_student' in request.POST:
        term = Term.objects.get(active=1)
        session = Session.objects.get(active=1)
        students = Student.objects.filter(active=1)
        for i in students:
            Paid_Student.objects.create(
                student=i.registration_number, amount_paid=0, email=i.email, term=term.term, session=session.session,
                year=session.year, group=i.group, arm=i.arm
            )
        messages.success(request, 'Done')
        return redirect('secret')
    
    elif 'fix_second_term_avg_score' in request.POST:
        avg_scores = Result.objects.filter(term=3,session='2023/2024')
        for i in avg_scores:
            number_of_subjects = RegisteredSubjects.objects.filter(session='2023/2024',student=i.student)
            new_avg = i.total/len(number_of_subjects)
            i.average = new_avg
            if(new_avg >= 40):
                i.remark = 'PASS'
            else:
                i.remark = 'FAIL'
            i.save()
        
        avg_scores = Result.objects.filter(term=4,session='2023/2024')
        for i in avg_scores:
            number_of_subjects = RegisteredSubjects.objects.filter(session='2023/2024',student=i.student)
            new_avg = i.total/len(number_of_subjects)
            i.average = new_avg
            if(new_avg >= 40):
                i.remark = 'PROMOTED'
            else:
                i.remark = 'NOT PROMOTED'
            i.save()
        messages.success(request, 'Done')
        return redirect('secret')
            
    elif 'add_session' in request.POST:
        subs = RegisteredSubjects.objects.filter(session=None)
        for i in subs:
            i.session = '2023/2024'
            i.save()
        messages.success(request, 'Done')
        return redirect('secret')

    elif 'change_pre_to_nation' in request.POST:
        Subject.objects.filter(subject='Security Education').update(subject='National Values')
        Record.objects.filter(subject='Security Education').update(subject='National Values')
        RegisteredSubjects.objects.filter(subject='Security Education').update(subject='National Values')
        messages.success(request, 'Done')
        return redirect('secret')

    elif 'remove_excess_subject' in request.POST:
        RegisteredSubjects.objects.filter(category='junior',subject='Security Education').delete()
        RegisteredSubjects.objects.filter(category='junior',subject='Physical and Health Education').delete()
        RegisteredSubjects.objects.filter(category='junior',subject='Basic Science').delete()
        RegisteredSubjects.objects.filter(category='junior',subject='Basic Technology').delete()
        RegisteredSubjects.objects.filter(category='junior',subject='Civic Education').delete()
        messages.success(request, 'Done')
        return redirect('secret')
    
    elif 'fix_civic_senior' in request.POST:
        subs = RegisteredSubjects.objects.filter(category='senior',subject='Mathematics')
        for i in subs:
            RegisteredSubjects.objects.create(
                student=i.student,group=i.group,arm=i.arm,session=i.session,active=True,
                lock=True,subject='Civic Education',first_name=i.first_name,last_name=i.last_name,
                added_by=request.user
            )
        messages.success(request, 'Done')
        return redirect('secret')
    
    elif 'remove_duplicate_record' in request.POST:
        subss = [
            ['JS3','YELLOW','Basic Science and Technology'],
            ['SS2','ART','CRS']
        ]
        studss = Student.objects.filter(active=1)
        for sub in subss:
            unitgroup = sub[0]
            unitarm = sub[1]
            for stud in studss:
                duplicate = Record.objects.filter(student=stud.registration_number,group=unitgroup,arm=unitarm,term=2,subject=sub[2])
                if duplicate.count() > 1:
                    duplicate.first().delete()
                    # print(f'{sub[0]}{sub[1]} {sub[2]}, {stud.registration_number}')
        messages.success(request, 'Done')
        return redirect('secret')

    elif 'clear_student_tuition' in request.POST:
        session = Session.objects.get(active=True)
        term = Term.objects.get(active=True)
        students = Student.objects.filter(active=1)
        for student in students:
            if(Paid_Student.objects.filter(student=student.registration_number,term=term.term,session=session.session).exists()):
                continue
            Paid_Student.objects.create(
                student=student.registration_number,amount_paid=0,email=student.email,
                term=term.term,session=session.session,year=session.year,group=student.group,arm=student.arm,
                status=True,print=True,complete=True
            )
        messages.success(request, 'Done')
        return redirect('secret')

    elif 'move_js3_to_ss1' in request.POST:
        session = Session.objects.get(active=True)
        term = Term.objects.get(active=True)
        students = Student.objects.filter(active=0, graduated=True, group='JS3')
        demo_list = [
            "DEMO211001", "DEMO211002", "DEMO211003", "DEMO211004", "DEMO211005", "DEMO211006", 
            "DEMO211007", "DEMO211008", "DEMO211009", "DEMO211010", "DEMO211011", "DEMO211012", 
            "DEMO211013", "DEMO211014", "DEMO211015", "DEMO211016", "DEMO211017", "DEMO211018", 
            "DEMO211019", "DEMO211020", "DEMO211021", "DEMO211022", "DEMO211023", "DEMO211024", 
            "DEMO211025", "DEMO211026", "DEMO211027", "DEMO211028", "DEMO211029", "DEMO211030", 
            "DEMO211031", "DEMO211032", "DEMO211033", "DEMO211034", "DEMO211035", "DEMO211036", 
            "DEMO211037", "DEMO211038", "DEMO211039", "DEMO211040", "DEMO211041", "DEMO211042", 
            "DEMO211043", "DEMO211044", "DEMO211045", "DEMO211046", "DEMO211047", "DEMO211048", 
            "DEMO211049", "DEMO211050", "DEMO211051", "DEMO211052", "DEMO211053", "DEMO211054", 
            "DEMO211055", "DEMO211056", "DEMO211057", "DEMO211058", "DEMO211059", "DEMO211060", 
            "DEMO211061", "DEMO211062", "DEMO211063", "DEMO211064", "DEMO211065", "DEMO211066", 
            "DEMO211067", "DEMO211068", "DEMO211069", "DEMO211070", "DEMO211071", "DEMO211072", 
            "DEMO211073", "DEMO211074", "DEMO211075", "DEMO211076", "DEMO211077", "DEMO211078", 
            "DEMO211079", "DEMO211080", "DEMO211081", "DEMO211082", "DEMO211083", "DEMO211084", 
            "DEMO211085", "DEMO211086", "DEMO211087", "DEMO211088", "DEMO211089", "DEMO211090", 
            "DEMO211091", "DEMO211092", "DEMO211093", "DEMO211094", "DEMO211095", "DEMO211096", 
            "DEMO211097", "DEMO211098", "DEMO211099", "DEMO211100", "DEMO211101", "DEMO211102", 
            "DEMO211103", "DEMO211104", "DEMO211105", "DEMO211106", "DEMO211107", "DEMO211108", 
            "DEMO211109", "DEMO211110", "DEMO211111", "DEMO211112", "DEMO211113", "DEMO211114", 
            "DEMO211115", "DEMO211116", "DEMO211117", "DEMO211118", "DEMO211119", "DEMO211120", 
            "DEMO211121", "DEMO211122", "DEMO211123", "DEMO211124", "DEMO211125", "DEMO211126", 
            "DEMO211127", "DEMO211128", "DEMO211129", "DEMO211130"
        ]

        counter = 0
        for student in demo_list:
            group = AllClass.objects.get(group='SS1',arm='SCIENCE')
            Student.objects.filter(registration_number=student).update(
                graduated=False,active=1,group=group.group,arm=group.arm,category=group.category
            )
            counter+=1

        groups = AllClass.objects.all()
        for group in groups:
            studentLen = len(Student.objects.filter(group=group.group,arm=group.arm))
            AllClass.objects.filter(id=group.id).update(
                number_of_student=studentLen
            )
        messages.success(request, f'{counter} students moved')
        return redirect('secret')
    
    context = {
        'group':school_group,
        'arm':arm
    }
    return render(request, 'configuration/sec.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def backupData(request):
    if request.method == "POST":
        dbaseDetail = settings.DATABASES['default']
        host = dbaseDetail['HOST']
        user = dbaseDetail['USER']
        psw = dbaseDetail['PASSWORD']
        db = dbaseDetail['NAME']

        print(f'host:{host},\nuser:{user},\npassword:{psw},\ndatabase:{db}')

        directory = '/home'
        outputFile = os.path.join(directory,'dump.sql')

        cmd = f'mysqldump -h {host} -u {user} -p {psw} {db} > {outputFile}'
        output = subprocess.run(cmd, shell=True)

        messages.success(request, 'Done')
        return redirect('backup')
    return render(request, 'configuration/backup.html')