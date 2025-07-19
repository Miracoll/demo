from academic.models import Record
from configuration.models import Session
from .models import Result
from django.db.models import Avg

def gradeGetter(reg):
    a = 0
    c = 0
    p = 0
    f = 0

    session = Session.objects.get(active=1)

    for i in range(1,4):
        record = Record.objects.filter(student=reg,term=i,session=session.session)
        for j in record:
            if j.grade == 'A':
                a += 1
            elif j.grade == 'C':
                c += 1
            elif j.grade == 'P':
                p += 1
            elif j.grade == 'F':
                f += 1
    grade = [a,c,p,f]
    return grade

def stat(group, session):
    record = len(Result.objects.filter(group=group.group,arm=group.arm,session=session.session,term=4))
    passed_number = len(Result.objects.filter(term=4,group=group.group,arm=group.arm,average__gte=40,session=session.session))
    failed_number = len(Result.objects.filter(term=4,group=group.group,arm=group.arm,average__lt=40,session=session.session))
    try:
        passed_percent = round((passed_number/record)*100,2)
    except ZeroDivisionError:
        return None
    try:
        failed_percent = round((failed_number/record)*100,2)
    except ZeroDivisionError:
        return None
    avg = Result.objects.filter(group=group.group,arm=group.arm,session=session.session,term=4).aggregate(avg=Avg('average'))['avg']

    return [passed_number,passed_percent,failed_number,failed_percent,round(avg,2)]