from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Sum
import csv
from operator import itemgetter
from io import StringIO
from decimal import Decimal
from configuration.models import Subject,Config,AllClass,RegisteredSubjects
from student.models import Student
from result.models import Result
from attendance.models import Attendance
from .models import Record

def calculate_result(request,uugroup,uuarm,uusub,csv_file,term,session,year,check_summer):
    teacher = Subject.objects.get(group=uugroup,arm=uuarm,subject=uusub).teacher
    getlock = Subject.objects.get(teacher=teacher,group=uugroup,arm=uuarm,subject=uusub).lock
    get_class = AllClass.objects.get(group=uugroup,arm=uuarm)
    get_subject = Subject.objects.get(group=uugroup,arm=uuarm,subject=uusub)
    print(get_class.promotion_score)
    if get_class.promotion_score is None:
        messages.error(request, 'Class have not been setup for result computation')
        return redirect('assessment')
    allstudent = [] #   Holding data for result computation
    check_empty_file = []
    totalindex = 0
    if getlock != 0:
        messages.error(request,'Already done upload')
        return redirect('assessment')
    allrecord = []
    record = ''
    file = csv_file.read().decode('utf-8')
    csv_data = csv.reader(StringIO(file), delimiter=',')
    next(csv_data)
    for line in csv_data:
        try:
            ca1 = round(float(line[6]),2)
            ca2 = round(float(line[7]),2)
            # ca3 = float(line[8])
            # project = float(line[9])
            # test = float(line[10])
            exam = round(float(line[8]),2)
        except ValueError:
            messages.error(request, 'Invalid data type, pls re-check your input')
            return redirect('assessment')
        student_class = line[3]
        student_arm = line[4]
        reg = line[2]
        getsubject = line[5]
        user = request.user
        total =ca1+ca2+exam
        if int(total) >= 70:
            grade = 'A'
            remark = 'Excellent'
        elif int(total) >= 55:
            grade = 'C'
            remark = 'Credit'
        elif int(total) >= 40:
            grade = 'P'
            remark = 'Pass'
        else:
            grade = 'F'
            remark = 'Fail'
        
        check_empty_file.append(total)
        unitstudent = list((ca1,ca2,exam,student_class,student_arm,reg,total,uusub,term))
        totalindex = int(unitstudent.index(total))
        print(f'totalindex is {totalindex}')
        allstudent.append(unitstudent)
        if student_class == uugroup and getsubject == uusub and student_arm == uuarm:
            record = Record(
                CA1=ca1,CA2=ca2,exam=exam,
                group=student_class,subject=getsubject,term=term,arm=student_arm,
                total=total,grade=grade,remark=remark,session=session,year=year,
                student=reg,added_by=user
            )
        else:
            messages.error(request, 'Upload failed, get another template and try again')
            return redirect('assessment')
        allrecord.append(record)
        check_record = Record.objects.filter(
            student=reg,session=session,term=term,subject=getsubject,group=uugroup,arm=uuarm
        )
        if check_record.exists():
            check_record.delete()
        upload = Subject.objects.get(group=uugroup,arm=uuarm,subject=uusub).upload
        Subject.objects.filter(group=uugroup, arm=uuarm,subject=uusub).update(upload=upload+1)
    check_sum = round(float(sum(check_empty_file)),2)
    if check_sum != check_summer:
        messages.error(request, 'File not saved or incorrect total score')
        return redirect('assessment')
    Record.objects.bulk_create(allrecord)
    # Update class average score
    class_subject_total = Record.objects.filter(subject=uusub,group=uugroup,arm=uuarm,term=term,session=session).aggregate(total = Sum('total'))
    subject_average = float(class_subject_total.get('total'))/get_subject.total_student
    Record.objects.filter(subject=uusub, group=uugroup,arm=uuarm,term=term, session=session).update(average=subject_average)
    # Calculate subject position here
    sp = sorted(allstudent, key=itemgetter(totalindex), reverse=True)
    print('in am in result')
    print(sp)
    prevpos = 0
    pos = 0
    position=0
    result_counter = 0
    same = 1
    for i in sp:
        fixpos = Record.objects.filter(group=i[3],arm=i[4],student=i[5],subject=i[7],term=term,session=session)
        if i[totalindex]  == prevpos:
            prevpos = i[totalindex]
            same += 1
            pos = result_counter
            if (pos == 1)or(pos == 21)or(pos == 31)or(pos == 41)or(pos == 51)or(pos == 61)or(pos == 71)or(pos == 81)or(pos == 91):
                position = str(pos) + 'st'
            elif (pos == 2)or(pos == 22)or(pos == 32)or(pos == 42)or(pos == 52)or(pos == 62)or(pos == 72)or(pos == 82)or(pos == 92):
                position = str(pos) + 'nd'
            elif (pos == 3)or(pos == 23)or(pos == 33)or(pos == 43)or(pos == 53)or(pos == 63)or(pos == 73)or(pos == 83)or(pos == 93):
                position = str(pos) + 'rd'
            else:
                position = str(pos) + 'th'
        else:
            result_counter += same
            pos = result_counter
            prevpos = i[totalindex]
            if (pos == 1)or(pos == 21)or(pos == 31)or(pos == 41)or(pos == 51)or(pos == 61)or(pos == 71)or(pos == 81)or(pos == 91):
                position = str(pos) + 'st'
            elif (pos == 2)or(pos == 22)or(pos == 32)or(pos == 42)or(pos == 52)or(pos == 62)or(pos == 72)or(pos == 82)or(pos == 92):
                position = str(pos) + 'nd'
            elif (pos == 3)or(pos == 23)or(pos == 33)or(pos == 43)or(pos == 53)or(pos == 63)or(pos == 73)or(pos == 83)or(pos == 93):
                position = str(pos) + 'rd'
            else:
                position = str(pos) + 'th'
            same = 1
        fixpos.update(position=position)
    Subject.objects.filter(teacher=teacher,group=uugroup,arm=uuarm,subject=uusub).update(lock=1)
    # Position calculation ends here

    # Calculate Result table data
    resultsta = Config.objects.get(id=1).start_result
    if resultsta == 1:
        # getgroup = uugroup
        # getarm = uuarm
        allresult = []
        allresultpos = []
        averageindex = 0

        studentand = RegisteredSubjects.objects.filter(group = uugroup,subject=uusub,arm=uuarm, active = 1)
        student = studentand.values_list('last_name','first_name','student')
        # response = HttpResponse(content_type = 'text/csv')
        # writer = csv.writer(response)
        # writer.writerow(['Last Name', 'First Name', 'Registration Number','Total','Average','Position'])
        if len(student) <= 0:
            messages.error(request,'No record found')
            return redirect('result_template')
        else:
            for student in student:
                stud = list(student)
                print(stud)
                studtotal = Record.objects.filter(student = stud[2],group=uugroup,arm=uuarm,term=term,session=session).aggregate(total = Sum('total'))
                print(studtotal)
                if stud[2] == None:
                    continue
                if studtotal['total'] == None:
                    studtotal['total'] = 0

                student_subject_list = RegisteredSubjects.objects.filter(student=stud[2],session=session,lock=True)
                if len(student_subject_list) == 0:
                    avg = 0
                else:
                    avg = int(studtotal['total'])/int(len(student_subject_list))

                present = len(Attendance.objects.filter(student = reg,status = 1,term = term,session=session))
                absent = len(Attendance.objects.filter(student = reg,status = 0,term = term,session=session))
                unitresult = list((stud[2],studtotal['total'],avg,term,uugroup,uuarm,year,session))
                averageindex = int(unitresult.index(avg))
                allresultpos.append(unitresult)
                if avg >= get_class.promotion_score:
                    result_remark = 'PASS'
                else:
                    result_remark = 'FAIL'

                if Result.objects.filter(student=stud[2],term=term,year=year,session=session).exists():
                    Result.objects.filter(student=stud[2],term=term,year=year,session=session).update(
                        total = studtotal['total'], average=avg,remark=result_remark
                    )
                else:
                    Result.objects.create(
                        student=stud[2],total=studtotal['total'],average=avg,present=present,absent=absent,
                        term=term,group=uugroup,arm=uuarm,year=year,session=session,added_by=request.user,
                        remark=result_remark
                    )
                # result = Result(
                #     student=stud[2],total=studtotal['total'],average=avg,present=present,absent=absent,
                #     term=term,group=getgroup,arm=getarm,year=year,session=session,added_by=request.user,
                # )
                # allresult.append(result)
            # Result.objects.bulk_create(allresult)

            
            # Calculate result position here
            sortedresult = sorted(allresultpos, key=itemgetter(averageindex), reverse=True)
            prevpos = 0
            pos = 0
            result_counter = 0
            same = 1
            position=0
            for i in sortedresult:
                fixpos = Result.objects.filter(group=i[4],arm=i[5],student=i[0],term=term,session=session)
                if i[averageindex]  == prevpos:
                    prevpos = i[averageindex]
                    same += 1
                    pos = result_counter
                    if (pos == 1)or(pos == 21)or(pos == 31)or(pos == 41)or(pos == 51)or(pos == 61)or(pos == 71)or(pos == 81)or(pos == 91):
                        position = str(pos) + 'st'
                    elif (pos == 2)or(pos == 22)or(pos == 32)or(pos == 42)or(pos == 52)or(pos == 62)or(pos == 72)or(pos == 82)or(pos == 92):
                        position = str(pos) + 'nd'
                    elif (pos == 3)or(pos == 23)or(pos == 33)or(pos == 43)or(pos == 53)or(pos == 63)or(pos == 73)or(pos == 83)or(pos == 93):
                        position = str(pos) + 'rd'
                    else:
                        position = str(pos) + 'th'
                else:
                    result_counter += same
                    pos = result_counter
                    prevpos = i[averageindex]
                    if (pos == 1)or(pos == 21)or(pos == 31)or(pos == 41)or(pos == 51)or(pos == 61)or(pos == 71)or(pos == 81)or(pos == 91):
                        position = str(pos) + 'st'
                    elif (pos == 2)or(pos == 22)or(pos == 32)or(pos == 42)or(pos == 52)or(pos == 62)or(pos == 72)or(pos == 82)or(pos == 92):
                        position = str(pos) + 'nd'
                    elif (pos == 3)or(pos == 23)or(pos == 33)or(pos == 43)or(pos == 53)or(pos == 63)or(pos == 73)or(pos == 83)or(pos == 93):
                        position = str(pos) + 'rd'
                    else:
                        position = str(pos) + 'th'
                    same = 1
                fixpos.update(position=position)
        
            # Calculate result position ends here
            

            # Anual result computation
            anualstudentresult = []
            if term == 3:
                getallstudent = RegisteredSubjects.objects.filter(group=uugroup,subject=uusub,arm=uuarm,active=1,lock=1)
                liststudent = getallstudent.values_list('registration_number','group','arm')
                alltermtotal = 0
                indexpos = ''
                for student in liststudent:

                    # Total score for 1st term
                    try:
                        resulttotal1 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=1
                        ).total
                        if resulttotal1 == None:
                            resulttotal1 = 0
                    except Result.DoesNotExist:
                        resulttotal1=0

                    # Total score for 2nd term
                    try:
                        resulttotal2 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=2
                        ).total
                        if resulttotal2 == None:
                            resulttotal2 = 0
                    except Result.DoesNotExist:
                        resulttotal2=0
                        
                    # Total score for 3rd term
                    try:
                        resulttotal3 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=3
                        ).total
                        if resulttotal3 == None:
                            resulttotal3 = 0
                    except Result.DoesNotExist:
                        resulttotal3=0

                    # Average score for 1st term
                    try:
                        avgresultscore1 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=1
                        ).average
                        if avgresultscore1 == None:
                            avgresultscore1 = 0
                    except Result.DoesNotExist:
                        avgresultscore1=0

                    # Average score for 2nd term
                    try:
                        avgresultscore2 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=2
                        ).average
                        if avgresultscore2 == None:
                            avgresultscore2 = 0
                    except Result.DoesNotExist:
                        avgresultscore2=0
                        
                    # Average score for 3rd term
                    try:
                        avgresultscore3 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=3
                        ).average
                        if avgresultscore3 == None:
                            avgresultscore3 = 0
                    except Result.DoesNotExist:
                        avgresultscore3=0

                    # Present attendance counter for 1st term
                    try:
                        getpresent1 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=1
                        ).present
                        if getpresent1 == None:
                            getpresent1 = 0
                    except Result.DoesNotExist:
                        getpresent1=0

                    # Present attendance counter for 2nd term
                    try:
                        getpresent2 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=2
                        ).present
                        if getpresent2 == None:
                            getpresent2 = 0
                    except Result.DoesNotExist:
                        getpresent2=0

                    # Present attendance counter for 3rd term
                    try:
                        getpresent3 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=3
                        ).present
                        if getpresent3 == None:
                            getpresent3 = 0
                    except Result.DoesNotExist:
                        getpresent3=0

                    # Absent attendance counter for 1st term
                    try:
                        getabsent1 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=1
                        ).absent
                        if getabsent1 == None:
                            getabsent1 = 0
                    except Result.DoesNotExist:
                        getabsent1=0

                    # Absent attendance counter for 2nd term
                    try:
                        getabsent2 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=2
                        ).absent
                        if getabsent2 == None:
                            getabsent2 = 0
                    except Result.DoesNotExist:
                        getabsent2=0

                    # Absent attendance counter for 3rd term
                    try:
                        getabsent3 = Result.objects.get(
                            student=student[0],group=student[1],arm=student[2],term=3
                        ).absent
                        if getabsent3 == None:
                            getabsent3 = 0
                    except Result.DoesNotExist:
                        getabsent3=0

                    resulttotal = (resulttotal1+resulttotal2+resulttotal3)/3
                    avgresultscore = (avgresultscore1+avgresultscore2+avgresultscore3)/3
                    getpresent = getpresent1+getpresent2+getpresent3
                    getabsent = getabsent1+getabsent2+getabsent3

                    anualunit = list((student[0],alltermtotal,avgresultscore,4,student[1],student[2],year,session))
                    indexpos = int(anualunit.index(avgresultscore))
                    anualstudentresult.append(anualunit)
                    print(f'i am result total {resulttotal}')
                    if avgresultscore >= get_class.promotion_score:
                        result_remark = 'PROMOTED'
                    else:
                        result_remark = 'NOT PROMOTED'
                    if Result.objects.filter(student=student[0],term=4,year=year,session=session).exists():
                        Result.objects.filter(student=student[0],term=4,year=year,session=session).update(
                            total=resulttotal,average=avgresultscore,remark=result_remark
                        )
                    else:
                        Result.objects.create(
                            student=student[0],total=resulttotal,average=avgresultscore,present=getpresent,absent=getabsent,
                            term=4,group=student[1],arm=student[2],year=year,session=session,added_by=request.user,remark=result_remark
                        )
                #     anualresultunit = Result(
                #         student=student[0],total=alltermtotal,average=avgresultscore,present=anualpresent,absent=anualabsent,
                #         term=4,group=student[1],arm=student[2],year=year,session=session,added_by=request.user,
                #     )
                #     anualresult.append(anualresultunit)
                #     alltermtotal = 0
                # Result.objects.bulk_create(anualresult)

                # Position
                sortedresult = sorted(anualstudentresult, key=itemgetter(indexpos), reverse=True)
                prevpos = 0
                pos = 0
                result_counter = 0
                same = 1
                position=0
                for i in sortedresult:
                    fixpos = Result.objects.filter(group=i[4],arm=i[5],student=i[0],term=4,session=session)
                    if i[indexpos]  == prevpos:
                        prevpos = i[indexpos]
                        same += 1
                        pos = result_counter
                        if (pos == 1)or(pos == 21)or(pos == 31)or(pos == 41)or(pos == 51)or(pos == 61)or(pos == 71)or(pos == 81)or(pos == 91):
                            position = str(pos) + 'st'
                        elif (pos == 2)or(pos == 22)or(pos == 32)or(pos == 42)or(pos == 52)or(pos == 62)or(pos == 72)or(pos == 82)or(pos == 92):
                            position = str(pos) + 'nd'
                        elif (pos == 3)or(pos == 23)or(pos == 33)or(pos == 43)or(pos == 53)or(pos == 63)or(pos == 73)or(pos == 83)or(pos == 93):
                            position = str(pos) + 'rd'
                        else:
                            position = str(pos) + 'th'
                    else:
                        result_counter += same
                        pos = result_counter
                        prevpos = i[indexpos]
                        if (pos == 1)or(pos == 21)or(pos == 31)or(pos == 41)or(pos == 51)or(pos == 61)or(pos == 71)or(pos == 81)or(pos == 91):
                            position = str(pos) + 'st'
                        elif (pos == 2)or(pos == 22)or(pos == 32)or(pos == 42)or(pos == 52)or(pos == 62)or(pos == 72)or(pos == 82)or(pos == 92):
                            position = str(pos) + 'nd'
                        elif (pos == 3)or(pos == 23)or(pos == 33)or(pos == 43)or(pos == 53)or(pos == 63)or(pos == 73)or(pos == 83)or(pos == 93):
                            position = str(pos) + 'rd'
                        else:
                            position = str(pos) + 'th'
                        same = 1
                        
                    fixpos.update(position=position)
                # Position ends
            # Anual result computation ends here

    else:
        messages.error(request,'The principal/vp/admin need to start result computation first')
        return redirect('result_template')
    # Calculate Result table data ends here

    # Anual report computation
    anualstudent = []
    anualrecord = []
    if term == 3:
        getallstudent = RegisteredSubjects.objects.filter(group=uugroup,subject=uusub,arm=uuarm,active=1)
        liststudent = getallstudent.values_list('registration_number','group','arm')
        avggrade = ''
        avgremark = ''
        annual_totalindex = 0
        for student in liststudent:
            stud = list(student)
            print(stud)
            # 1st term CA
            try:
                ca11 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=1,session=session,subject=uusub
                ).CA1
                if ca11 == None:
                    ca11 = 0
            except Record.DoesNotExist:
                ca11 = 0

            try:
                ca12 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=1,session=session,subject=uusub
                ).CA2
                if ca12 == None:
                    ca12 = 0
            except Record.DoesNotExist:
                ca12 = 0

            # try:
            #     ca13 = Record.objects.get(
            #         student=stud[0],group=stud[1],arm=stud[2],term=1,session=session,subject=uusub
            #     )
            #     if ca13 == None:
            #         ca13 = 0
            # except Record.DoesNotExist:
            #     ca13=0

            # 2nd term CA
            try:
                ca21 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=2,session=session,subject=uusub
                ).CA1
                if ca21 == None:
                    ca21 = 0
            except Record.DoesNotExist:
                ca21=0

            try:
                ca22 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=2,session=session,subject=uusub
                ).CA2
                if ca22 == None:
                    ca22 = 0
            except Record.DoesNotExist:
                ca22=0

            # try:
            #     ca23 = Record.objects.get(
            #         student=stud[0],group=stud[1],arm=stud[2],term=2,session=session,subject=uusub
            #     )
            #     if ca23 == None:
            #         ca23 = 0
            # except Record.DoesNotExist:
            #     ca23=0

            # 3rd term CA
            try:
                ca31 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=3,session=session,subject=uusub
                ).CA1
                if ca31 == None:
                    ca31 = 0
            except Record.DoesNotExist:
                ca31=0

            try:
                ca32 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=3,session=session,subject=uusub
                ).CA2
                if ca32 == None:
                    ca32 = 0
            except Record.DoesNotExist:
                ca32=0

            # try:
            #     ca33 = Record.objects.get(
            #         student=stud[0],group=stud[1],arm=stud[2],term=3,session=session,subject=uusub
            #     )
            #     if ca33 == None:
            #         ca33 = 0
            # except Record.DoesNotExist:
            #     ca33=0

            # # 1st term project
            # try:
            #     project11 = Record.objects.get(
            #         student=stud[0],group=stud[1],arm=stud[2],term=1,session=session,subject=uusub
            #     )
            #     if project11 == None:
            #         project11 = 0
            # except Record.DoesNotExist:
            #     project11=0

            # # 2nd term project
            # try:
            #     project21 = Record.objects.get(
            #         student=stud[0],group=stud[1],arm=stud[2],term=2,session=session,subject=uusub
            #     )
            #     if project21 == None:
            #         project21 = 0
            # except Record.DoesNotExist:
            #     project21=0

            # # 3rd term project
            # try:
            #     project31 = Record.objects.get(
            #         student=stud[0],group=stud[1],arm=stud[2],term=3,session=session,subject=uusub
            #     )
            #     if project31 == None:
            #         project31 = 0
            # except Record.DoesNotExist:
            #     project31=0

            # # 1st term test
            # try:
            #     test11 = Record.objects.get(
            #         student=stud[0],group=stud[1],arm=stud[2],term=1,session=session,subject=uusub
            #     )
            #     if test11 == None:
            #         test11 = 0
            # except Record.DoesNotExist:
            #     test11=0

            # # 2nd term test
            # try:
            #     test21 = Record.objects.get(
            #         student=stud[0],group=stud[1],arm=stud[2],term=2,session=session,subject=uusub
            #     )
            #     if test21 == None:
            #         test21 = 0
            # except Record.DoesNotExist:
            #     test21=0

            # # 3rd term test
            # try:
            #     test31 = Record.objects.get(
            #         student=stud[0],group=stud[1],arm=stud[2],term=3,session=session,subject=uusub
            #     )
            #     if test31 == None:
            #         test31 = 0
            # except Record.DoesNotExist:
            #     test31=0

            # 1st term exam
            try:
                exam11 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=1,session=session,subject=uusub
                ).exam
                if exam11 == None:
                    exam11 = 0.0
            except Record.DoesNotExist:
                exam11=0

            # 2nd term exam
            try:
                exam21 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=2,session=session,subject=uusub
                ).exam
                if exam21 == None:
                    exam21 = 0.0
            except Record.DoesNotExist:
                exam21=0

            # 3rd term exam
            try:
                exam31 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=3,session=session,subject=uusub
                ).exam
                if exam31 == None:
                    exam31 = 0
            except Record.DoesNotExist:
                exam31=0

            # 1st term subject average
            try:
                subavg11 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=1,session=session,subject=uusub
                ).average
                if subavg11 == None:
                    subavg11 = 0
            except Record.DoesNotExist:
                subavg11=0

            # 2nd term subject average
            try:
                subavg21 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=2,session=session,subject=uusub
                ).average
                if subavg21 == None:
                    subavg21 = 0
            except Record.DoesNotExist:
                subavg21=0

            # 3rd term subject average
            try:
                subavg31 = Record.objects.get(
                    student=stud[0],group=stud[1],arm=stud[2],term=3,session=session,subject=uusub
                ).average
                if subavg31 == None:
                    subavg31 = 0
            except Record.DoesNotExist:
                subavg31=0

            # Average CA

            # avgca1 = (Decimal(ca11.get('CA1__sum'))+Decimal(ca12.get('CA2__sum'))+Decimal(ca13.get('CA3__sum')))
            # avgca2 = (Decimal(ca21.get('CA1__sum'))+Decimal(ca22.get('CA2__sum'))+Decimal(ca23.get('CA3__sum')))
            # avgca3 = (Decimal(ca31.get('CA1__sum'))+Decimal(ca32.get('CA2__sum'))+Decimal(ca33.get('CA3__sum')))

            avgca1 = ca11+ca12+exam11
            avgca2 = ca21+ca22+exam21
            avgca3 = ca31+ca32+exam31

            # # Average project
            # avgproject = project11.project+project21.project+project31.project

            # # Average test
            # avgtest = test11.test+test21.test+test31.test

            # Average exam
            avgexam = exam11+exam21+exam31

            # Average subject average
            avgsubjectavg = subavg11+subavg21+subavg31

            # Average total
            avgtotal = (avgca1+avgca2+avgca3)

            if int(avgtotal/3) >= 70:
                avggrade = 'A'
                avgremark = 'Excellent'
            elif int(avgtotal/3) >= 55:
                avggrade = 'C'
                avgremark = 'Credit'
            elif int(avgtotal/3) >= 40:
                avggrade = 'P'
                avgremark = 'Pass'
            else:
                avggrade = 'F'
                avgremark = 'Fail'

            # IMPORTANT: check if the index of total match totalindex variable
            anualunitstudent = list((avgca1,avgca2,avgca3,avgexam,uugroup,uuarm,stud[0],avgtotal,uusub,4))
            anualstudent.append(anualunitstudent)
            
            annual_totalindex = int(anualunitstudent.index(avgtotal))

            record = Record(
            CA1=avgca1,CA2=avgca2,CA3=avgca3,average=avgsubjectavg/3,annaul_average=avgtotal/3,
            group=stud[1],subject=uusub,term=4,arm=stud[2],total=avgtotal,grade=avggrade,remark=avgremark,
            student=stud[0],session=session,year=year,added_by=request.user)

            anualrecord.append(record)
        Record.objects.bulk_create(anualrecord)
        # Calculate anual position here
        spa = sorted(anualstudent, key=itemgetter(annual_totalindex), reverse=True)
        print(spa)
        prevpos = 0
        pos = 0
        result_counter = 0
        averageindex = 0
        same = 1
        position=0
        for i in spa:
            fixpos = Record.objects.filter(group=i[4],arm=i[5],student=i[6],subject=i[8],term=4,session=session)
            print(fixpos)
            if i[annual_totalindex]  == prevpos:
                prevpos = i[averageindex]
                same += 1
                pos = result_counter
                if (pos == 1)or(pos == 21)or(pos == 31)or(pos == 41)or(pos == 51)or(pos == 61)or(pos == 71)or(pos == 81)or(pos == 91):
                    position = str(pos) + 'st'
                elif (pos == 2)or(pos == 22)or(pos == 32)or(pos == 42)or(pos == 52)or(pos == 62)or(pos == 72)or(pos == 82)or(pos == 92):
                    position = str(pos) + 'nd'
                elif (pos == 3)or(pos == 23)or(pos == 33)or(pos == 43)or(pos == 53)or(pos == 63)or(pos == 73)or(pos == 83)or(pos == 93):
                    position = str(pos) + 'rd'
                else:
                    position = str(pos) + 'th'
            else:
                result_counter += same
                pos = result_counter
                prevpos = i[averageindex]
                if (pos == 1)or(pos == 21)or(pos == 31)or(pos == 41)or(pos == 51)or(pos == 61)or(pos == 71)or(pos == 81)or(pos == 91):
                    position = str(pos) + 'st'
                elif (pos == 2)or(pos == 22)or(pos == 32)or(pos == 42)or(pos == 52)or(pos == 62)or(pos == 72)or(pos == 82)or(pos == 92):
                    position = str(pos) + 'nd'
                elif (pos == 3)or(pos == 23)or(pos == 33)or(pos == 43)or(pos == 53)or(pos == 63)or(pos == 73)or(pos == 83)or(pos == 93):
                    position = str(pos) + 'rd'
                else:
                    position = str(pos) + 'th'
                same = 1
            fixpos.update(position=position)
        # Anual position calculation ends here
    messages.success(request, 'Added successful')
    return redirect('assessment')