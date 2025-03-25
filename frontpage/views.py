from django.shortcuts import render
from django.views.generic import View
from .functions import get_ordinal_suffix, get_top_students
from student.models import Student

# Create your views here.

class Home(View):
    template_name = 'frontpage/index.html'
    def get(self,request):
        students = []
        top_students = get_top_students()

        for group_students in top_students.values():  # Iterate over groups
            pos = 0
            for result in group_students:  # Iterate over top 3 students
                pos += 1

                try:
                    student = Student.objects.get(registration_number=result.student)  # Get student instance
                except Student.DoesNotExist:
                    print(f"Student with reg {result.student} not found.")
                    continue  # Skip this student if not found

                # Create a new dictionary for each student
                new_dict = {
                    'reg': student.registration_number,
                    'passport': student.passport.url if student.passport else None,
                    'group': result.group,
                    'lastname': student.last_name,
                    'firstname' :student.first_name,
                    'pos': pos,
                    'suffix': get_ordinal_suffix(pos),
                }

                students.append(new_dict)
                print(f'Added {result.student} of {new_dict["group"]} with position {new_dict["pos"]}')

        print("Final student list:", students)

        context = {'results':students}
        return render(request,self.template_name, context)

class About(View):
    template_name = 'frontpage/about.html'
    def get(self,request):
        return render(request,self.template_name)

class Contact(View):
    template_name = 'frontpage/contact.html'
    def get(self,request):
        return render(request,self.template_name)
    
class Admission(View):
    template_name = 'frontpage/admission.html'
    def get(self,request):
        return render(request,self.template_name)
    
class Newsletter(View):
    template_name = 'frontpage/newsletter.html'
    def get(self, request):
        return render(request,self.template_name)