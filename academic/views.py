from django.shortcuts import render, redirect
from configuration.models import AllClass, AllSubject, Arm, Class, Session, Subject, Term, Config,RegisteredSubjects
from academic.models import Record
from student.models import Student
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from lms.decorators import allowed_users
import csv
from .functions import calculate_result

# Create your views here.

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher'])
def computation_error(request):
    return render(request, 'academic/computationerror.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','controller'])
def admin_assessment(request):
    term = Term.objects.get(active = 1).term
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year
    usub = Subject.objects.filter(lock = 0)
    subject = Subject.objects.filter(lock=0).order_by('group','arm','subject')
    adminGetTemplate = Subject.objects.all().order_by('group','arm','subject')
    getgroup = Class.objects.all()
    getarm =  Arm.objects.all()
    if Config.objects.get(id=1).start_result == 0:
        return redirect('computation_error')

    if 'manualupload' in request.POST:
        mall = request.POST.get('mass')
        mallsplit = mall.split(', ')
        mgroup = mallsplit[1]
        marm = mallsplit[2]
        getsubject = mallsplit[0]
        ass = request.POST.get('ass')
        score = request.POST.get('score')
        reg_num =request.POST.get('reg_num')
        
        if ass == 'CA1':
            new_value = {'CA1':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'CA2':
            new_value = {'CA2':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'CA3':
            new_value = {'CA3':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'project':
            new_value = {'project':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'test':
            new_value = {'test':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'exam':
            new_value = {'exam':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        else:
            User.objects.filter(username=request.user.username).update(is_active=False)
            messages.error(request,'Self destruction activated')
            redirect('admin_assessment')
        messages.success(request,f'Added successful')
        redirect('admin_assessment')

    # For csv upload

    if 'csvupload' in request.POST:
        csv_file = request.FILES["file"]
        if not csv_file.name.endswith('.csv'):
            messages.warning(request,'File is not CSV type')
            return redirect('admin_assessment')
        getUploadSubjectRef = request.POST.get('subject')
        try:
            uploadSubject = Subject.objects.get(ref=getUploadSubjectRef)
        except Subject.DoesNotExist:
            User.objects.filter(username=request.user.username).update(is_active=False)
            messages.error(request,'Self destruction activated')
            return redirect('admin_assessment')
        
        uusub = uploadSubject.subject
        uugroup = uploadSubject.group
        uuarm = uploadSubject.arm
        check_sum = round(float(request.POST.get('summer')),2)
        calculate_result(request,uugroup,uuarm,uusub,csv_file,term,session,year,check_sum)

    # Get template
    if 'submit' in request.POST:
        getAdminSubject = request.POST.get('subject')
        try:
            adminSubject = Subject.objects.get(ref=getAdminSubject)
        except Subject.DoesNotExist:
            User.objects.filter(username=request.user.username).update(is_active=False)
            messages.error(request,'Self destruction activated')
            return redirect('admin_assessment')
        cca1 = 0
        cca2 = 0
        cexam = 0

        group = adminSubject.group
        arm = adminSubject.arm
        sub = adminSubject.subject

        studentand = RegisteredSubjects.objects.filter(group=group,arm=arm,active=1,subject=sub,lock=1).order_by('last_name','first_name')
        print(studentand)
        student = studentand.values_list('last_name','first_name','student','group','arm','subject')
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Registration Number','Class','Arm','Subject','CA1','CA2','Exam'])
        if len(student) == 0:
            messages.error(request,'No record found')
            return redirect('assessment')
        else:
            for student in student:
                stud = list(student)
                if Record.objects.filter(student=stud[2],subject=sub,group=group,arm=arm,term=term).exists():
                    cca1 = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).CA1
                    cca2 = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).CA2
                    # cca3 = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).CA3
                    # cproject = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).project
                    # ctest = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).test
                    cexam = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).exam
                stud.extend([cca1,cca2,cexam])
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{group}{arm} {sub} CA.csv"'
            return response

    context = {
        'subject':subject,
        'usub':usub,
        'group':getgroup,
        'arm':getarm,
        'admin_template_subject':adminGetTemplate
    }
    return render(request, 'academic/admin_assessment.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['subject-teacher'])
def assessment(request):
    term = Term.objects.get(active = 1).term
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year
    usub = Subject.objects.filter(teacher = request.user, lock = 0)
    subject = Subject.objects.filter(teacher = request.user)
    if Config.objects.get(id=1).start_result == 0:
        return redirect('computation_error')

    if 'manualupload' in request.POST:
        mall = request.POST.get('mass')
        mallsplit = mall.split(', ')
        mgroup = mallsplit[1]
        marm = mallsplit[2]
        getsubject = mallsplit[0]
        ass = request.POST.get('ass')
        score = request.POST.get('score')
        reg_num =request.POST.get('reg_num')
        
        if ass == 'CA1':
            new_value = {'CA1':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'CA2':
            new_value = {'CA2':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'CA3':
            new_value = {'CA3':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'project':
            new_value = {'project':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'test':
            new_value = {'test':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        elif ass == 'exam':
            new_value = {'exam':score,'term':term,'added_by':request.user}
            Record.objects.update_or_create(group=mgroup,arm=marm,subject=getsubject,student=reg_num,defaults=new_value)
        else:
            messages.success(request,'Self destruction activated')
            redirect('assessment')
        messages.success(request,f'Added successful')
        redirect('assessment')

    # For csv upload

    if 'csvupload' in request.POST:
        csv_file = request.FILES["file"]
        if not csv_file.name.endswith('.csv'):
            messages.warning(request,'File is not CSV type')
            return redirect('assessment')
        getsub = request.POST.get('usub')
        getsublist = getsub.split(', ')
        uusub = getsublist[0]
        uugroup = getsublist[1]
        uuarm = getsublist[2]
        check_sum = round(float(request.POST.get('summer')),2)
        calculate_result(request,uugroup,uuarm,uusub,csv_file,term,session,year,check_sum)

    # Get template
    if 'submit' in request.POST:
        iall = request.POST.get('subject')
        iallsplit = iall.split(', ')
        group = iallsplit[1]
        arm = iallsplit[2]
        sub = iallsplit[0]
        cca1 = 0
        cca2 = 0
        cca3 = 0
        cproject = 0
        ctest = 0
        cexam = 0

        print(group,arm)

        studentand = RegisteredSubjects.objects.filter(group=group,arm=arm,active=1,subject=sub,lock=1).order_by('last_name')
        print(studentand)
        student = studentand.values_list('last_name','first_name','student','group','arm','subject')
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Registration Number','Class','Arm','Subject','CA1','CA2','Exam'])
        if len(student) == 0:
            messages.error(request,'No record found')
            return redirect('assessment')
        else:
            for student in student:
                stud = list(student)
                if Record.objects.filter(student=stud[2],subject=sub,group=group,arm=arm,term=term).exists():
                    cca1 = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).CA1
                    cca2 = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).CA2
                    # cca3 = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).CA3
                    # cproject = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).project
                    # ctest = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).test
                    cexam = Record.objects.get(student=stud[2],subject=sub,group=group,arm=arm,term=term).exam
                stud.extend([cca1,cca2,cexam])
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{group}{arm} {sub} CA.csv"'
            return response

    context = {'subject':subject, 'usub':usub}
    return render(request, 'academic/assessment.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','class-teacher'])
def eassessment(request):
    term = Term.objects.get(active = 1).term
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year
    subject = Subject.objects.filter(teacher=request.user)
    if request.method == 'POST':
        isub = request.POST.get('subject')
        isubsplit = isub.split(', ')
        mgroup = isubsplit[1]
        marm = isubsplit[2]
        getsubject = isubsplit[0]
        mark = request.POST.get('mark')
        allowed_question = request.POST.get('answer')

        

        # Setup.objects.create(
        #     mark_per_question=mark,allowed_question=allowed_question,added_by=request.user,
        #     subject=getsubject,group=mgroup,arm=marm,term=term,year=year,session=session
        # )

        messages.success(request, f'E-assessment for {getsubject} in {mgroup}{marm} is successful')

        # TODO: Check if number of question to answer is less than all equal to total number of question
    context = {'subject':subject}
    return render(request,'academic/eassessment.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['class-teacher'])
def class_academics(request):
    group = AllClass.objects.get(teacher=request.user.username)
    if request.method == 'POST':
        ca_max = request.POST.get('ca_max')
        exam_max = request.POST.get('exam_max')
        promotion = request.POST.get('promote')
        AllClass.objects.filter(teacher=request.user.username).update(CA_max=ca_max,exam_max=exam_max,promotion_score=promotion)
        
        messages.success(request, 'Changes added successfully')
        return redirect('class_academics')
    context = {'group':group}
    return render(request, 'academic/class_academics.html', context)