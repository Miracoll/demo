from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from academic.models import Record
from lms.decorators import allowed_users
from lms.models import Profile
from configuration.models import Class, Arm, AllClass, RegisteredSubjects,Term, Session, AllSubject
from result.models import Result
from .models import Student
from .forms import StudentImage, ProfileImage
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth.models import User
from configuration.models import Config
from lms.functions import registerSeniorStudentCourse, removeStudentCourse
from configuration.models import Config

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image

# Create your views here.

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def student(request):
    return render(request, 'student/student.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def transferstudent(request):
    group = Class.objects.all()
    arm = Arm.objects.all()
    if 'submit' in request.POST:
        config = Config.objects.get(id=1)
        if config.start_result:
            messages.error(request, "Can't transfer student while result computation is active")
            return redirect('transfer_student')

        reg = request.POST.get('reg_num')
        getarm = request.POST.get('armget')
        getgroup = request.POST.get('group')
        oldgroup = Student.objects.get(registration_number = reg).group
        oldarm = Student.objects.get(registration_number = reg).arm

        Student.objects.filter(registration_number = reg).update(group=getgroup,arm=getarm)
        # get current
        oldnos = len(Student.objects.filter(group = oldgroup, arm = oldarm, active = 1))
        AllClass.objects.filter(group=oldgroup, arm=oldarm).update(number_of_student = oldnos)
        # get new
        nos = len(Student.objects.filter(group = getgroup, arm = getarm, active = 1))
        AllClass.objects.filter(group=getgroup, arm=getarm).update(number_of_student = nos)
        # Apply changes in registered subjects table
        RegisteredSubjects.objects.filter(student=reg).update(group=getgroup,arm=getarm)
        messages.success(request,'Update successful')
        return redirect('transfer_student')
    context = {'group':group,'arm':arm}
    return render(request, 'student/studenttransfer.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def disablestudent(request):
    if 'submit' in request.POST:
        config = Config.objects.get(id=1)
        if config.start_result:
            messages.error(request, "Can't diable student while result computation is active")
            return redirect('transfer_student')
        reg = request.POST.get('reg_num')
        # getgroup = Student.objects.get(registration_number = reg).group
        # getarm = Student.objects.get(registration_number = reg).arm
        student = Student.objects.filter(registration_number=reg)
        active = User.objects.filter(username = reg)
        student.update(active=0)
        active.update(is_active = 0)
        # nos = len(Student.objects.filter(group = getgroup, arm = getarm, active = 1))
        # AllClass.objects.filter(group=getgroup, arm=getarm).update(number_of_student = nos)
        messages.success(request,'Update successful')
        return redirect('disable_student')
    return render(request, 'student/studentdisable.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','controller'])
def enablestudent(request):
    if 'submit' in request.POST:
        config = Config.objects.get(id=1)
        if config.start_result:
            messages.error(request, "Can't enable student while result computation is active")
            return redirect('transfer_student')
        reg = request.POST.get('reg_num')
        # getgroup = Student.objects.get(registration_number = reg).group
        # getarm = Student.objects.get(registration_number = reg).arm
        student = Student.objects.filter(registration_number=reg)
        active = User.objects.filter(username = reg)
        student.update(active=1)
        active.update(is_active = 1)
        # nos = len(Student.objects.filter(group = getgroup, arm = getarm, active = 1))
        # AllClass.objects.filter(group=getgroup, arm=getarm).update(number_of_student = nos)
        messages.success(request,'Update successful')
        return redirect('enable_student')
    return render(request, 'student/studentenable.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal'])
def editreg(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        new_reg = request.POST.get('new_reg_num')
        if Student.objects.filter(registration_number=reg).exists():
            if User.objects.filter(username=new_reg).exists() or Student.objects.filter(registration_number=new_reg).exists():
                messages.error(request, f'Registration number already taken')
                return redirect('edit_reg')
            else:
                student = Student.objects.filter(registration_number=reg)
                student.update(registration_number=new_reg)
                User.objects.filter(username = reg).update(username = new_reg)
                messages.success(request,'Update successful')
                return redirect('edit_reg')
        else:
            messages.error(request, f'Registration number({reg}) does not exist')
            return redirect('edit_reg')
    return render(request, 'student/studentregedit.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','subject-teacher','controller'])
def getstudent(request):
    errormsg = False
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        try:
            student = Student.objects.get(registration_number=reg).ref
            return redirect('manage_student',student)
        except Student.DoesNotExist:
            errormsg = True
    return render(request, 'student/studentget.html',{'errormsg':errormsg})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','class-teacher','subject-teacher','controller'])
def managestudent(request,pk):
    person = Student.objects.get(ref=pk)
    form = StudentImage(instance=person)
    # print(form)
    if 'submit1' in request.POST:
        form = StudentImage(request.POST, request.FILES, instance=person)
        if form.is_valid():
            formInstance = form.save(commit=False)
            dob = str(form.cleaned_data.get('dob')).split('-')
            print(dob)
            formInstance.birth_day = dob[2]
            formInstance.birth_month = dob[1]
            formInstance.birth_year = dob[0]
            formInstance.save()
            last = form.cleaned_data.get('last_name')
            first = form.cleaned_data.get('first_name')
            email = form.cleaned_data.get('email')
            if email is None:
                email = ''

            # Update user model
            User.objects.filter(username=person.registration_number).update(last_name=last,first_name=first,email=email)
            # Update Ristered Subject model
            RegisteredSubjects.objects.filter(student=person.registration_number).update(last_name=last,first_name=first)
            
            # TODO: Delete passport before adding a new one

            messages.success(request,'Update successful')
            return redirect('manage_student',pk)

    context = {'student':person, 'form':form}
    return render(request, 'student/studentmanage.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','subject-teacher','class-teacher'])
def getstudentresult(request):
    group = AllClass.objects.filter(active=1)
    arm = Arm.objects.all()
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        student = Student.objects.get(registration_number=reg).id
        return redirect('display_result',student)
    context = {'group':group, 'arm':arm}
    return render(request, 'student/studentgetresult.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','class-teacher','controller'])
def resetstudentpassword(request):
    if request.method == 'POST':
        reg = request.POST.get('reg')
        user = User.objects.get(username=reg)
        user.set_password('student')
        user.save()
        messages.success(request, 'Password changed successfully')
        return redirect('studentpasswordreset')
    return render(request,'student/resetpassword.html')

def datasheet(request):
    allgroup = AllClass.objects.all()
    if request.method == 'POST':
        ref = request.POST.get('group')
        getgroup = AllClass.objects.get(ref=ref)
        return redirect('get-datasheet',getgroup.ref)
    context = {
        'allgroup':allgroup,
    }
    return render(request, 'student/datasheet.html',context)

def getDatasheet(request, ref):
    group = AllClass.objects.get(ref=ref)
    config = Config.objects.get(id=1)
    students = Student.objects.filter(group=group.group,arm=group.arm,active=1).order_by('last_name')
    if request.method == 'POST':
        ref = request.POST.get('group')
        # getgroup = AllClass.objects.get(ref=ref)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{group.group} {group.arm} bio-data.pdf"'
        pdf_document = SimpleDocTemplate(response, pagesize=letter)

        data1 = [
            [f'{config.school_name}'],
            [f'{group.group} {group.arm} BIO DATA'],
            ['Subject:__________________________Teacher Name________________Sign:__________'],
            ['Session:____________________________________Term:__________________'],
        ]

        data2 = [
            ['S/N','Passport','Reg Number','Last Name','First Name','Other Name','Gender'],
        ]

        counter = 1
        for student in students:
            image_path = student.passport
            image = Image(image_path, width=50, height=50)
            # data2[row_counter][1] = 'image'
            print(image)
            data2.append([str(counter),image,student.registration_number, student.last_name, student.first_name, student.other_name, student.sex])
            counter+=1

        # Create tables
        table1 = Table(data1)
        table2 = Table(data2)

        # row_counter = 1
        # for i in students:
        #     image_path = i.passport
        #     print(image_path)
        #     image = Image(image_path, width=50, height=50)  # Adjust width and height as needed
        #     data2[row_counter][1] = 'image'  # Replace the existing text with the Image object
        #     row_counter+=1
        
        style = TableStyle(
            [
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 16),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('PADDING', (0, 0), (-1, 0), 7),
            ]
        )
        
        style2 = TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]
        )

        table1.setStyle(style)
        table2.setStyle(style2)

        # Build the PDF document
        pdf_content = [table1, Spacer(1, 30), table2]
        pdf_document.build(pdf_content)

        return response
    context = {'students':students,'group':group}
    return render(request, 'student/getdatasheet.html', context)

def printSujectList(request):
    group = AllClass.objects.all()
    config = Config.objects.get(id=1)
    if request.method == 'POST':
        ref = request.POST.get('group')
        getgroup = AllClass.objects.get(ref=ref)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{getgroup.group} {getgroup.arm}.pdf"'
        pdf_document = SimpleDocTemplate(response, pagesize=(letter[1], letter[0]))

        data1 = [
            [f'{config.school_name}'],
            [f'{getgroup.group} {getgroup.arm} subject list'],
            ['Subject:__________________________Teacher Name________________Sign:__________'],
            ['Session:____________________________________Term:__________________'],
        ]

        data2 = [
            ['S/N','Reg Number','Last Name','First Name','Sub1','Sub2','Sub3','Sub4','Sub5','Subject6','Subject7','Subject8','Subject9'],
        ]

        counter = 1
        students = Student.objects.filter(group=getgroup.group, arm=getgroup.arm, active=1).order_by('last_name')
        for student in students:
            data2.append([str(counter),student.registration_number, student.last_name, student.first_name,'Math','English','Civic','Igbo','Bio'])
            counter+=1

        # Create tables
        table1 = Table(data1)
        table2 = Table(data2)
        
        style = TableStyle(
            [
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 16),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('PADDING', (0, 0), (-1, 0), 7),
            ]
        )
        
        style2 = TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]
        )

        table1.setStyle(style)
        table2.setStyle(style2)

        # Build the PDF document
        pdf_content = [table1, Spacer(1, 30), table2]
        pdf_document.build(pdf_content)

        return response
    context = {'allgroup':group}
    return render(request, 'student/printdatasheet.html', context)

def printDatasheet(request):
    group = AllClass.objects.all()
    config = Config.objects.get(id=1)
    if request.method == 'POST':
        ref = request.POST.get('group')
        getgroup = AllClass.objects.get(ref=ref)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{getgroup.group} {getgroup.arm}.pdf"'
        pdf_document = SimpleDocTemplate(response, pagesize=letter)

        data1 = [
            [f'{config.school_name}'],
            [f'{getgroup.group} {getgroup.arm} datasheet'],
            ['Subject:__________________________Teacher Name________________Sign:__________'],
            ['Session:____________________________________Term:__________________'],
        ]

        data2 = [
            ['S/N','Reg Number','Last Name','First Name','Other Name','Gender','CA1','CA2','Exam','Total'],
            ['','','','','','','20%','20%','60%','100%']
        ]

        counter = 1
        students = Student.objects.filter(group=getgroup.group, arm=getgroup.arm, active=1).order_by('last_name')
        for student in students:
            data2.append([str(counter),student.registration_number, student.last_name, student.first_name, student.other_name, student.sex])
            counter+=1

        # Create tables
        table1 = Table(data1)
        table2 = Table(data2)
        
        style = TableStyle(
            [
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 16),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('PADDING', (0, 0), (-1, 0), 7),
            ]
        )
        
        style2 = TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]
        )

        table1.setStyle(style)
        table2.setStyle(style2)

        # Build the PDF document
        pdf_content = [table1, Spacer(1, 30), table2]
        pdf_document.build(pdf_content)

        return response
    context = {'allgroup':group}
    return render(request, 'student/printdatasheet.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','class-teacher','controller'])
def getStudentRegisterCourse(request):
    if request.method == 'POST':
        reg = request.POST.get('reg')
        try:
            student = Student.objects.get(registration_number=reg)
        except Student.DoesNotExist:
            messages.error(request, 'Student not found')
            return redirect('get-student-register-course')
        if student.graduated:
            messages.error(request, 'Student already already graduated')
            return redirect('get-student-register-course')
        return redirect('register-course', student.ref)
    return render(request,'student/getstudentresgistercourse.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','class-teacher','controller'])
def registerCourse(request,ref):
    session = Session.objects.get(active=1)
    term = Term.objects.get(active=1)
    user = request.user
    student = Student.objects.get(ref=ref)
    if not student.category == 'senior':
        messages.info(request, 'Junior category subjects will be registered automatically')
        return redirect('register-course')
    
    comp_subjects = ['Mathematics','English Language','Civic Education','Igbo Language','Biology']
    if not RegisteredSubjects.objects.filter(student=student.registration_number,session=session.session).exists():
        for i in comp_subjects:
            RegisteredSubjects.objects.create(
                student=student.registration_number,subject=i,group=student.group,arm=student.arm,category='senior',
                added_by=request.user,lock=True,last_name=student.last_name,first_name=student.first_name,session=session.session
            )
    courses = AllSubject.objects.filter(category='senior').order_by('subject')
    registered = RegisteredSubjects.objects.filter(student=student.registration_number)
    if request.method == 'POST':
        if len(registered) < 9 and len(registered) > 10:
            messages.error(request, 'Student subjects must be either 9 or 10')
            return redirect('register-course', ref)
        
        registered.update(lock=True)
        student.register_course = True
        student.save()
        messages.success(request,'Registration successful')
        return redirect('register-course', student.ref)

    context = {
        'student':student,
        'courses':courses,
        'registered':registered
    }
    return render(request, 'student/registercourse.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','class-teacher','controller'])
def addCourses(request, sub, ref):
    session = Session.objects.get(active=1)
    term = Term.objects.get(active=1)
    subject = AllSubject.objects.get(ref=sub)
    student = Student.objects.get(ref=ref)
    registered = len(RegisteredSubjects.objects.filter(student=student.registration_number))
    # Check for number of subjects added
    if registered >= 10:
        messages.error(request, 'Student have reach the maximum limit')
        return redirect('register-course', student.ref)
    
    # Check for existing subjects
    if RegisteredSubjects.objects.filter(student=student.registration_number,subject=subject.subject,session=session.session).exists():
        messages.error(request, 'Subject already exist')
        return redirect('register-course', student.ref)
    course = RegisteredSubjects.objects.create(
        student=student.registration_number,subject=subject.subject,group=student.group,arm=student.arm,category='senior',
        added_by=request.user,last_name=student.last_name,first_name=student.first_name,session=session.session
    )
    messages.success(request, 'Added')
    return redirect('register-course', student.ref)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','class-teacher','controller'])
def removeCourses(request,ref):
    student_course = RegisteredSubjects.objects.get(ref=ref)
    student = Student.objects.get(registration_number=student_course.student)
    course = RegisteredSubjects.objects.filter(ref=ref)
    course.delete()
    messages.success(request, 'Removed')
    return redirect('register-course', student.ref)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','class-teacher','controller'])
def unlockCourseRegister(request):
    if request.method == 'POST':
        reg = request.POST.get('reg')
        try:
            student = Student.objects.get(registration_number=reg)
        except Student.DoesNotExist:
            messages.error(request, 'Student not found')
            return redirect('get-student-register-course')
        if student.graduated:
            messages.error(request, 'Student already already graduated')
            return redirect('get-student-register-course')
        registered = RegisteredSubjects.objects.filter(student=student.registration_number)
        registered.update(lock=False)
        student.register_course = False
        student.save()
        messages.success(request,'Unlock')
        return redirect('register-course', student.ref)
    return render(request, 'student/unlockcourseregister.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin', 'controller'])
def fix20242025FirstTermResult(request):
    allGroup = AllClass.objects.all()
    data = request.GET.get('group')
    students = []
    student_data = []
    result_container = []

    try:
        session = Session.objects.get(active=True)
        term = Term.objects.get(active=True)
    except Session.DoesNotExist:
        messages.error(request, 'No active session found.')
        return redirect('fix-2024-result')
    except Term.DoesNotExist:
        messages.error(request, 'No active term found.')
        return redirect('fix-2024-result')

    if data:
        try:
            output = AllClass.objects.get(ref=data)
        except AllClass.DoesNotExist:
            messages.error(request, 'Such class does not exist')
            return redirect('fix-2024-result')

        # Fetch all students in the selected class
        students = Student.objects.filter(active=1, group=output.group, arm=output.arm).order_by('last_name')

        # Fetch results for students in the selected class, session, and term
        results = Result.objects.filter(
            arm=output.arm, group=output.group, session=session.session, term=term.term
        )

        # Create a list of dictionaries with student details and their results
        result_dict = {result.student: result for result in results}
        for student in students:
            result = result_dict.get(student.registration_number)
            student_data.append({
                "student": student,
                "total_score": getattr(result, "total", None),
                "average_score": getattr(result, "average", None),
                "remark": getattr(result, "remark", None),
                "position": getattr(result, "position", None),
                "teacher_comment":getattr(result, "teachercomment", None),
                "principal_comment":getattr(result, "principalcomment", None),
            })

    # Debugging: Print data to console
    print("Student Data:", student_data)

    if 'fix' in request.POST:
        group = AllClass.objects.get(ref=data)
        for result in results:
            pos = []

            pos.append(result.student)

            subjects = RegisteredSubjects.objects.filter(student=result.student)

            # Calculate for average score
            average = round(result.total/len(subjects), 2)
            pos.append(average)

            # Set student remark
            remark = ''
            if(average >= group.promotion_score):
                remark = 'PASS'
            else:
                remark = 'FAIL'

            result.average = average
            result.remark = remark

            result.save()

            result_container.append(pos)

        # print result container
        print(result_container)

        # Sort by the Decimal value at index 1 in descending order
        sorted_data = sorted(result_container, key=lambda x: x[1], reverse=True)

        # Function to get the suffix for positions
        def get_suffix(position):
            if 10 <= position % 100 <= 20:  # Special case for 11th, 12th, 13th, etc.
                return 'th'
            else:
                suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
                return suffixes.get(position % 10, 'th')

        # Assign positions, handling ties in scores
        position = 1
        last_score = None
        for index, (student_id, score) in enumerate(sorted_data):
            if score != last_score:
                last_score = score
                position = index + 1  # New position if score changes
            suffix = get_suffix(position)
            print(f"Position: {position}{suffix}, Student ID: {student_id}, Score: {score}")

            Result.objects.filter(student=student_id,session=session.session,term=term.term).update(
                position=f'{position}{suffix}',
            )

        messages.success(request, 'Successful')
        return redirect('fix-2024-result')
    
    elif 'comment' in request.POST:
        p1 = request.POST.get('p1')
        p2 = request.POST.get('p2')
        p3 = request.POST.get('p3')
        p4 = request.POST.get('p4')

        t1 = request.POST.get('t1')
        t2 = request.POST.get('t2')
        t3 = request.POST.get('t3')
        t4 = request.POST.get('t4')

        for r in results:
            if(r.average >= 70):
                r.teachercomment = t1
                r.principalcomment = p1
            elif(r.average >= 55 and r.average < 70):
                r.teachercomment = t2
                r.principalcomment = p2
            elif(r.average >= 40 and r.average < 55):
                r.teachercomment = t3
                r.principalcomment = p3
            else:
                r.teachercomment = t4
                r.principalcomment = p4

            r.save()

        messages.success(request, 'Successful')
        return redirect('fix-2024-result')

    context = {
        'allgroup': allGroup,
        'data': output if data else None,
        'student_data': student_data,
    }
    return render(request, 'student/fix_2024_result.html', context)
