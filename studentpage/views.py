from django.shortcuts import redirect, render
from django.urls import reverse
from hostel.models import Hostel, Bedspace
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .decorators import allowed_users
from configuration.models import Config, Term, Class, Arm, Session,AllSubject,RegisteredSubjects,AllClass
from configuration.functions import telegramMessage
from attendance.models import Attendance
from card.models import Card
from lms.functions import registerSeniorStudentCourse, removeStudentCourse
from lms.models import Profile
from student.models import Student, Paid_Student
from hostel.models import Paid_Occupant
from result.models import Result, Comment
from .forms import StudentUpdateForm
from payment.models import Payment
from academic.models import Record
from news.models import News
from xhtml2pdf import pisa
import os
from secrets import token_hex
from parent.models import Parent
import qrcode

# Create your views here.

@login_required(login_url='signin')
# @allowed_users(allowed_roles=['student','parent'])
def studentdash(request):
    user = request.user
    if user.is_authenticated:
        if user.profile.role.keyword != 'student' and user.profile.role.keyword != 'parent':
            logout(request)
            return redirect('signin')
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active = 1)
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=request.user.username)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    student_user = User.objects.get(username=student.registration_number)
    present = len(Attendance.objects.filter(student=student_user,session=session.session,term=term,status=1))
    absent = len(Attendance.objects.filter(student=student_user,session=session.session,term=term,status=0))
    context = {
        'student':student,
        'session':session,
        'term':term,
        'present':present,
        'absent':absent,
    }
    return render(request, 'studentpage/student.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def result(request,pk):
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(id=pk)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    student_user = User.objects.get(username=student.registration_number)
    # reg = Student.objects.get(id=pk).registration_number
    avg = Result.objects.get(student=student.registration_number).average
    if avg >= 70:
        avgagg = 70
    elif avg >= 55:
        avgagg = 55
    elif avg >= 40:
        avgagg = 40
    else:
        avgagg = 39
    comment = Comment.objects.filter(score = avgagg)
    # student = Student.objects.filter(registration_number=student.registration_number)
    record = Record.objects.filter(student = student.registration_number)
    result = Result.objects.filter(student = student.registration_number)
    print(avg)
    context = {
        'student':student,
        'record':record,
        'result':result,
        'average':avg,
        'comment':comment,
    }
    return render(request,'studentpage/result.html',context)

def loginuser(request):
    sch_name = Config.objects.get(id=1).school_name
    if request.method == 'POST':
        username = request.POST.get('reg').upper()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'student does not exist')
            return redirect('signin')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            if user.profile.role.keyword == 'student' or user.profile.role.keyword == 'parent':
                return redirect('studentdash')
            else:
                return redirect('login')
        else:
            messages.error(request,'username/password is incorrect')
            return redirect('signin')
    context = {'name':sch_name}
    return render(request, 'studentpage/login.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def logoutuser(request):
    logout(request)
    return redirect('signin')

def forgetPassword(request):
    from datetime import datetime
    current_year = int(datetime.now().year)
    days = range(1,32)
    months = range(1,13)
    years = range(2000,current_year+1)
    if request.method == 'POST':
        reg = request.POST.get('reg').upper()
        day = request.POST.get('day')
        month = request.POST.get('month')
        year = request.POST.get('year')
        try:
            student = Student.objects.get(registration_number=reg)
            user = User.objects.get(username=student.registration_number)
        except Student.DoesNotExist:
            messages.error(request, 'Invalid registration number')
            return redirect('student_forget_password')
        
        if student.birth_day == day and student.birth_month == month and student.birth_year == year:
            user.set_password('student')
            user.save()
            Profile.objects.filter(user=user).update(set_password=False)
            telegramMessage(f'{student.last_name} {student.first_name} just reset his/her password.')
            messages.success(request, 'Successful')
            return redirect('signin')
        else:
            messages.error(request, 'Date of birth entered did not matched the one provided initially. Contact school administrator to reset the password')
            return redirect('student_forget_password')

    context = {
        'days':days,
        'months':months,
        'years':years
    }
    return render(request, 'studentpage/forget_password.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def checkresult(request):
    config = Config.objects.get(id=1)
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=user.username)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    all_session = Session.objects.all()
    all_group = AllClass.objects.filter(active=True)
    if request.method == 'POST':
        # getgroup = request.POST.get('group')
        # getarm = request.POST.get('arm')
        getterm = request.POST.get('term')
        getcardpin = request.POST.get('pin')
        getcardserial = request.POST.get('serial')
        get_group = request.POST.get('group')
        get_session = request.POST.get('session')

        try:
            group = AllClass.objects.get(ref=get_group)
        except AllClass.DoesNotExist:
            messages.error(request, 'Invalid class selection')
            return redirect('resultchecker')
        
        try:
            session = Session.objects.get(ref=get_session)
        except Session.DoesNotExist:
            messages.error(request, 'Invalid session selection')
            return redirect('resultchecker')
        
        getgroup = group.group
        getarm = group.arm

        # Check tuition fee for selected option
        print(getterm)
        if getterm != '4':
            if not Paid_Student.objects.filter(student=student.registration_number,term=getterm,group=getgroup,arm=getarm,status=1).exists():
                messages.error(request, 'No tuition payment found or invalid selection')
                return redirect('resultchecker')

        if Card.objects.filter(pin=getcardpin,serial=getcardserial).exists():
            usage = Card.objects.get(pin=getcardpin,serial=getcardserial).usage
            if usage == 0:
                Card.objects.filter(pin=getcardpin,serial=getcardserial).update(
                    student=student.registration_number,group=getgroup,arm=getarm,term=getterm,usage=1
                )
                try:
                    getrecordid = Result.objects.get(student=student.registration_number,term=getterm,group=getgroup,arm=getarm,active=1).ref
                except Result.DoesNotExist:
                        messages.error(request, 'No result found for your selection')
                        return redirect('resultchecker')
                if getterm == '4':
                    return redirect('show_annual_result', getrecordid,4,getgroup,getarm,session.ref)
                else:
                    return redirect('show_result', getrecordid,getterm,getgroup,getarm,session.ref)
            elif usage >= 1 and usage < config.card_usage:
                # Check student, class, arm and term
                card = Card.objects.get(pin=getcardpin,serial=getcardserial)

                if card.student==student.registration_number and card.group==getgroup and card.arm==getarm and card.term==getterm:
                    try:
                        getrecordid = Result.objects.get(student=card.student,term=card.term,group=card.group,arm=card.arm,session=session).ref
                    except Result.DoesNotExist:
                        messages.error(request, 'No result found for your selection')
                        return redirect('resultchecker')
                    Card.objects.filter(pin=getcardpin,serial=getcardserial).update(usage=usage+1)
                    if getterm == '4':
                        return redirect('show_annual_result', getrecordid,4,getgroup,getarm,session.ref)
                    else:
                        return redirect('show_result', getrecordid,getterm,getgroup,getarm,session.ref)
                        # return redirect(reverse('show_result', args=[getrecordid, getterm, getgroup, getarm, session]))
                else:
                    messages.error(request,'Invalid data')
                    return redirect('resultchecker')
            else:
                messages.error(request,'Maximum card usage')
                return redirect('resultchecker')
        else:
            messages.error(request,'Invalid data')
            return redirect('resultchecker')
    context = {'all_session':all_session, 'all_group':all_group}
    return render(request, 'studentpage/resultform.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def displayresult(request,pk,term):
    session = Session.objects.get(active = 1).session
    year = Session.objects.get(active = 1).year
    result = Result.objects.get(ref=pk)
    # reg = Result.objects.get(ref=pk).student
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=result.student)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    
    if term == 3:
        avg = Result.objects.get(student=student.registration_number, term=3).average
        # avgavg = Result.objects.get(student=reg, term=4).average
    else:
        avg = Result.objects.get(student=student.registration_number, term=term).average
    if avg >= 70:
        avgagg = 70
    elif avg >= 55:
        avgagg = 55
    elif avg >= 40:
        avgagg = 40
    else:
        avgagg = 39
    comment = Comment.objects.filter(score = avgagg)
    record = Record.objects.filter(student = student.registration_number, term=term,session=session, active=1)
    get_result = Result.objects.get(student = student.registration_number, term=term,session=session)
    context = {
        'student':student,
        'record':record,
        'result':get_result,
        'average':avg,
        'comment':comment,
    }
    return render(request, 'studentpage/resultdisplay.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def showResult(request,pk,term,getgroup,getarm,getsession):
    session = Session.objects.get(ref=getsession)
    # term = Term.objects.get(active=1)
    result = Result.objects.get(ref=pk)
    # reg = Result.objects.get(ref=pk).student
    group = AllClass.objects.get(group=getgroup,arm=getarm)
    # principal = 
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=result.student)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    check_record = Record.objects.filter(student = student.registration_number, term=term,group=getgroup,arm=getarm, active=0, session=session)
    check_result = Result.objects.filter(student=student.registration_number,term=term,group=getgroup,arm=getarm,active=0,session=session)
    # group = AllClass.objects.get(group=student.group,arm=student.arm)
    if check_record.exists() or check_result.exists():
        messages.error(request, 'Result not ready yet')
        return redirect('resultchecker')
    record = Record.objects.filter(student=student.registration_number,term=term,group=getgroup,arm=getarm,active=1,session=session).order_by('subject')
    get_result = Result.objects.get(student=student.registration_number,term=term,group=getgroup,arm=getarm,session=session)
    if(term == '1'):
        strterm = 'First'
    elif (term == '2'):
        strterm = 'Second'
    elif (term == '3'):
        strterm = 'Third'
    telegramMessage(f'Hello Miracle, {student.last_name} {student.first_name} with {student.registration_number} as registration number just checked {strterm} term result.\nPosition:{get_result.position}/{group.number_of_student} from {student.group}{student.arm} class')
    context = {
        'student':student,
        'record':record,
        'result':get_result,
        'session':session,
        'term':term,
        'group':group,
        # 'principal':principal,
    }
    return render(request, 'studentpage/showresult.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def showAnnualResult(request,pk,term,getgroup,getarm,getsession):
    session = Session.objects.get(ref=getsession)
    result = Result.objects.get(ref=pk)
    group = AllClass.objects.get(group=getgroup,arm=getarm)
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=result.student)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    check_record = Record.objects.filter(student = student.registration_number, term=4,group=getgroup,arm=getarm, active=0)
    check_result = Result.objects.filter(student=student.registration_number,term=4,group=getgroup,arm=getarm,active=0)
    # group = AllClass.objects.get(group=student.group,arm=student.arm)
    if check_record.exists() or check_result.exists():
        messages.error(request, 'Result not ready yet')
        return redirect('resultchecker')
    record = Record.objects.filter(student=student.registration_number,term=4,group=getgroup,arm=getarm,active=1).order_by('subject')
    get_result = Result.objects.get(student=student.registration_number,term=4,group=getgroup,arm=getarm)
    telegramMessage(f'Hello Miracle, {student.last_name} {student.first_name} with {student.registration_number} as registration number just checked annual term result.\nPosition:{get_result.position}/{group.number_of_student} from {student.group}{student.arm} class')
    context = {
        'student':student,
        'record':record,
        'result':get_result,
        'session':session,
        'term':term,
        'group':group,
        # 'principal':principal,
    }
    return render(request, 'studentpage/showannualresult.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def displayresultpdf(request,pk,term):
    STATIC_ROOT = os.path.join(settings.BASE_DIR, 'lms/static')
    # reg = Student.objects.get(id=pk).registration_number
    result = Result.objects.get(ref=pk)
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=result.student)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    avgagg = 0
    avgavg = 0
    
    if term == 3:
        avg = Result.objects.get(student=student.registration_number, term=3).average
        avgavg = Result.objects.get(student=student.registration_number, term=4).average
    else:
        avg = Result.objects.get(student=student.registration_number, term=term).average
    if avg >= 70:
        avgagg = 70
    elif avg >= 55:
        avgagg = 55
    elif avg >= 40:
        avgagg = 40
    else:
        avgagg = 39

    comment = Comment.objects.filter(score = avgagg)
    # student = Student.objects.filter(registration_number=student.registration_number)
    record = Record.objects.filter(student = student.registration_number, term=term)
    get_result = Result.objects.filter(student = student.registration_number, term=term)

    template_path = 'studentpage/resultdisplay_pdf.html'
    context = {
        'student':student,
        'record':record,
        'result':get_result,
        'average':avg,
        'averageavg':avgavg,
        'comment':comment,
        'STATIC_ROOT':STATIC_ROOT,
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

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def showtuition(request):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    # student = Student.objects.get(registration_number=request.user.username)
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=user.username)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    checkpaidstudent = Paid_Student.objects.filter(student=student.registration_number,term=term,year=year,session=session,status=1)
    if checkpaidstudent.exists():
        return redirect('tuitionreceipt')
    public_key = os.environ.get('PAYSTACK_PUBLIC_KEY')
    # public_key = os.getenv("PAYSTACK_PUBLIC_KEY")
    try:
        tuition = Payment.objects.get(category='tuition',group=student.group).amount
    except Payment.DoesNotExist:
        messages.info(request, 'Proceed to ICT unit before proceeding')
        return redirect('studentdash')
    group = student.group
    arm = student.arm

    ref = token_hex(16)
    while Paid_Student.objects.filter(ref=ref).exists():
        ref = token_hex(16)

    if not Paid_Student.objects.filter(student=student.registration_number, term=term,year=year,session=session).exists():
        Paid_Student.objects.create(
            student=student.registration_number,email=request.user.email,ref=ref,term=term,session=session,year=year,
            status=0,added_by=request.user,group=group,arm=arm,amount_paid=tuition
        )
    payment = Paid_Student.objects.filter(
        student=student.registration_number, term=term,year=year,session=session
    )

    context = {
        'public':public_key,
        'tuition':tuition,
        'payment':payment,
    }
    return render(request, 'studentpage/showtuitionfee.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def tuitionreceipt(request):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    school = Config.objects.get(id=1).school_name
    # student = Student.objects.get(registration_number=request.user.username)
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=user.username)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    payment = Paid_Student.objects.filter(
        student=student.registration_number, term=term,year=year,session=session,print=1
    )
    try:
        tuition = Payment.objects.get(category='tuition',group=student.group).amount
    except Payment.DoesNotExist:
        tuition = Payment.objects.get(category='tuition',group='all').amount
    Paid_Student.objects.filter(student = student.registration_number).update(
        status = 1, amount_paid = tuition
    )
    context = {'payment':payment, 'school':school}
    return render(request, 'studentpage/tuitionreceipt.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def hostel(request):
    if not Config.objects.get(id=1).use_hostel:
        messages.error(request,'Unauthorize access')
        return redirect('studentdash')
    hostel = Hostel.objects.filter(lock=0,active=1)
    context = {'hostel':hostel}
    return render(request, 'studentpage/hostelfee.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def showhostel(request, pk):
    if not Config.objects.get(id=1).use_hostel:
        messages.error(request,'Unauthorize access')
        return redirect('studentdash')
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=user.username)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    checkpaidstudent = Paid_Occupant.objects.filter(occupant=student.registration_number,term=term,year=year,session=session,status=1)
    if checkpaidstudent.exists():
        return redirect('hostelreceipt')
    public_key = os.environ.get('PAYSTACK_PUBLIC_KEY')
    print(public_key)
    # public_key = os.getenv("PAYSTACK_PUBLIC_KEY")
    hostel = Payment.objects.get(payment=pk).amount
    group = student.group
    arm = student.arm

    ref = token_hex(16)
    while Paid_Occupant.objects.filter(ref=ref).exists():
        ref = token_hex(16)

    if not Paid_Occupant.objects.filter(occupant=student.registration_number, term=term,year=year,session=session).exists():
        Paid_Occupant.objects.create(
            occupant=student.registration_number,email=request.user.email,ref=ref,term=term,session=session,year=year,
            status=0,added_by=request.user,group=group,arm=arm,hostel=pk
        )
    payment = Paid_Occupant.objects.filter(
        occupant=student.registration_number, term=term,year=year,session=session
    )

    context = {
        'public':public_key,
        'hostel':hostel,
        'payment':payment,
    }
    return render(request, 'studentpage/showhostelfee.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def hostelreceipt(request):
    if not Config.objects.get(id=1).use_hostel:
        messages.error(request,'Unauthorize access')
        return redirect('studentdash')
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=user.username)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    payment = Paid_Occupant.objects.filter(
        occupant=student.registration_number, term=term,year=year,session=session,print=1
    )
    hostel_name = Paid_Occupant.objects.get(
        occupant=student.registration_number, term=term,year=year,session=session,print=1
    ).hostel
    hostel = Payment.objects.get(payment=hostel_name).amount
    Paid_Occupant.objects.filter(occupant = student.registration_number).update(
        status = 1, amount_paid = hostel
    )
    context = {'payment':payment}
    return render(request, 'studentpage/hostelreceipt.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def history(request):
    # stud = request.user.username
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=user.username)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    tuition = Paid_Student.objects.filter(student=student.registration_number)
    hostel = Paid_Occupant.objects.filter(occupant=student.registration_number)
    context = {
        'tuition':tuition,
        'hostel':hostel
    }
    return render(request, 'studentpage/history.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def news(request):
    news = News.objects.filter(receiver='all',dashboard=True) | News.objects.filter(receiver='student',dashboard=True)
    context = {'news':news}
    return render(request,'studentpage/news.html',context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def single_news(request, reference):
    news = News.objects.get(reference=reference)
    context = {'news':news}
    return render(request,'studentpage/single_news.html',context)

class ChangePassword(LoginRequiredMixin, View):
    template_name = 'studentpage/changepassword.html'
    def get(self, request):
        return render(request,self.template_name)

    def post(self,request,*args,**kargs):
        user = User.objects.get(username=self.request.user.username)
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

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def profile(request):
    # student = Student.objects.get(registration_number=request.user.username)
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=user.username)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    profile = StudentUpdateForm(instance=student)
    # if request.method == 'POST':
    #     profile = StudentUpdateForm(request.POST, instance=student)
    #     if profile.is_valid():
    #         profile.save()
    #         messages.success(request, 'Update successful')
    #         return redirect('profile')
    context={
        'profile':profile
    }
    return render(request,'studentpage/profile.html',context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def registerCourses(request):
    session = Session.objects.get(active=1)
    term = Term.objects.get(active=1)
    user = request.user
    if user.profile.role.keyword == 'student':
        student = Student.objects.get(registration_number=user.username)
    elif user.profile.role.keyword == 'parent':
        parent = Parent.objects.get(unique_number=user.username)
        student = Student.objects.get(registration_number=parent.current_student)
    if not student.category == 'senior':
        messages.info(request, 'Your subjects will be automatically registered')
        return redirect('studentdash')
    
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
        print(len(registered))
        if len(registered) < 9 and len(registered) > 10:
            messages.error(request, 'Your subjects must be either 9 or 10')
            return redirect('student_course_register')
        
        registered.update(lock=True)
        student.register_course = True
        student.save()
        messages.success(request,'Registration successful')
        return redirect('student_course_register')

    context = {
        'student':student,
        'courses':courses,
        'registered':registered
    }
    return render(request, 'studentpage/register-courses.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def addCourses(request, sub, ref):
    session = Session.objects.get(active=1)
    term = Term.objects.get(active=1)
    subject = AllSubject.objects.get(ref=sub)
    student = Student.objects.get(ref=ref)
    registered = len(RegisteredSubjects.objects.filter(student=student.registration_number))
    course = registerSeniorStudentCourse(request,student,registered,session,term,subject,'student_course_register')
    return redirect('student_course_register')

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student','parent'])
def removeCourses(request,ref):
    course = removeStudentCourse(request,ref)
    return redirect('student_course_register')