from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from .models import *
from django.contrib.auth.models import User, auth
from django.views import generic
from .forms import CreateNewForm
from django.core.exceptions import ObjectDoesNotExist
from datetime import date,timedelta
from django.urls import reverse
from calendar import monthrange
from collections import defaultdict

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def attendanceUpdate(subs):
    for s in subs:
        s.attendance = s.calcPercentage
        s.lec_to_skip = s.calcLecNeeded
        s.lec_total = s.lec_present + s.lec_absent
        s.percentage_bar = int(s.attendance)
        s.save()
        submonths = SubjectMonth.objects.filter(subject = s)
        for sm in submonths:
            sm.attendance = sm.calcPercentage
            sm.lec_to_skip = sm.calcLecNeeded
            sm.lec_total = sm.lec_present + sm.lec_absent
            sm.percentage_bar = int(sm.attendance)
            sm.save()

def index(request):

    sems = Semester.objects.all()

    return render(request,"timetable.html",{'sems': sems})

def subinfo(request):

    username = None
    if request.user.is_authenticated:
        username = request.user.get_username
        sems = request.user.semester.all()
        subs = Subject.objects.none()
        for s in sems:
            subs = subs|Subject.objects.filter(semester=s)
        attendanceUpdate(subs)


        return render(request,"stats.html",{'sems':sems,'subs':subs,'username':username,
            'username': request.user.get_username,})
    else:
        return HttpResponseRedirect(reverse('accounts:user_login'))

def timetable(request):
    
    username = None
    if request.user.is_authenticated:
        username = request.user.get_username
        day_list = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        days = request.user.day.all()
        sems = request.user.semester.all()
        return render(request,"events.1.html",{'days':days,'sems': sems,'username':username,'dl':day_list})
    else:
        return HttpResponseRedirect("../../accounts/login")


def create(request):
    if request.method=='POST':
        form = CreateNewForm(request.POST)

        if form.is_valid():
            sem_name = form.cleaned_data['sem_name']
            subjects_list = form.cleaned_data['Subjects'].split(',')
            '''try request.user.semester.get(name=sem_name):
                s = request.user.semester.get(name=sem_name)
            except ObjectDoesNotExists:
                s = Semester(name=sem_name)
                s.save()
                request.user.semester.add(s)
            finally: 
                for sub in subjects_list:
                subject = Subject(name=sub,semester=s)
                subject.save()'''
            if request.user.semester.filter(name=sem_name).exists():
                s = request.user.semester.filter(name=sem_name)[0]
            else:
                s = Semester(name=sem_name)
                s.save()
                request.user.semester.add(s)
            for sub in subjects_list:
                subject = Subject(name=sub,semester=s)
                subject.save()

        return HttpResponseRedirect("/semesters/")
    else:
        form = CreateNewForm()
        return render(request,"create.html",{'form':form})

def add_sem(request):
    if request.method == 'POST':
        sem_name = request.POST['sem_name']
        start_date = request.POST['start_date']
        last_date = request.POST['last_date']
        min_att = request.POST['min_att']
        sem = Semester(name=sem_name,user=request.user,last_date=last_date,start_date=start_date,min_attendance=min_att)
        sem.save()

        return HttpResponseRedirect(reverse('seminfo:add_sub'))

    else:
        return render(request,"add_sem.html", {'username': request.user.get_username})

def add_sub(request):
    username = None
    if request.user.is_authenticated:
        if request.method=='POST':
            if 'add' in request.POST:
                subject_name = request.POST['subject_name']
                sub = Subject(name=subject_name,semester=request.user.semester.last())
                sub.save()
                return HttpResponseRedirect(reverse('seminfo:add_sub'))
            if 'next' in request.POST:
                return HttpResponseRedirect(reverse('seminfo:create_tt'))
                
        username = request.user.get_username
        sem = request.user.semester.last()
        sb = Subject.objects.filter(semester=sem)
        
        return render(request,"add_sub.html",{'sem':sem,'sb':sb,'username':username,
            'username': request.user.get_username,})
    else:
        return HttpResponseRedirect(reverse('accounts:user_login'))

def delete_subject(request,id):
    Subject.objects.filter(id=id).delete()
    return HttpResponseRedirect(reverse('seminfo:add_sub'))

def create_tt(request):
    if request.user.is_authenticated:
        request.user.get_username
        day_list = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        nl = list(map(str,list(range(1,11))))
        sem = request.user.semester.last()
        subs= Subject.objects.filter(semester=sem)
        username = None
        if request.method=="POST":
            for d in day_list:
                for n in nl:
                    p_id = request.POST[d+"_"+n]
                    if p_id!="":
                        period = Subject.objects.filter(id=p_id).first()
                        day = Day(name=d, user=request.user,semester=sem,period=period)
                        day.save()
            return HttpResponseRedirect(reverse('seminfo:seminfo',kwargs={'id':sem.id}))
        return render(request,"add_tt.html",{'sem': sem,'username':username,'dl':day_list,'subs':subs, 'nl':nl,
            'username': request.user.get_username,})
    else:
        return HttpResponseRedirect(reverse('accounts:user_login'))

def calendarToday(request):
    if request.user.is_authenticated:
        today = date.today()
        d1 = today.strftime("%d")
        d2 = today.strftime("%m")
        d3 = today.strftime("%Y")
        return HttpResponseRedirect(reverse('seminfo:calendar',kwargs={'date':int(d1),'month':int(d2),'year':(d3)}))
    else:
        return HttpResponseRedirect(reverse('accounts:user_login'))
 
def Calendar(request,date,month,year):
    if request.method=="POST":

        if 'addlec' in request.POST:
            sub_id = request.POST['new_lec']
            day = request.POST['lec_date']
            subject = Subject.objects.filter(id=sub_id)[0]
            semester = subject.semester
            new_lec = Lecture(semester=semester,subject=subject,date=day)
            new_lec.save()
            return HttpResponseRedirect(reverse('seminfo:calendar',kwargs={'date':date,'month':month,'year':year}))
        else:
            status = request.POST['status']
            lec_id = request.POST['id']
            l = Lecture.objects.filter(id=lec_id)[0]

            date = l.date.day
            month = l.date.month
            year = l.date.year

            subjectmonth = SubjectMonth.objects.filter(subject = l.subject).filter(month=l.date.strftime("%B"))[0]
            l.update(status,subjectmonth)
            l.status = status
            l.save()
            subjectmonth.save()
            attendanceUpdate(Subject.objects.filter(id=l.subject.id))
            return HttpResponseRedirect(reverse('seminfo:calendar',kwargs={'date':date,'month':month,'year':year}))

    else:
        #monthTag = ['January','February','March','April','May','June','July','August','September','October','November','December']
        user = request.user
        day_string = date+"-"+month+"-"+year
        day_date = datetime.datetime.strptime(day_string,"%d-%m-%Y")
        d = datetime.date(int(year),int(month),int(date)).strftime("%d")
        m = datetime.date(int(year),int(month),int(date)).strftime("%m")
        y = datetime.date(int(year),int(month),int(date)).strftime("%Y")
        today = datetime.datetime.now()
        future = day_date > today
        weekday_start = monthrange(int(year),int(month))[0]
        no_of_days = monthrange(int(year),int(month))[1]
        gaps = list(range(0,weekday_start))
        dates = list(range(1,no_of_days+1))
        monthName = datetime.date(int(year),int(month),int(date)).strftime("%B")
        sem = request.user.semester.filter(user=request.user)
        lectures = Lecture.objects.none()
        sems = Semester.objects.filter(start_date__lte=day_date).filter(last_date__gte=day_date).filter(user=request.user)
        for s in sems:
            lectures = lectures|Lecture.objects.filter(date=day_date).filter(semester=s)
        subs = Subject.objects.none()
        for s in sems:
            subs = subs|Subject.objects.filter(semester=s)
        myrange = list(range(0,7))
        day_no = day_date.weekday()
        context = {
            'user':request.user,
            'sem':sem,
            'lectures': lectures,
            'date':int(date),
            'month':int(month),
            'year':int(year),
            'day_date':day_date,
            'gaps':gaps,
            'dates':dates,
            'today_day':today.day,
            'today_month':today.month,
            'today_year':today.year,
            'month_name':monthName,
            'subs':subs,
            'd':d,
            'm':m,
            'y':y,
            'range':myrange,
            'day_no':day_no,
            'future':future,
            'username': request.user.get_username,
        }
        return render(request,"calendar.html",context)

def stats(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.get_username
        sems = request.user.semester.all()
        current_sems = Semester.objects.filter(start_date__lte=date.today()).filter(last_date__gte=date.today()).filter(user=request.user)
        return render(request,"stats-list.html",{'sems':sems,'username':username,'current_sems':current_sems,
            'username': request.user.get_username,})
    else:
        return HttpResponseRedirect(reverse('accounts:user_login'))

def statsDetail(request,id,category):
    username = None
    if request.user.is_authenticated:

        if request.method=='POST':
            category = request.POST['category']
            return HttpResponseRedirect(reverse('seminfo:statsDetail',kwargs={'id':id,'category':category}))

        username = request.user.get_username
        sem = Semester.objects.filter(id=id)[0]
        sem_months = []
        for dt in daterange(sem.start_date, sem.last_date):
            month = dt.strftime("%B")
            if month not in sem_months:
                sem_months.append(month)
        present = 0
        absent = 0
        cancelled = 0
        
        subs = Subject.objects.filter(semester=sem)
        attendanceUpdate(subs)
        for s in subs:
            present = present + s.lec_present
            absent = absent + s.lec_absent
            cancelled = cancelled + s.lec_cancelled

        sum = present + absent
        try:
            percent = truncate(present/sum*100,1)
        except ZeroDivisionError:
            percent = 0

        percentInt = int(percent)

        if category=="all-time":
            return render(request,"stats.html",{'sem':sem,'subs':subs,'username':username,'present':present,'sum':sum,'percent':percent,'cancelled':cancelled,'percentInt':percentInt,'sem_months':sem_months,'category':category,
            'username': request.user.get_username,})
            
        else:
            today = date.today()
            current_month = today.strftime("%B")
            month = category
            submonths = SubjectMonth.objects.filter(semester=sem).filter(month=month)
            return render(request,"stats.html",{'sem':sem,'submonths':submonths,'username':username,'present':present,'sum':sum,'percent':percent,'cancelled':cancelled,'percentInt':percentInt,'sem_months':sem_months,'category':category,'subs':subs,'current_month':current_month,
            'username': request.user.get_username,})
    else:
        return HttpResponseRedirect(reverse('accounts:user_login'))

def sem(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.get_username
        sems = request.user.semester.all()
        current_sems = Semester.objects.filter(start_date__lte=date.today()).filter(last_date__gte=date.today()).filter(user=request.user)
        return render(request,"sem-list.html",{'sems':sems,'username':username,'current_sems':current_sems,
            'username': request.user.get_username,})
    else:
        return HttpResponseRedirect(reverse('accounts:user_login'))

def seminfo(request,id):
    username = None
    if request.user.is_authenticated:
        username = request.user.get_username
        sem = Semester.objects.filter(id=id)[0]
        subs = Subject.objects.filter(semester=sem)
        periods = Day.objects.filter(semester=sem)
        days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        return render(request,"sem.html",{'sem':sem,'subs':subs,'username':username,'days':days,'periods':periods,
            'username': request.user.get_username,})
    else:
        return HttpResponseRedirect(reverse('accounts:user_login'))

def scheduleDefault(request):
    username = None
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse( 'seminfo:schedule', kwargs = {'day':'today'}))
    else:
        return HttpResponseRedirect(reverse('accounts:user_login'))

def schedule(request,day):
    username = None
    if request.user.is_authenticated:
        if request.method == "POST":
            day = request.POST['day']
            return HttpResponseRedirect(reverse('seminfo:schedule',kwargs={'day':day}))

        sems = request.user.semester.all()
        lectures = Lecture.objects.none()
        if day=="today":
            date = datetime.date.today()
        else:
            date = datetime.date.today() + datetime.timedelta(days=1)
        for sem in sems:
                lectures = lectures | Lecture.objects.filter(semester=sem).filter(date=date)
        subjectmonth = SubjectMonth.objects.none()
        for lecture in lectures:
            month = date.strftime("%B")
            subjectmonth = subjectmonth | SubjectMonth.objects.filter(subject=lecture.subject).filter(month=month)
        
        schedule = []
        
        for sub in subjectmonth:
            lec_to_skip = sub.lec_to_skip
            for lec in lectures:  
                if(lec.subject==sub.subject):
                    schedule.append({lec.subject.name:lec_to_skip})
                    lec_to_skip = lec_to_skip - 1;

        context = {
            'schedule':schedule,
            'day':day,
            'submonths':subjectmonth,
            'username': request.user.get_username,
        }
        return render(request,"schedule.html",context)

    else:
        return HttpResponseRedirect(reverse('accounts:user_login'))


def about(request):
    return render(request,"about.html")