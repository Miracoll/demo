from django.contrib import messages
from django.shortcuts import redirect
from random import randrange
from student.models import Student
from configuration.models import Session, Role, Config, Category,RegisteredSubjects
from staff.models import Staff
import random
import string

# Generate student registration number
def generateStudentRegNumber(cat):
    session = Session.objects.get(active=1)
    config = Config.objects.get(id=1)
    student_len = len(Student.objects.filter(session=session))
    year = str(session.year)
    serial = int(student_len) + 1
    serial_str = str(serial)
    getcat = Category.objects.get(category=cat)
    reg = f'{config.school_initial}{year[2:]}{getcat.code}{serial_str.zfill(3)}'
    return reg

# Generate staff registration number
def generateStaffRegNumber(role):
    config = Config.objects.get(id=1)
    role = Role.objects.get(role=role)
    staff = len(Staff.objects.all())
    serial = int(staff) + 1
    serial_str = str(serial)
    reg = f'{config.school_initial}{role.code}{serial_str.zfill(3)}'
    return reg

# Add course
def registerSeniorStudentCourse(request,student,registered_len,session,term,subject,redirect_to):
    # Check for number of subjects added
    if registered_len >= 10:
        messages.error(request, 'You have reach the maximum limit')
        return redirect(redirect_to)
    
    # Check for existing subjects
    if RegisteredSubjects.objects.filter(student=student.registration_number,subject=subject.subject,session=session.session).exists():
        messages.error(request, 'Subject already exist')
        return redirect(redirect_to)
    course = RegisteredSubjects.objects.create(
        student=student.registration_number,subject=subject.subject,group=student.group,arm=student.arm,category='senior',
        added_by=request.user,last_name=student.last_name,first_name=student.first_name,session=session.session
    )
    messages.success(request, 'Added')
    return course

#Remove course
def removeStudentCourse(request,ref):
    course = RegisteredSubjects.objects.filter(ref=ref)
    course.delete()
    messages.success(request, 'Removed')
    return course

def generatePassword(length=7, use_uppercase=False, use_numbers=True, use_symbols=False):
    # Define character pools based on user's choices
    character_pool = string.ascii_lowercase
    if use_uppercase:
        character_pool += string.ascii_uppercase
    if use_numbers:
        character_pool += string.digits
    if use_symbols:
        character_pool += string.punctuation

    # Ensure the character pool is not empty
    if not character_pool:
        raise ValueError("At least one character type must be selected")

    # Generate a random password
    password = ''.join(random.choice(character_pool) for _ in range(length))
    return password