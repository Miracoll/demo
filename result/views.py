from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from lms.decorators import allowed_users
from lms.models import Profile
from configuration.models import AllClass, Subject, Config, Term, Session,RegisteredSubjects,AllSubject, Class,Arm
from result.utils import render_to_pdf
from student.models import Student
from academic.models import Record
from result.models import Result
from result.models import Result, Comment
from result.functions import gradeGetter,stat
from attendance.models import Attendance
from django.http import HttpResponse
import csv
from django.contrib import messages
from django.template.loader import get_template
from xhtml2pdf import pisa
import qrcode
from django.conf import settings
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import landscape, A4,A0,A1,A2,portrait
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer,Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Create your views here.

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','class-teacher','controller'])
def resulttemplate(request):
    user = request.user
    if (user.profile.role.keyword == 'subject-teacher'):
        allgroup = AllClass.objects.filter(teacher = request.user)
        subject = Subject.objects.filter(teacher = request.user)
    elif (user.profile.role.keyword == 'admin' or user.profile.role.keyword == 'controller'):
        allgroup = AllClass.objects.all().order_by('group','arm')
        subject = Subject.objects.all().order_by('group','arm','subject')
    session = Session.objects.get(active=1)
    term = Term.objects.get(active=1).term
    # Download subject result
    if 'submit' in request.POST:
        msub = request.POST.get('subject')
        msublist = msub.split(', ')
        getgroup = msublist[1]
        getarm = msublist[2]
        subject = msublist[0]

        studentand = RegisteredSubjects.objects.filter(group = getgroup, arm=getarm, subject=subject, active=1, lock=1)
        student = studentand.values_list('last_name','first_name','student','group','arm')
        # print(student)

        # nondata = ['','','','','=sum(d2:g2)','=AVERAGE(D2:G2)','=IF(I2>=70,"A",IF(I2>=55,"C",IF(I2>=40,"P","F")))','=IF(I2>=70,"Excellent",IF(I2>=55,"Good",IF(I2>=40,"Pass","Fail")))','=RANK(I2,$I$2:$I$50)']
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Registration Number','Class','Arm','Subject','CA1','CA2','Exam','Total','Grade','Remark','Position','Status'])
        if len(student) == 0:
            messages.error(request,'No record found')
            return redirect('result_template')
        else:
            for student in student:
                stud = list(student)
                try:
                    ca1 = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).CA1
                    ca2 = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).CA2
                    # ca3 = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).CA3
                    # project = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).project
                    # test = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).test
                    exam = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).exam
                    total = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).total
                    grade = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).grade
                    remark = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).remark
                    position = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).position
                    status1 = Record.objects.get(student=stud[2],session=session.session,subject=subject,group=getgroup,arm=getarm,term=term).active
                except Record.DoesNotExist:
                    continue
                if status1 == 1:
                    status = 'Published'
                else:
                    status = 'Not yet published'
                stud.extend([subject,ca1,ca2,exam,total,grade,remark,position,status])
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{getgroup}{getarm} record.csv"'
            return response
    # Download class result
    if 'submit1' in request.POST:
        group = request.POST.get('group')
        groupsplit = group.split(',')
        getgroup = groupsplit[0]
        getarm = groupsplit[1]
        # subject = request.POST.get('subject1')

        studentand = Student.objects.filter(group = getgroup, arm=getarm, active = 1).order_by('last_name')
        student = studentand.values_list('last_name','first_name','registration_number')
        # print(student)
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Registration Number','Total','Average','Position','Status'])
        if len(student) == 0:
            messages.warning(request,'No record found')
            return redirect('result_template')
        else:
            for student in student:
                stud = list(student)
                try:
                    total1 = Result.objects.get(student=stud[2],session=session.session,group=getgroup,arm=getarm,term=term,active=1).total
                    average1 = Result.objects.get(student=stud[2],session=session.session,group=getgroup,arm=getarm,term=term,active=1).average
                    position1 = Result.objects.get(student=stud[2],session=session.session,group=getgroup,arm=getarm,term=term,active=1).position
                    status1 = Result.objects.get(student=stud[2],session=session.session,group=getgroup,arm=getarm,term=term,active=1).active
                except Result.DoesNotExist:
                    continue
                if status1 == 1:
                    status = 'Active'
                else:
                    status = 'Inactive'
                stud.extend([total1,average1,position1,status])
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{getgroup}{getarm} result.csv"'
            return response
    
    context = {'group':allgroup,'subject':subject}
    return render(request, 'result/resultmanage.html', context)

def termresult(request):
    return render(request, 'result/termresult.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','class-teacher'])
def personality(request):
    user = request.user
    getgroup = user.first_name
    getarm = user.last_name
    session = Session.objects.get(active=1)
    term = Term.objects.get(active=1)
    if 'submit' in request.POST:


        studentand = Student.objects.filter(group = getgroup, arm=getarm, active = 1).order_by('last_name')
        student = studentand.values_list('last_name','first_name','registration_number','group','arm')
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        writer.writerow(['Last Name', 'First Name', 'Registration Number','Class','Arm','Attentiveness','Politeness','Neatness','Moral concepts','Punctuality','Social attitudes','Hand Writing','Speech Fluency','Lab & Workshop Skill','Sport & Games','Communication','Critical Thinking','Number of Days Present','Total Days'])
        if len(student) == 0:
            messages.error(request,'No record found')
            return redirect('personality')
        for student in student:
            stud = list(student)
            writer.writerow(stud)
        response['Content-Disposition'] = f'attachment; filename="{getgroup}{getarm} personality.csv"'
        return response
    
    elif 'csvupload' in request.POST:
        csv_file = request.FILES["file"]
        if not csv_file.name.endswith('.csv'):
            messages.warning(request,'File is not CSV type')
            return redirect('personality')
        file = csv_file.read().decode('utf-8')
        csv_data = csv.reader(io.StringIO(file), delimiter=',')
        next(csv_data)
        for line in csv_data:
            person = line[2]
            group = line[3]
            arm = line[4]
            atten = line[5]
            polite = line[6]
            neat = line[7]
            moral = line[8]
            punctual = line[9]
            social = line[10]
            writing = line[11]
            speech = line[12]
            lab = line[13]
            sport = line[14]
            communication = line[15]
            critical = line[16]
            present_days = int(line[17])
            total_days = int(line[18])

            main_group = AllClass.objects.get(group=getgroup, arm=getarm)
            if main_group.approve_result == 0:
                messages.error(request, 'Result not yet ready for personality upload')
                return redirect('personality')
            Result.objects.filter(group=getgroup,arm=getarm,session=session.session,term=term.term,student=person).update(
                attentiveness=atten, politeness=polite, neatness=neat, moral_concepts=moral,punctuality=punctual,
                social_attitudes=social, hand_writing=writing, speech_fluency=speech, lab=lab,present=present_days,
                sport=sport, communication=communication,thinking=critical,absent=total_days-present_days
            )
            if term.term == 3:
                Result.objects.filter(group=getgroup,arm=getarm,session=session.session,term=4,student=person).update(
                attentiveness=atten, politeness=polite, neatness=neat, moral_concepts=moral,punctuality=punctual,
                social_attitudes=social, hand_writing=writing, speech_fluency=speech, lab=lab,present=present_days,
                sport=sport, communication=communication,thinking=critical,absent=total_days-present_days
            )
        messages.success(request, 'Done')
        return redirect('personality')
    context = {}
    return render(request, 'result/personality.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','class-teacher'])
def resultDatasheet(request):
    allgroup = AllClass.objects.filter(teacher = request.user)
    subject = Subject.objects.filter(teacher = request.user)
    session = Session.objects.all()
    term = Term.objects.all()
    if 'submit' in request.POST:

        msub = request.POST.get('subject')
        msublist = msub.split(', ')
        getgroup = msublist[1]
        getarm = msublist[2]
        getsubject = msublist[0]
        getsession = request.POST.get('session')
        getterm = request.POST.get('term')

        records = Record.objects.filter(subject=getsubject, group=getgroup, arm=getarm, session=getsession, term=getterm)

        if not records.exists():
            messages.error(request, 'No data found')
            return redirect('result_datasheet')

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="table_example.pdf"'

        # Create a PDF document
        pdf_doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []

        short_text = "This is a short text above the table. You can customize this text."
        short_text_style = ParagraphStyle(
            'short_text_style',
            parent=getSampleStyleSheet()['Normal'],
            fontName='Helvetica-Bold',
            fontSize=12,
            spaceAfter=10,
        )
        short_text_paragraph = Paragraph(short_text, short_text_style)
        elements.append(short_text_paragraph)

        lines = [
            ['S/N','REG NUMBER','LAST NAME','FIRST NAME','OTHER NAME','GENDER','CA1','CA2','EXAM','TOTAL']
        ]
        counter = 1

        for record in records:
            student = Student.objects.get(registration_number=record.student)
            lines.append([str(counter),record.student,student.last_name,student.first_name,student.other_name,student.sex,str(round(record.CA1,1)),str(round(record.CA2,1)),str(record.exam),str(record.total)])
            counter+=1

        # Create the table and style
        table = Table(lines)
        style = TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]
        )

        table.setStyle(style)

        # Add the table to the PDF document
        elements.append(table)

        # Build the PDF document
        pdf_doc.build(elements)

        return response

    context = {
        'group':allgroup,
        'subject':subject,
        'session':session,
        'term':term,
    }
    return render(request, 'result/datasheet.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','class-teacher','controller'])
def broadsheet(request):
    all_class = AllClass.objects.all()
    # print(request.user.profile.role.keyword, request.user.first_name, request.user.last_name)
    if (request.user.profile.role.keyword == 'class-teacher'):
        all_class = AllClass.objects.get(group=request.user.first_name, arm=request.user.last_name)
    session = Session.objects.all()
    if request.method == 'POST':
        get_group = request.POST.get('ref')
        get_session = request.POST.get('session')
        ses = Session.objects.get(ref=get_session)
        user = request.user
        if user.profile.role.keyword == 'class-teacher':
            group = AllClass.objects.get(teacher = request.user)
        elif user.profile.role.keyword == 'admin' or user.profile.role.keyword =='controller':
            try:
                group = AllClass.objects.get(ref=get_group)
            except AllClass.DoesNotExist:
                user.is_active = False
                user.save()
                Profile.objects.filter(user=user).update(blocked_reason='From result broadsheet')
                messages.error(request, 'Self destruction activated')
                return redirect('logout')
        config = Config.objects.get(id=1)
        students = Student.objects.filter(group=group.group, arm=group.arm, active=1).order_by('last_name')
        class_subjects = Subject.objects.filter(group=group.group,arm=group.arm).values_list('subject')
        header = ['S/N','Reg Number','Last Name','First Name','Sex']
        subject = []
        class_stat = stat(group, ses)
        if class_stat is None:
            messages.error(request, 'No result to display')
            return redirect('broadsheet')
        for i in class_subjects:
            tuple_2_list = list(i)
            subject.append(tuple_2_list[0])
            header.append(tuple_2_list[0])
        header_summary = ['Total','Average',"F's","P's","C's","A's",'Remark','Position']
        header.extend(header_summary)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{group.group}{group.arm} broadsheet.pdf"'
        if group.category == 'senior':
            pdf_document = SimpleDocTemplate(response, pagesize=landscape(A0),rightMargin=5,leftMargin=5,topMargin=5,bottomMargin=5)
        else:
            pdf_document = SimpleDocTemplate(response, pagesize=landscape(A1),rightMargin=5,leftMargin=5,topMargin=5,bottomMargin=5)

        data1 = [
            [f'{config.school_name}'],
            [f'{group.group}{group.arm} BROADSHEET'],
            ['Teacher Name_____________________________Sign:__________'],
            ['Session:____________________________________'],
        ]

        data2 = [
            header,
            ['','','','','','1ST|2ND|3RD|TOTAL|AVG','1ST|2ND|3RD|TOTAL|AVG','1ST|2ND|3RD|TOTAL|AVG','1ST|2ND|3RD|TOTAL|AVG','1ST|2ND|3RD|TOTAL|AVG','1ST|2ND|3RD|TOTAL|AVG','1ST|2ND|3RD|TOTAL|AVG','1ST|2ND|3RD|TOTAL|AVG','1ST|2ND|3RD|TOTAL|AVG','1ST|2ND|3RD|TOTAL|AVG','1ST|2ND|3RD|TOTAL|AVG'],
        ]

        counter = 1
        students = Student.objects.filter(group=group.group, arm=group.arm, active=1).order_by('last_name')
        for student in students:
            student_personal_data = [str(counter),student.registration_number, student.last_name.upper(), student.first_name.upper(),student.sex.upper()[0]]
            for sub in range(len(subject)):
                try:
                    record = Record.objects.get(student=student.registration_number,term=4,subject=subject[sub],session=ses.session)
                    ca1 = record.CA1
                    ca2 = record.CA2
                    ca3 = record.CA3
                    total = record.total
                    average = record.annaul_average
                except Record.DoesNotExist:
                    ca1 = '-'
                    ca2 = '-'
                    ca3 = '-'
                    total = '-'
                    average = '-'
                record_collect = f'{ca1}|{ca2}|{ca3}|{total}|{average}'
                student_personal_data.append(record_collect)
            try:
                result = Result.objects.get(student=student.registration_number,term=4,session=ses.session)
                r_total = result.total
                r_average = result.average
                r_position = result.position
                if r_average>=40:
                    remark='PASSED'
                else:
                    remark='FAILED'
                grade = gradeGetter(student.registration_number)
            except Result.DoesNotExist:
                pass
                r_total = '-'
                r_average = '-'
                r_position = '-'
                remark = '-'
                grade = ['-','-','-','-']
            result_collect = [r_total,r_average,grade[3],grade[2],grade[1],grade[0],remark,r_position]
            student_personal_data.extend(result_collect)

            data2.append(student_personal_data)
            counter+=1

        data3 = [
            [f'{group.group}{group.arm} RESULT SUMMARY',''],
            ['NUMBER OF STUDENTS',f'{group.number_of_student}'],
            ['NUMBER OF PASSED STUDENTS',f'{class_stat[0]}'],
            ['NUMBER OF FAILED STUDENTS',f'{class_stat[2]}'],
            ['PERCENTAGE OF PASSED STUDENTS',f'{class_stat[1]}%'],
            ['PERCENTAGE OF FAILED STUDENTS',f'{class_stat[3]}%'],
            ['CLASS AVERAGE',f'{class_stat[4]}'],
            ['CLASS TEACHER','_________________________'],
            ['PRINCIPAL\'S NAME','_____________________'],
            ['DATE AND STAMP','________________________'],
        ]

        # Create tables
        table1 = Table(data1)
        table2 = Table(data2)
        table3 = Table(data3)
        
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
                ('BACKGROUND', (0, 0), (-1, 1), colors.grey),
                ('BACKGROUND', (0, 1), (4, 1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, 1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]
        )

        style3 = TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                # ('BACKGROUND', (0, 1), (4, 1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]
        )

        table1.setStyle(style)
        table2.setStyle(style2)
        table3.setStyle(style3)

        # Build the PDF document
        pdf_content = [table1, Spacer(1, 30), table2, Spacer(1, 30), table3]
        pdf_document.build(pdf_content)

        return response
    context = {
        'group':all_class,
        'session': session
    }
    return render(request, 'result/broadsheet.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','subject-teacher','class-teacher'])
def displayresult(request,pk):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year
    school = Config.objects.get(id=1).school_name
    
    reg = Student.objects.get(id=pk).registration_number
    
    avgagg = 0
    
    if term == 3:
        avg = Result.objects.get(student=reg, term=3).average
        avgavg = Result.objects.get(student=reg, term=4).average
    else:
        avg = Result.objects.get(student=reg, term=term).average

    if avg >= 70:
        avgagg = 70
    elif avg >= 55:
        avgagg = 55
    elif avg >= 40:
        avgagg = 40
    else:
        avgagg = 39
    comment = Comment.objects.filter(score = avgagg)
    student = Student.objects.filter(registration_number=reg)
    record = Record.objects.filter(student = reg, term=term)
    result = Result.objects.filter(student = reg, term=term)
    context = {
        'student':student,
        'record':record,
        'result':result,
        'average':avg,
        # 'averageavg':avgavg,
        'comment':comment,
    }

    return render(request, 'result/resultdisplay.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','guildance-and-cousellor','subject-teacher','class-teacher'])
def displayresultpdf(request,pk):
    term = Term.objects.get(active=1).term
    reg = Student.objects.get(id=pk).registration_number
    avgagg = 0
    if term == 3:
        avg = Result.objects.get(student=reg, term=3).average
        avgavg = Result.objects.get(student=reg, term=4).average
    else:
        avg = Result.objects.get(student=reg, term=term).average
    if avg >= 70:
        avgagg = 70
    elif avg >= 55:
        avgagg = 55
    elif avg >= 40:
        avgagg = 40
    else:
        avgagg = 39

    comment = Comment.objects.filter(score = avgagg)
    student = Student.objects.filter(registration_number=reg)
    record = Record.objects.filter(student = reg, term=term)
    result = Result.objects.filter(student = reg, term=term)

    template_path = 'result/resultdisplay_pdf.html'
    context = {
        'student':student,
        'record':record,
        'result':result,
        'average':avg,
        # 'averageavg':avgavg,
        'comment':comment,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="result.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','hostel-manager','guildance-and-cousellor','class-teacher'])
def resultcomment(request):
    # Execute if result status is competed by the class teacher
    term = Term.objects.get(active=1)
    session = Session.objects.get(active=1)
    print(request.user.profile.role)
    if 'submit' in request.POST:
        comment70 = request.POST.get('comment70')
        comment55 = request.POST.get('comment55')
        comment40 = request.POST.get('comment40')
        comment39 = request.POST.get('comment39')
        
        if request.user.profile.role.keyword == 'class-teacher':
            records = Result.objects.filter(group=request.user.first_name,arm=request.user.last_name,term=term.term, session=session.session)
            for record in records:
                if record.average >= 70:
                    record.teachercomment = comment70
                elif record.average >= 55 and record.average < 70:
                    record.teachercomment = comment55
                elif record.average >= 40 and record.average < 55:
                    record.teachercomment = comment40
                elif record.average <= 40:
                    record.teachercomment = comment39
                record.save()
        elif request.user.profile.role.keyword == 'principal':
            records = Result.objects.filter(term=term.term, session=session.session)
            for record in records:
                print(record)
                if record.average >= 70:
                    record.principalcomment = comment70
                elif record.average >= 55 and record.average < 70:
                    record.principalcomment = comment55
                elif record.average >= 40 and record.average < 55:
                    record.principalcomment = comment40
                elif record.average <= 40:
                    record.principalcomment = comment39
                record.save()
        elif request.user.profile.role.keyword == 'guidance-and-counsellor':
            records = Result.objects.filter(term=term.term, session=session.session)
            for record in records:
                print(record)
                if record.average >= 70:
                    record.gccomment = comment70
                elif record.average >= 55 and record.average < 70:
                    record.gccomment = comment55
                elif record.average >= 40 and record.average < 55:
                    record.gccomment = comment40
                elif record.average <= 40:
                    record.gccomment = comment39
                record.save()
        elif request.user.profile.role.keyword == 'hostel-manager':
            records = Result.objects.filter(term=term.term, session=session.session)
            for record in records:
                print(record)
                if record.average >= 70:
                    record.hostelcomment = comment70
                elif record.average >= 55 and record.average < 70:
                    record.hostelcomment = comment55
                elif record.average >= 40 and record.average < 55:
                    record.hostelcomment = comment40
                elif record.average <= 40:
                    record.hostelcomment = comment39
                record.save()

        if term.term == 3:
            if request.user.profile.role.keyword == 'class-teacher':
                records = Result.objects.filter(group=request.user.first_name,arm=request.user.last_name,term=4,session=session.session)
                for record in records:
                    if record.average >= 70:
                        record.teachercomment = comment70
                    elif record.average >= 55 and record.average < 70:
                        record.teachercomment = comment55
                    elif record.average >= 40 and record.average < 55:
                        record.teachercomment = comment40
                    elif record.average <= 40:
                        record.teachercomment = comment39
                    record.save()
            elif request.user.profile.role.keyword == 'principal':
                records = Result.objects.filter(term=4,session=session.session)
                for record in records:
                    print(record)
                    if record.average >= 70:
                        record.principalcomment = comment70
                    elif record.average >= 55 and record.average < 70:
                        record.principalcomment = comment55
                    elif record.average >= 40 and record.average < 55:
                        record.principalcomment = comment40
                    elif record.average <= 40:
                        record.principalcomment = comment39
                    record.save()
            elif request.user.profile.role.keyword == 'guidance-and-counsellor':
                records = Result.objects.filter(term=4,session=session.session)
                for record in records:
                    print(record)
                    if record.average >= 70:
                        record.gccomment = comment70
                    elif record.average >= 55 and record.average < 70:
                        record.gccomment = comment55
                    elif record.average >= 40 and record.average < 55:
                        record.gccomment = comment40
                    elif record.average <= 40:
                        record.gccomment = comment39
                    record.save()
            elif request.user.profile.role.keyword == 'hostel-manager':
                records = Result.objects.filter(term=4,session=session.session)
                for record in records:
                    print(record)
                    if record.average >= 70:
                        record.hostelcomment = comment70
                    elif record.average >= 55 and record.average < 70:
                        record.hostelcomment = comment55
                    elif record.average >= 40 and record.average < 55:
                        record.hostelcomment = comment40
                    elif record.average <= 40:
                        record.hostelcomment = comment39
                    record.save()

        messages.success(request, 'Done')
        return redirect('result_comment')

    if 'submit1' in request.POST:
        reg = request.POST.get('reg')
        comment = request.POST.get('comment')
        # print(request.user.profile.role)
        if request.user.profile.role.keyword == 'principal':
            Result.objects.filter(student = reg,term=term.term,session=session.session).update(principalcomment = comment)
        if request.user.profile.role.keyword == 'guildance-and-cousellor':
            Result.objects.filter(student = reg,term=term.term,session=session.session).update(gccomment = comment)
        if request.user.profile.role.keyword == 'hostel-manager':
            Result.objects.filter(student = reg,term=term.term,session=session.session).update(hostelcomment = comment)
        if request.user.profile.role.keyword == 'class-teacher':
            Result.objects.filter(student = reg,term=term.term,session=session.session).update(teachercomment = comment)
            
        messages.success(request, 'Done')
        return redirect('result_comment')
    return render(request, 'result/resultcomment.html')

# show and approve subject result
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','controller'])
def approveresult(request):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year
    if (request.user.profile.role.keyword == 'subject-teacher'):
        unitsubject = Subject.objects.filter(teacher=request.user)
    elif (request.user.profile.role.keyword == 'admin' or request.user.profile.role.keyword == 'controller'):
        unitsubject = Subject.objects.all().order_by('group','arm','subject')
    allgroup = AllClass.objects.filter(active = 1)
    context = {
        'allgroup':allgroup,
        'unitsubject':unitsubject,
    }
    return render(request, 'result/resultapprove.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['class-teacher'])
def resultstatus(request):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year
    unitsubject = Subject.objects.filter(
        group = request.user.first_name, arm=request.user.last_name
    )
    group = AllClass.objects.get(group=request.user.first_name, arm=request.user.last_name)
    if request.method == 'POST':
        if group.approve_result == 0:
            messages.error(request, 'Approve result before publishing')
            return redirect('result_status')
        Result.objects.filter(group=request.user.first_name,arm=request.user.last_name,term=term,session=session,year=year).update(approve=1,active=1)
        Record.objects.filter(group=request.user.first_name,arm=request.user.last_name,term=term,session=session,year=year).update(active=1)
        if term == 3:
            Result.objects.filter(group=request.user.first_name,arm=request.user.last_name,term=4,session=session,year=year).update(approve=1,active=1)
            Record.objects.filter(group=request.user.first_name,arm=request.user.last_name,term=4,session=session,year=year).update(active=1)
        messages.success(request, 'Published, student can start checking result')
        return redirect('result_status')
    context = {
        'unitsubject':unitsubject,
        'group':group
    }
    return render(request, 'result/resultstatus.html', context)

def approveclassresult(request):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year
    group = request.user.first_name
    arm = request.user.last_name
    if Subject.objects.filter(group=group,arm=arm,approve_result=0).exists():
        messages.error(request,'All subjects must be approve by subject teacher')
        return redirect('result_status')
    # Generate qr code for result
    students = Result.objects.filter(group=group,arm=arm,term=term,session=session,year=year)
    if term == 3:
        annual_students = Result.objects.filter(group=group,arm=arm,term=4,session=session,year=year)
        for student in annual_students:
            data = student.ref
            img = qrcode.make(data)
            img_name = str(student.ref) + '.png'
            img.save(settings.MEDIA_ROOT + '/qrcode/' + img_name)
            student.qrcode = 'qrcode/'+img_name
            
            student.save()

    for student in students:

        data = student.ref
        img = qrcode.make(data)
        img_name = str(student.ref) + '.png'
        img.save(settings.MEDIA_ROOT + '/qrcode/' + img_name)
        student.qrcode = 'qrcode/'+img_name
        
        student.save()

    AllClass.objects.filter(group=group,arm=arm).update(lock=1,approve_result=1)
    messages.success(request, 'proceed with personality and comment upload')
    return redirect('result_status')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher','controller'])
def approveresultclick(request,pk):
    Subject.objects.filter(ref=pk).update(approve_result = 1)
    messages.success(request,'Done')
    return redirect('result_approve')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def resultcomputation(request):
    group = AllClass.objects.all()
    subject = Subject.objects.all()
    session = Session.objects.get(active=True)
    
    if 'start' in request.POST:
        psw1 = request.POST.get('psw1')
        user = request.user
        if not user.check_password(psw1):
            messages.error(request, 'Invalid entry')
            return redirect('result_compute')
        Config.objects.filter(id=1).update(start_result=1,entry=0)
        # TODO:Send mail to all staff

        # Register courses for junior category
        junior_student = Student.objects.filter(category='junior',active=1)
        junior_subject = AllSubject.objects.filter(category='junior',active=1)
        for js in junior_student:
            for sub in junior_subject:
                if RegisteredSubjects.objects.filter(student=js.registration_number, subject=sub.subject).exists():
                    continue
                RegisteredSubjects.objects.create(
                    student=js.registration_number,subject=sub.subject,group=js.group,arm=js.arm,category='junior',
                    added_by=request.user,last_name=js.last_name,first_name=js.first_name,lock=1,session=session.session
                )

        # Get total students
        for i in group:
            print(i)
            nos = len(Student.objects.filter(group=i.group,arm=i.arm,active=1))
            class_subject = len(Subject.objects.filter(group=i.group,arm=i.arm))
            if i.category == 'junior':
                AllClass.objects.filter(group=i.group, arm=i.arm).update(number_of_student=nos,number_of_subjects=class_subject)
            elif i.category == 'senior':
                AllClass.objects.filter(group=i.group, arm=i.arm).update(number_of_student=nos,number_of_subjects=10)
        for i in subject:
            nos = len(RegisteredSubjects.objects.filter(group=i.group,arm=i.arm,subject=i.subject))
            Subject.objects.filter(group=i.group, arm=i.arm,subject=i.subject).update(total_student=nos)

        return redirect('result_compute')
    elif 'stop' in request.POST:
        psw2 = request.POST.get('psw2')
        user = request.user
        if not user.check_password(psw2):
            messages.error(request, 'Invalid entry')
            return redirect('result_compute')
        # Stop result computation
        Config.objects.filter(id=1).update(start_result=0)
        # Reset class data
        for i in group.values():
            nos = len(Student.objects.filter(group=i.get('group'),arm=i.get('arm'),active=1))
            AllClass.objects.filter(group=i.get('group'), arm=i.get('arm')).update(
                lock=0,approve_result=0,number_of_subjects=None
            )
        # Reset subject
        for i in subject.values():
            nos = len(Student.objects.filter(group=i.get('group'),arm=i.get('arm'),active=1))
            Subject.objects.filter(group=i.get('group'), arm=i.get('arm')).update(
                upload=0,lock=0,approve_result=0
            )
        return redirect('result_compute')
    context = {}
    return render(request, 'result/resultcomputation.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def getupload(request):
    if 'submit' in request.POST:
        reg = request.POST.get('reg_num')
        staff = Subject.objects.filter(teacher=reg)
        if staff.exists():
            return redirect('manage_upload',reg)
        else:
            messages.error(request,"Sorry, i can't find your request")
            return redirect('get_upload')
    return render(request, 'result/getupload.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def manageupload(request,pk):
    staff = Subject.objects.filter(teacher=pk)
    context = {'staff':staff}
    return render(request,'result/unlockupload.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def unlockresultupload(request,pk):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year
    Subject.objects.filter(id=pk).update(lock = 0,upload = 0)
    getstaff = Subject.objects.get(id=pk).teacher
    group = Subject.objects.get(id=pk).group
    arm = Subject.objects.get(id=pk).arm
    subject = Subject.objects.get(id=pk).subject
    AllClass.objects.filter(group=group,arm=arm).update(approve_result=0,lock=0)
    Record.objects.filter(group=group,subject=subject,arm=arm,term=term,session=session,year=year).delete()
    Result.objects.filter(group=group,arm=arm,term=term,session=session,year=year).delete()
    if term == 3:
        Record.objects.filter(group=group,subject=subject,arm=arm,term=4,session=session,year=year).delete()
        Result.objects.filter(group=group,arm=arm,term=4,session=session,year=year).delete()
    messages.success(request, 'Unlock successful')
    return redirect('manage_upload',getstaff)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','subject-teacher'])
def allocateSubject(request):
    user = request.user
    subject_teacher = Subject.objects.filter(teacher=user.username)
    all_subjects = AllSubject.objects.filter(active=1)
    groups = Class.objects.all()
    arms = Arm.objects.all()
    subjects = Subject.objects.all()
    
    if request.method == 'POST':
        group = request.POST.get('group')
        arm = request.POST.get('arm')
        subject = request.POST.get('subject')
        try:
            get_class = Subject.objects.get(group=group,arm=arm,subject=subject)
        except Subject.DoesNotExist:
            messages.error(request, 'Such class does not exit')
            return redirect('allocate')
        print(get_class.teacher)
        if get_class.teacher is None:
            Subject.objects.filter(group=group,arm=arm,subject=subject).update(teacher=user.username)
            messages.success(request, 'Successful')
            return redirect('allocate')
        else:
            messages.error(request, 'Class already taken')
            return redirect('allocate')
    context = {
        'teacher':subject_teacher,
        'groups':groups,
        'arms':arms,
        'subjects':subjects,
        'all_subjects':all_subjects,
    }
    return render(request, 'result/allocate.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','class-teacher','controller'])
def print_class_result(request):
    all_class = AllClass.objects.all()
    if (request.user.profile.role.keyword == 'class-teacher'):
        all_class = AllClass.objects.get(group=request.user.first_name, arm=request.user.last_name)
    sessions = Session.objects.all()
    terms = Term.objects.all()

    # if request.method == 'POST':
    #     selected_session = request.POST.get('session')
    #     selected_term = request.POST.get('term')
    #     selected_class = request.POST.get('class')

    #     session = Session.objects.get(ref=selected_session)
    #     term = Term.objects.get(ref=selected_term)
    #     group = AllClass.objects.get(ref=selected_class)
        
    #     result = Result.objects.filter(
    #         session=session.session,
    #         term=term.term,
    #         group=group.group,
    #         arm=group.arm
    #     )

    context = {
        'group': all_class,
        'sessions': sessions,
        'terms': terms,
    }
    return render(request, 'result/print_class_result.html', context)

def download_class_result_pdf(request):
    print('i am in')
    if request.method == 'POST':
        selected_session = request.POST.get('session')
        selected_term = request.POST.get('term')
        selected_class = request.POST.get('class')

        config = Config.objects.first()

        all_record = []

        session = Session.objects.get(ref=selected_session)
        term = Term.objects.get(ref=selected_term)
        group = AllClass.objects.get(ref=selected_class)

        # students = Student.objects.filter(group=group.group,arm=group.arm,active=1,graduated=False).order_by('last_name')
        results = Result.objects.filter(
            session=session.session,
            term=term.term,
            group=group.group,
            arm=group.arm,
        ).order_by('-average')

        for result in results:
            student = Student.objects.get(registration_number=result.student)
            each_student_record = {}

            # Personal record
            each_student_record['name'] = f"{student.last_name.upper()} {student.first_name.upper()} {(student.other_name or '').upper()}"
            each_student_record['gender'] = student.sex
            each_student_record['dob'] = student.dob
            each_student_record['passport'] = student.passport.url
            each_student_record['reg_no'] = student.registration_number

            # # Result record
            # result = Result.objects.filter(
            #     session=session.session,
            #     term=term.term,
            #     student=student.registration_number,
            # ).first()
            
            each_student_record['session'] = result.session
            each_student_record['term'] = result.term
            each_student_record['present'] = result.present
            each_student_record['absent'] = result.absent
            each_student_record['position'] = result.position
            each_student_record['total'] = result.total
            each_student_record['average'] = result.average
            each_student_record['class'] = f'{result.group}{result.arm}'
            each_student_record['remark'] = result.remark
            each_student_record['qrcode'] = result.qrcode.url if result.qrcode else None
            each_student_record['total_student'] = len(results)
            each_student_record['attendance'] = result.present+result.absent

            each_student_record['attentiveness'] = result.attentiveness
            each_student_record['politeness'] = result.politeness
            each_student_record['moral_concepts'] = result.moral_concepts
            each_student_record['punctuality'] = result.punctuality
            each_student_record['social_attitudes'] = result.social_attitudes
            each_student_record['neatness'] = result.neatness

            each_student_record['hand_writing'] = result.hand_writing
            each_student_record['speech_fluency'] = result.speech_fluency
            each_student_record['lab'] = result.lab
            each_student_record['sport'] = result.sport
            each_student_record['communication'] = result.communication
            each_student_record['thinking'] = result.thinking

            each_student_record['teachercomment'] = result.teachercomment
            each_student_record['principalcomment'] = result.principalcomment

            # Academic subject record
            records = Record.objects.filter(
                student=student.registration_number,
                session=session.session,
                term=term.term,
                active=1,
            ).order_by('subject')
            if records:
                subjects = []
                for record in records:
                    subject = {}
                    subject['subject'] = record.subject
                    subject['CA1'] = record.CA1
                    subject['CA2'] = record.CA2
                    subject['CA3'] = record.CA3
                    subject['exam'] = record.exam
                    subject['total'] = record.total
                    subject['average'] = record.average
                    subject['position'] = record.position
                    subject['grade'] = record.grade
                    subject['remark'] = record.remark
                    subject['total_subject'] = len(records)

                    subjects.append(subject)
                each_student_record['subjects'] = subjects
            
            all_record.append(each_student_record)

        print('all record',all_record)
            


        context = {
            'students': all_record,
            'config': config,
        }

        # pdf = render_to_pdf('result/result_pdf_template.html', context)
        # return pdf

    return render(request, 'result/result_pdf_template.html', context)