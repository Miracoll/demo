from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from .forms import HostelForm
from .models import Bedspace, Floor, Hostel, Occupant, Room, Paid_Occupant
from payment.models import Payment
from configuration.models import Config
from student.models import Student
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from lms.decorators import allowed_users
from configuration.models import Term,Session

# Create your views here.
def nohostel(request):
    return render(request,'hostel/no_hostel.html')

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','hostel-manager'])
def createhostel(request):
    if not Config.objects.get(id=1).use_hostel:
        return redirect('no_hostel')
    form = HostelForm()
    if request.method == 'POST':
        form = HostelForm(request.POST, request.FILES)
        if form.is_valid():
            # Hostel creation start
            name = request.POST.get('hostel_name').lower().replace(' ','_')
            if Hostel.objects.filter(hostel_name=name).exists():
                messages.warning(request, f'{name} already exist')
                return redirect('createhostel')
            hostel = form.save(commit=False)
            hostel.hostel_name = name
            hostel.added_by = request.user
            hostel.save()
            # Hostel creation end

            # Hostel floor creation start
            floor = int(request.POST.get('floor_number'))
            for i in range(floor):
                getfloor = 'floor '+ str(i)
                Floor.objects.create(
                    floor=getfloor,hostel_id=Hostel.objects.get(hostel_name=name), added_by=request.user
                )

            messages.success(request, f'{name} created')
            return redirect('createhostel')
    context = {'form':form}
    return render(request, 'hostel/createhostel.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','hostel-manager'])
def payment_setup(request):
    if not Config.objects.get(id=1).use_hostel:
        return redirect('no_hostel')
    hostel = Hostel.objects.filter(active=1)
    if 'pay' in request.POST:
        pay = request.POST.get('payment')
        amount = request.POST.get('amount')
        Payment.objects.create(payment=pay,amount=amount,category='hostel',added_by=request.user)
        messages.success(request, 'Payment added')
        return redirect('paymentsetup')
    context = {'hostel':hostel}
    return render(request,'hostel/hostelpayment.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','hostel-manager'])
def hostelfloor(request):
    if not Config.objects.get(id=1).use_hostel:
        return redirect('no_hostel')
    floor = Floor.objects.filter(active=1)
    if request.method == 'POST':
        getfloor = request.POST.get('floor')
        gethostel = request.POST.get('hostel')
        getroom = int(request.POST.get('room'))

        hostel = Hostel.objects.get(hostel_name=gethostel)

        if Floor.objects.get(hostel_id=hostel,floor=getfloor).lock:
            messages.warning(request, 'Need principal permission to proceed')
            return redirect('hostelfloor')

        Floor.objects.filter(hostel_id=hostel,floor=getfloor).update(number_of_room=getroom, last_updated_by=request.user.username, lock=True)
        fixfloor = Floor.objects.get(floor=getfloor,hostel_id=hostel)
        for i in range(getroom):
            fixroom = 'room '+ str(i)
            Room.objects.create(
                room=fixroom, floor=fixfloor, added_by=request.user
            )
        messages.success(request, 'Floor updated')
        return redirect('hostelfloor')
    context = {'floor':floor}
    return render(request, 'hostel/hostelfloor.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','principal','vice-principal','hostel-manager'])
def hostelroom(request):
    if not Config.objects.get(id=1).use_hostel:
        return redirect('no_hostel')
    room = Room.objects.filter(active=1)
    if request.method == 'POST':
        getroom = request.POST.get('room')
        getfloor = request.POST.get('floor')
        gethostel = request.POST.get('hostel')
        getoccupant = int(request.POST.get('occupant'))

        if Hostel.objects.filter(hostel_name=gethostel).exists():
            hostel = Hostel.objects.get(hostel_name=gethostel)
        else:
            messages.error(request, 'Self destruction activated')
            User.objects.filter(username=request.user.username).update(is_active=0)
            return redirect('logout')

        floor = Floor.objects.get(floor=getfloor, hostel_id=hostel)

        if Room.objects.get(room=getroom,floor=floor).lock:
            messages.warning(request, 'Need principal permission to proceed')
            return redirect('hostelroom')

        Room.objects.filter(room=getroom,floor=floor).update(occupant_per_room=getoccupant, space_available=getoccupant, last_updated_by=request.user.username, lock=True)
        fixroom = Room.objects.get(room=getroom,floor=floor)

        for i in range(getoccupant):
            fixbedspace = 'bedspace '+ str(i)
            Bedspace.objects.create(
                bedspace=fixbedspace, room=fixroom, added_by=request.user,
                hostel=hostel, floor=floor
            )
        messages.success(request, 'Room updated')
        return redirect('hostelroom')
    context = {'room':room}
    return render(request, 'hostel/hostelroom.html', context)

def hostelbedspace(request):
    if not Config.objects.get(id=1).use_hostel:
        return redirect('no_hostel')
    bedspace = Bedspace.objects.filter(active=1)
    context = {'bedspace':bedspace}
    return render(request, 'hostel/hostelbedspace.html', context)

def assignhostel(request):
    if not Config.objects.get(id=1).use_hostel:
        return redirect('no_hostel')
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    if request.method == 'POST':
        reg = request.POST.get('reg')
        if not User.objects.filter(username=reg).exists():
            messages.warning(request, 'Sorry i do not know the person')
            return redirect('assignhostel')
        if Occupant.objects.filter(student=reg, year=year,session=session,term=term).exists():
            identity = User.objects.get(username=reg)
            messages.warning(request, f'I have already done allocation for {identity.last_name} {identity.first_name}')
            return redirect('assignhostel')
        if Paid_Occupant.objects.filter(occupant=reg, year=year,session=session,term=term).exists():
            getid = Paid_Occupant.objects.get(occupant=reg, year=year,session=session,term=term).id
            return redirect('viewhostel',getid)
        else:
            messages.warning(request, "Sorry i can't find this identity")
            return redirect('assignhostel')
    return render(request, 'hostel/assignhostel.html')

def viewhostel(request, pk):
    if not Config.objects.get(id=1).use_hostel:
        return redirect('no_hostel')
    get_id = Paid_Occupant.objects.get(id=pk).id
    get_hostel_name = Paid_Occupant.objects.get(id=pk).hostel
    get_hostel_id = Hostel.objects.get(hostel_name=get_hostel_name).ref
    hostel = Hostel.objects.get(ref=get_hostel_id)
    bedspace = Bedspace.objects.filter(hostel=hostel, lock=0, active = 1)
    context = {'bedspace':bedspace,'hostel':hostel,'id':get_id}
    return render(request, 'hostel/viewhostel.html', context)

def assign2occupant(request, pk, regg):
    if not Config.objects.get(id=1).use_hostel:
        return redirect('no_hostel')
    confirm_occupant = Paid_Occupant.objects.get(id=regg).occupant
    bedspace = Bedspace.objects.filter(ref=pk)
    hostel = Bedspace.objects.get(ref=pk).hostel
    getbedspace = Bedspace.objects.get(ref=pk)
    floor = Bedspace.objects.get(ref=pk).floor
    term = Term.objects.get(active=1).term
    session = Session.objects.get(active=1).session
    year = Session.objects.get(active=1).year
    if request.method == 'POST':
        occupant = request.POST.get('occupant')
        if occupant != confirm_occupant:
            # User.objects.filter(username=request.user.username).update(is_active=0)
            messages.warning(request, 'Cross check id/registration number')
            return redirect('assign2occupant', pk, regg)
        # Arithemetic
        room = getbedspace.room
        get_occupied1 = int(room.occupied)
        Room.objects.filter(id=room.id,active=1,lock=0).update(occupied=get_occupied1+1)
        get_occupied2 = int(room.occupied)
        get_space = room.occupant_per_room - get_occupied2
        Room.objects.filter(id=room.id,active=1,lock=0).update(
            space_available = get_space-1
        )

        # Lock room if filled up
        if room.space_available == 0 and room.occupied == room.occupant_per_room:
            Room.objects.filter(floor=floor,active=1,lock=0).update(lock=True,available=False)

        # Lock bedspace if taken
        bedspace.update(lock=1,occupied=1)

        # Lock floor if filled up
        if not Room.objects.filter(floor_id=floor.id,lock=0).exists():
            Floor.objects.filter(id=floor.id).update(lock=1)

        # Lock hostel if filled up
        if not Floor.objects.filter(hostel_id=floor.id,lock=0).exists():
            Floor.objects.filter(id=floor.id).update(lock=1)
        
        # Add to occupant table
        amount = Payment.objects.get(payment=hostel.hostel_name).first_install
        Occupant.objects.create(
            student=occupant,amount_paid=amount,bedspace=getbedspace,year=year,session=session,term=term,
            created_by=request.user
        )
        getprint = Occupant.objects.get(year=year,session=session,term=term,student=occupant).ref
        messages.success(request, 'Allocation successful')
        return redirect('hostelprintout',getprint)
    context = {'bedspace':bedspace}
    return render(request, 'hostel/assignoccupant.html', context)

def hostelprintout(request,pk):
    if not Config.objects.get(id=1).use_hostel:
        return redirect('no_hostel')
    school_name = Config.objects.get(id=1).school_name
    get_student = Occupant.objects.get(ref=pk).student
    student = Student.objects.filter(registration_number=get_student)
    hostel = Occupant.objects.filter(ref=pk)
    context = {'hostel':hostel,'name':school_name,'student':student}
    return render(request, 'hostel/printout.html',context)