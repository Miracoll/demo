from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from configuration.models import Config, Session, Term, Class,Arm
from student.models import Student, Paid_Student
from applicant.models import Applicant, Paid_Applicant
from .models import Payment
from hostel.models import Hostel
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from lms.decorators import allowed_users
from lms.models import Profile
import os
from secrets import token_hex
import csv
from random import randrange
from lms.functions import generateStudentRegNumber

# Create your views here.

def setup(request):
    group = Class.objects.all()
    arm = Arm.objects.all()
    if 'pay' in request.POST:
        pay = request.POST.get('payment').capitalize()
        amount = request.POST.get('amount')
        cat = request.POST.get('cat')
        getgroup = request.POST.get('group')
        print(getgroup)
        # getarm = request.POST.get('arm')

        if cat == 'tuition' or cat == 'others':
            if getgroup == 'all':
                for i in group.values():
                    if Payment.objects.filter(category=cat,group=i['group']).exists():
                        continue
                    Payment.objects.create(payment=pay,amount=amount,category=cat,group=i['group'],added_by=request.user)
                messages.success(request, 'Payment added')
                return redirect('payment_setup')
            elif getgroup == 'junior':
                junior_class = Class.objects.filter(category='junior')
                junior_class = Class.objects.filter(category='junior')
                if not junior_class.exists():
                    messages.error(request, 'No class for the category')
                    return redirect('payment_setup')
                for i in junior_class.values():
                    if Payment.objects.filter(category=cat,group=i['group']).exists():
                        continue
                    Payment.objects.create(payment=pay,amount=amount,category=cat,group=i['group'],added_by=request.user)
                messages.success(request, 'Payment added')
                return redirect('payment_setup')
            elif getgroup == 'senior':
                senior_class = Class.objects.filter(category='senior')
                if not senior_class.exists():
                    messages.error(request, 'No class for the category')
                    return redirect('payment_setup')
                for i in senior_class.values():
                    if Payment.objects.filter(category=cat,group=i['group']).exists():
                        continue
                    Payment.objects.create(payment=pay,amount=amount,category=cat,group=i['group'])
                messages.success(request, 'Payment added')
                return redirect('payment_setup')
            else:
                if not Class.objects.filter(group=getgroup).exists():
                    messages.error(request, 'Self destruction activated')
                    Profile.objects.filter(user=request.user).update(blocked_reason='Illegal data entry')
                    User.objects.filter(username=request.user.username).update(is_active=False)
                    return redirect('logout')
                Payment.objects.create(payment=pay,amount=amount,category=cat,group=getgroup,added_by=request.user)
                messages.success(request, 'Payment added')
                return redirect('payment_setup')

        elif cat == 'application':
            if Payment.objects.filter(category='application').exists():
                messages.warning(request,'Application fee payment already setup')
                return redirect('payment_setup')
            Payment.objects.create(payment=pay,amount=amount,category=cat,added_by=request.user,group='all')
            messages.success(request, 'Payment added')
            return redirect('payment_setup')
        
        else:
            messages.error(request, 'Invalid selection')
            return redirect('payment_setup')
    context = {'group':group,'arm':arm}
    return render(request,'payment/setup.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','bursar'])
def clearapplication(request):
    if 'clear' in request.POST:
        ref_num = request.POST.get('pay_ref')
        pay = Paid_Applicant.objects.get(payment_ref=ref_num)
        if pay.status == 1:
            messages.error(request, 'applicant already cleared')
            return redirect('clear_application')
        applicant = Applicant.objects.get(ref=pay.applicant.ref)
        if Applicant.objects.filter(ref=ref_num).exists():
            # pemail = Applicant.objects.get(email=email).email
            pamount = Payment.objects.get(category='application').amount

            level = Class.objects.get(group=applicant.group)

            # ref = token_hex(16)
            # while Paid_Applicant.objects.filter(ref=ref).exists():
            #     ref = token_hex(16)
            # payment = Paid_Applicant.objects.get(payment_ref=ref_num).payment_ref

            if Paid_Applicant.objects.filter(payment_ref=ref_num).exists():
                Paid_Applicant.objects.filter(payment_ref=ref_num).update(status=1,amount=pamount,cleared_by=request.user,manual_cleared = True)
            else:
                messages.error(request, 'Payment not found')
                return redirect('clear_application')
            # # Generate registration number here
            # rand = generateStudentRegNumber(applicant.category)
            # Student.objects.create(
            #     last_name=applicant.last_name,first_name=applicant.first_name,other_name=applicant.other_name,email=applicant.email,mobile=applicant.mobile,
            #     group=applicant.group,arm=applicant.arm,year=applicant.year,term=applicant.term,session=applicant.session,registration_number=rand,
            #     level = level.level,category=level.category
            # )
            messages.success(request, 'Cleared')
            return redirect('clear_application')
        else:
            messages.warning(request, 'Such applicant does not exist')
            return redirect('clear_application')
    return render(request, 'payment/applicationclear.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','bursar'])
def managepayment(request):
    payment = Payment.objects.all()
    context = {'payment':payment}
    return render(request, 'payment/managepayment.html',context)

def modifypayment(request, pk):
    payment = Payment.objects.filter(ref=pk)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        Payment.objects.filter(ref=pk).update(amount=int(amount))
        messages.success(request, 'Done')
        return redirect('manage_payment')
    context = {'payment':payment}
    return render(request, 'payment/modifypayment.html', context)

def paidstudent(request):
    payment = Payment.objects.all()
    getterm = Term.objects.all()
    getsession = Session.objects.all()
    if request.method == 'POST':
        getapplicationfee = Payment.objects.get(category='application').amount
        payment_type = request.POST.get('payment')
        status = request.POST.get('status')
        session = request.POST.get('session')
        term = request.POST.get('term')
        print(payment_type)
        print(status)
        # Get paid students (TUITION FEE)
        if (payment_type.capitalize() == 'Tuition') and (status == '1'):
            paidstudent = Paid_Student.objects.filter(session=session,term=term,status=1)
            students = paidstudent.values_list('student','group','arm','session','term')
            response = HttpResponse(content_type = 'text/csv')
            writer = csv.writer(response)
            writer.writerow(['Last Name', 'First Name', 'Registration Number','Class','Arm','Session_paid','Term_paid'])
            for student in students:
                stud = [
                    Student.objects.get(registration_number=student[0]).last_name,
                    Student.objects.get(registration_number=student[0]).first_name,
                    student[0],
                    student[1],
                    student[2],
                    student[3],
                    student[4],
                ]
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="Paid students for {session} term {term}.csv"'
            return response
        # Get unpaid students (TUITION FEE)
        elif (payment_type.capitalize() == 'Tuition') and (status == '2'):
            allstudent = Student.objects.filter(active = 1)
            students = allstudent.values_list('last_name','first_name','registration_number','group')
            response = HttpResponse(content_type = 'text/csv')
            writer = csv.writer(response)
            writer.writerow(['Last Name', 'First Name', 'Registration Number','Amount paid','Balance'])
            for student in students:
                gettuitionfee = Payment.objects.get(category='tuition',group=student[3]).amount
                if Paid_Student.objects.filter(student=student[2],session=session,term=term,amount_paid=gettuitionfee, status=1).exists():
                    continue
                if Paid_Student.objects.filter(student=student[2],session=session,term=term, status=1).exists():
                    amount_paid = Paid_Student.objects.get(student=student[2],session=session,term=term, status=1).amount_paid
                    balance = int(gettuitionfee) - int(amount_paid)
                else:
                    amount_paid = 0
                    balance = gettuitionfee
                stud = [
                    student[0],
                    student[1],
                    student[2],
                    amount_paid,
                    balance,
                ]
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{session} term {term} unpaid students.csv"'
            return response

        # Get all students (TUITION FEE)
        elif (payment_type.capitalize() == 'Tuition') and (status == '3'):
            allstudent = Student.objects.filter(active = 1)
            students = allstudent.values_list('last_name','first_name','registration_number','group')
            response = HttpResponse(content_type = 'text/csv')
            writer = csv.writer(response)
            writer.writerow(['Last Name', 'First Name', 'Registration Number','Amount paid','Balance','Status'])
            for student in students:
                gettuitionfee = Payment.objects.get(category='tuition',group=student[3]).amount
                if Paid_Student.objects.filter(student=student[2],session=session,term=term,amount_paid=gettuitionfee, status=1).exists():
                    status = 'Paid'
                    amount_paid = Paid_Student.objects.get(student=student[2],session=session,term=term, status=1).amount_paid
                    balance = int(gettuitionfee) - int(amount_paid)
                elif Paid_Student.objects.filter(student=student[2],session=session,term=term, status=1).exists():
                    amount_paid = Paid_Student.objects.get(student=student[2],session=session,term=term, status=1).amount_paid
                    balance = int(gettuitionfee) - int(amount_paid)
                    status = 'Incomplete'
                else:
                    amount_paid = 0
                    balance = gettuitionfee
                    status = 'Not paid'
                stud = [
                    student[0],
                    student[1],
                    student[2],
                    amount_paid,
                    balance,
                    status,
                ]
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{session} term {term} payment.csv"'
            return response

        # Get paid applicant (APPLICATION FEE)
        if (payment_type.capitalize() == 'Application') and (status == '1'):
            paidstudent = Paid_Applicant.objects.filter(amount=getapplicationfee,session=session,term=term,status=1)
            students = paidstudent.values_list('email','ref','session','term')
            response = HttpResponse(content_type = 'text/csv')
            writer = csv.writer(response)
            writer.writerow(['Last Name', 'First Name', 'Email','Payment Reference','Session','Term'])
            for student in students:
                stud = [
                    Applicant.objects.get(email=student[0]).last_name,
                    Applicant.objects.get(email=student[0]).first_name,
                    student[0],
                    student[1],
                    student[2],
                    student[3],
                ]
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="Paid applicants for {session} term {term}.csv"'
            return response

        # Get unpaid applicants (APPLICATION FEE)
        elif (payment_type.capitalize() == 'Application') and (status == '2'):
            allstudent = Applicant.objects.filter(session = session, term=term)
            students = allstudent.values_list('last_name','first_name','email')
            response = HttpResponse(content_type = 'text/csv')
            writer = csv.writer(response)
            writer.writerow(['Last Name', 'First Name', 'Email','Amount paid','Balance','Payment Reference','mobile'])
            for student in students:
                ref = Paid_Applicant.objects.get(email=student[2],session=session,term=term).ref
                mobile = Applicant.objects.get(email=student[2],session=session,term=term).mobile
                if Paid_Applicant.objects.filter(email=student[2],session=session,term=term,amount=getapplicationfee, status=1).exists():
                    continue
                elif Paid_Applicant.objects.filter(email=student[2],session=session,term=term, status=1).exists():
                    amount_paid = Paid_Applicant.objects.get(email=student[2],session=session,term=term, status=1).amount
                    balance = int(getapplicationfee) - int(amount_paid)
                else:
                    amount_paid = 0
                    balance = getapplicationfee
                stud = [
                    student[0],
                    student[1],
                    student[2],
                    amount_paid,
                    balance,
                    ref,
                    mobile
                ]
                writer.writerow(stud)
            response['Content-Disposition'] = f'attachment; filename="{session} term {term} unpaid students.csv"'
            return response
    context = {
        'payment':payment,
        'term':getterm,
        'session':getsession
    }
    return render(request, 'payment/paidstudent.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','bursar'])
def cleartuition(request):
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    if request.method == 'POST':
        reg = request.POST.get('reg')
        amount = request.POST.get('amount')
        pamount = Paid_Student.objects.get(student=reg,session=session,term=term).amount_paid
        print(amount,pamount,reg)
        if str(amount) != str(pamount):
            messages.warning(request, 'Sorry amount did not match')
            return redirect('cleartuition')
        checkstudent = Paid_Student.objects.filter(student=reg, year=year, term=term, session=session, status=0)
        if checkstudent.exists():
            checkstudent.update(amount_paid=pamount, status=1)
            messages.success(request, 'Cleared')
            return redirect('cleartuition')
        else:
            messages.warning(request, 'Something went wrong, contact admin')
            return redirect('cleartuition')
    return render(request, 'payment/tuitionclear.html')