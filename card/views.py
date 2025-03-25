from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from lms.decorators import allowed_users
from card.models import Card
from configuration.models import Config
from student.models import Student
import secrets
import csv

# Create your views here.

def pinletters(letter):
    
    if letter.lower() == 'a':
        exchange = '9'
    elif letter.lower() == 'b':
        exchange = '7'
    elif letter.lower() == 'c':
        exchange = '5'
    elif letter.lower() == 'd':
        exchange = '3'
    elif letter.lower() == 'e':
        exchange = '1'
    elif letter.lower() == 'f':
        exchange = '3'
    elif letter.lower() == '0':
        exchange = '2'
    else:
        exchange = letter

    return exchange

def generatePinSerial():
    sch_initial = Config.objects.get(id=1).school_initial
    genpin = secrets.token_hex(16)
    newpinserial = []
    pin = ''
    serial = ''
    data = []
    counter = 1
    for i in genpin:
        newpinserial.append(pinletters(i))

    # Generate pin and serial number
    for getpin in newpinserial:
        if counter <= 12:
            pin += getpin
        elif counter > 12 and counter <= 20:
            serial += getpin
        else:
            break
        counter += 1
    data.append(pin)
    data.append(sch_initial+serial)
        
    return data


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def generatecard(request):
    if 'submit' in request.POST:
        user = request.user
        typeChecker = int(request.POST.get('term'))
        js3ss3Checker = request.POST.get('ss3')
        print(js3ss3Checker)
        psw = request.POST.get('pass')
        if not user.check_password(psw):
            messages.error(request, 'Invalid password')
            return redirect('generatecard')
        response = HttpResponse(content_type = 'text/csv')
        writer = csv.writer(response)
        array = [
            ['SURNAME','FIRST NAME','REGISTRATION NUMBER','PASSWORD','CLASS','ARM','PIN', 'SERIAL NUMBER'],
            ['PIN', 'SERIAL NUMBER'],
            ['SURNAME','FIRST NAME','REGISTRATION NUMBER','PASSWORD','CLASS','ARM','PIN1', 'SERIAL NUMBER1','PIN2','SERIAL NUMBER2'],
            ['PIN1', 'SERIAL NUMBER1','PIN2', 'SERIAL NUMBER2'],
        ]
        writer.writerow(array[typeChecker])
        npin = int(request.POST.get('npin'))
        if js3ss3Checker == 'on':
            students = Student.objects.filter(active=1).order_by('group','arm','last_name')
        else:
            students = Student.objects.filter(active=1).exclude(group__endswith='3').order_by('group','arm','last_name')
        if typeChecker == 0:
            for student in students:
                cardDetail = generatePinSerial()
                writer.writerow([student.last_name,student.first_name,student.registration_number,student.token,student.group,student.arm,cardDetail[0],cardDetail[1]])
                Card.objects.create(pin=cardDetail[0],serial=cardDetail[1],student=student.registration_number,group=student.group,arm=student.arm)
        elif typeChecker == 1:
            for n in range(npin):
                cardDetail = generatePinSerial()
                writer.writerow([cardDetail[0],cardDetail[1]])
                Card.objects.create(pin=cardDetail[0],serial=cardDetail[1])
        elif typeChecker == 2:
            for student in students:
                cardDetail1 = generatePinSerial()
                cardDetail2 = generatePinSerial()
                writer.writerow([student.last_name,student.first_name,student.registration_number,student.token,student.group,student.arm,cardDetail1[0],cardDetail1[1],cardDetail2[0],cardDetail2[1]])
                Card.objects.create(pin=cardDetail1[0],serial=cardDetail1[1],student=student.registration_number,group=student.group,arm=student.arm)
                Card.objects.create(pin=cardDetail2[0],serial=cardDetail2[1],student=student.registration_number,group=student.group,arm=student.arm)
        elif typeChecker == 3:
            for n in range(npin):
                cardDetail1 = generatePinSerial()
                cardDetail2 = generatePinSerial()
                writer.writerow([cardDetail1[0],cardDetail1[1],cardDetail2[0],cardDetail2[1]])
                Card.objects.create(pin=cardDetail1[0],serial=cardDetail1[1])
                Card.objects.create(pin=cardDetail2[0],serial=cardDetail2[1])

        response['Content-Disposition'] = f'attachment; filename="Card.csv"'
        messages.success(request, 'Generated and export')
        return response
    return render(request, 'card/cardgenerate.html')