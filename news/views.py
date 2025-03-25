from django.shortcuts import redirect, render
from .forms import NewsForm
from .models import News
from django.contrib import messages
from student.models import Student
from staff.models import Staff
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from lms.decorators import unauthenticated_user, allowed_users
# import os
# from twilio.rest import Client

# Create your views here.

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def news(request):
    allnews = News.objects.filter(private=False)
    form = NewsForm()
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        student = Student.objects.filter(active=1)
        staff = Staff.objects.filter(active=1)
        if form.is_valid():
            sms = request.POST.get('sms')
            email = request.POST.get('email')
            dashboard = request.POST.get('dashboard')
            title = form.cleaned_data.get('title')
            content = form.cleaned_data.get('content')
            # print(sms,email,dashboard)
            news = form.save(commit=False)
            if sms == 'on':
                get_sms = True
            else:
                get_sms = False
            if email == 'on':
                get_email = True
            else:
                get_email = False
            if dashboard == 'on':
                get_dashboard = True
            else:
                get_dashboard = False
            
            news.sms = get_sms
            news.email = get_email
            news.dashboard = get_dashboard
            news.author = request.user
            news.private = False
            news.save()
            if get_email:
                for i in student.values():
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [i.get('email')]
                    send_mail( title, content, email_from, recipient_list )
                for i in staff.values():
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [i.get('email')]
                    send_mail( title, content, email_from, recipient_list )
            # if get_sms:
            #     for i in student.values():
            #         account_sid = os.environ['TWILIO_ACCOUNT_SID']
            #         auth_token = os.environ['TWILIO_AUTH_TOKEN']
            #         client = Client(account_sid, auth_token)

            #         message = client.messages.create(
            #             body=f"{content}",
            #             from_='+15017122661',
            #             to='+15558675310'
            #         )
            #         print(message.sid)
            #     for i in staff.values():
            #         account_sid = os.environ['TWILIO_ACCOUNT_SID']
            #         auth_token = os.environ['TWILIO_AUTH_TOKEN']
            #         client = Client(account_sid, auth_token)

            #         message = client.messages.create(
            #             body=f"{content}",
            #             from_='+15017122661',
            #             to='+15558675310'
            #         )
            #         print(message.sid)
            messages.success(request, 'Done')
            return redirect('news')
    context = {'form':form,'news':allnews}
    return render(request, 'news/news.html', context)
    
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','controller'])
def private_news(request):
    allnews = News.objects.filter(private=True)
    form = NewsForm()
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            sms = request.POST.get('sms')
            email = request.POST.get('email')
            dashboard = request.POST.get('dashboard')
            receiver = request.POST.get('receiver')
            title = form.cleaned_data.get('title')
            content = form.cleaned_data.get('content')
            news = form.save(commit=False)
            if sms == 'on':
                get_sms = True
            else:
                get_sms = False
            if email == 'on':
                get_email = True
            else:
                get_email = False
            if dashboard == 'on':
                get_dashboard = True
            else:
                get_dashboard = False
            
            news.sms = get_sms
            news.email = get_email
            news.dashboard = get_dashboard
            news.author = request.user
            news.private = True
            news.save()
            if receiver == 'student':
                receivers = Student.objects.filter(active=1)
                if get_email:
                    for i in receivers.values():
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [i.get('email')]
                        send_mail( title, content, email_from, recipient_list )
                    # if get_sms:
                    #     for i in receivers.values():
                    #         account_sid = os.environ['TWILIO_ACCOUNT_SID']
                    #         auth_token = os.environ['TWILIO_AUTH_TOKEN']
                    #         client = Client(account_sid, auth_token)

                    #         message = client.messages.create(
                    #             body=f"{content}",
                    #             from_='+15017122661',
                    #             to='+15558675310'
                    #         )
                    #         print(message.sid)
            elif receiver == 'staff':
                receivers = Staff.objects.filter(active=1)
                if get_email:
                    for i in receivers.values():
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [i.get('email')]
                        send_mail( title, content, email_from, recipient_list )
                # if get_sms:
                #     for i in receivers.values():
                #         account_sid = os.environ['TWILIO_ACCOUNT_SID']
                #         auth_token = os.environ['TWILIO_AUTH_TOKEN']
                #         client = Client(account_sid, auth_token)

                #         message = client.messages.create(
                #             body=f"{content}",
                #             from_='+15017122661',
                #             to='+15558675310'
                #         )
                #         print(message.sid)
            elif receiver == 'parent':
                receivers = Student.objects.filter(active=1)
                if get_email:
                    for i in receivers.values():
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [i.get('nok_email')]
                        send_mail( title, content, email_from, recipient_list )
                # if get_sms:
                #     for i in receivers.values():
                #         account_sid = os.environ['TWILIO_ACCOUNT_SID']
                #         auth_token = os.environ['TWILIO_AUTH_TOKEN']
                #         client = Client(account_sid, auth_token)

                #         message = client.messages.create(
                #             body=f"{content}",
                #             from_='+15017122661',
                #             to='+15558675310'
                #         )
                #         print(message.sid)
                
            messages.success(request, 'Done')
            return redirect('privatenews')
    context = {'form':form,'news':allnews}
    return render(request, 'news/private_news.html', context)

def createnews(request):
    form = NewsForm()
    context = {'form':form}
    return render(request, 'news/createnews.html', context)