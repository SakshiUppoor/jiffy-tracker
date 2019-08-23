from django.db import models
from django.contrib.auth.models import User
import datetime
from datetime import timedelta,date
import os
from django.db.models.signals import post_save
from django.dispatch import receiver

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

# Create your models here.
class Semester(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,related_name="semester")
    name = models.CharField(max_length=20)
    #created_by = user
    start_date = models.DateField(default=datetime.date.today)
    last_date = models.DateField(default=datetime.date.today)
    min_attendance = models.IntegerField(default=75)  

    def __str__(self):
        return self.name
    
class Subject(models.Model):

    name = models.CharField(max_length=100)
    lec_present = models.IntegerField(default = 0)
    lec_absent = models.IntegerField(default = 0)
    lec_cancelled = models.IntegerField(default = 0)
    lec_total  = models.IntegerField(default = 0)
    attendance = models.FloatField(default = 0)
    lec_to_skip = models.IntegerField(default = 0)
    percentage_bar = models.IntegerField(default = 0)
    @property
    def calcPercentage(self):
        try:
            self.attendance = (self.lec_present)/(self.lec_present+self.lec_absent) * 100
        except ZeroDivisionError:
            self.attendance = 0
        self.attendance = truncate(self.attendance,2)
        return self.attendance

    @property
    def calcLecNeeded(self):
        p = self.attendance
        absent = self.lec_absent
        present = self.lec_present
        sum = self.lec_absent + self.lec_present
        min = self.semester.min_attendance
        needed = 0
        if p > min:
            while(p>=min):
                absent = absent + 1
                sum = absent + present
                p = present / sum * 100
                if p>=min:
                    needed = needed + 1
        elif p < min:
            while(p<=min):
                present = present + 1
                sum = absent + present
                p = present / sum *100
                if p <=min:
                    needed = needed + 1 

        self.lec_to_skip = needed
        return self.lec_to_skip

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + ', ' + self.semester.name
    
    
class SubjectMonth(models.Model):
    month = models.CharField(max_length=100)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default = '')
    lec_present = models.IntegerField(default = 0)
    lec_absent = models.IntegerField(default = 0)
    lec_cancelled = models.IntegerField(default = 0)
    lec_total  = models.IntegerField(default = 0)
    attendance = models.FloatField(default = 0)
    lec_to_skip = models.IntegerField(default = 0) 
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    percentage_bar = models.IntegerField(default = 0)
    @property
    def calcPercentage(self):
        try:
            self.attendance = (self.lec_present)/(self.lec_total) * 100

        except ZeroDivisionError:
            self.attendance = 0
        self.attendance = truncate(self.attendance,2)
        return self.attendance

    @property
    def calcLecNeeded(self):
        p = self.attendance
        absent = self.lec_absent
        present = self.lec_present
        sum = self.lec_absent + self.lec_present
        min = self.semester.min_attendance
        needed = 0
        if p > min:
            while(p>=min):
                absent = absent + 1
                sum = absent + present
                p = present / sum * 100
                if p>=min:
                    needed = needed + 1
        elif p < min:
            while(p<=min):
                present = present + 1
                sum = absent + present
                p = present / sum *100
                if p <=min:
                    needed = needed + 1 

        self.lec_to_skip = needed
        return self.lec_to_skip

    def __str__(self):
        return self.month + "-" + self.semester.name + "-" + self.subject.name
    


class Timetable(models.Model):

    semester = models.OneToOneField(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return self.semester
    

class Day(models.Model):
    name_choices = [
        ('Mon','Monday'),
        ('Tue','Tuesday'),
        ('Wed','Wednesday'),
        ('Thu','Thursday'),
        ('Fri','Friday'),
        ('Sat','Saturday'),
        ('Sun','Sunday')]
    name = models.CharField(max_length=3,choices = name_choices,default ='Mon')
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,related_name="day")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, default = '')
    period = models.ForeignKey(Subject,on_delete=models.CASCADE, null=True,related_name="period")

    def __str__(self):
        return self.name + '-' + self.semester.name

class Lecture(models.Model):
    date = models.DateField(default=datetime.date.today)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, default = '')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default = '')
    status_choices = [
        ('P','Present'),
        ('A','Absent'),
        ('C','Cancelled'),
        ('0','Off')
    ]
    status = models.CharField(max_length=1,choices = status_choices,default ='0')

    def update(self,post,subjectmonth):
        sub = self.subject
        pre = self.status
        if(pre!=post):
            if post=="P":
                sub.lec_present = sub.lec_present + 1
                subjectmonth.lec_present = subjectmonth.lec_present + 1
            elif post=="A":
                sub.lec_absent = sub.lec_absent + 1
                subjectmonth.lec_absent = subjectmonth.lec_absent + 1
            else:
                sub.lec_cancelled = sub.lec_cancelled + 1
                subjectmonth.lec_cancelled = subjectmonth.lec_cancelled + 1

            if pre=="P":
                sub.lec_present = sub.lec_present - 1
                subjectmonth.lec_present = subjectmonth.lec_present - 1
            elif pre=="A":
                sub.lec_absent = sub.lec_absent - 1
                subjectmonth.lec_absent = subjectmonth.lec_absent - 1
            elif pre=="C":
                sub.lec_cancelled = sub.lec_cancelled - 1
                subjectmonth.lec_cancelled = subjectmonth.lec_cancelled - 1
        sub.lec_total = sub.lec_present + sub.lec_absent
        subjectmonth.lec_total = subjectmonth.lec_present + subjectmonth.lec_absent
        sub.save()
        subjectmonth.save()

    def __str__(self):
        return self.subject.name

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

@receiver(post_save,sender=Subject)
def create_subject_months(sender, **kwargs):
    if kwargs['created']:
        start_date = kwargs.get('instance').semester.start_date
        stop_date = kwargs.get('instance').semester.last_date
        sem = kwargs.get('instance').semester
        
        for dt in daterange(start_date, stop_date):
            m = dt.strftime("%B");
            if SubjectMonth.objects.filter(subject=kwargs.get('instance')).filter(month=m).exists():
                pass
            else:
                newMonth = SubjectMonth.objects.create(subject=kwargs.get('instance'),month = m,semester=kwargs.get('instance').semester)

@receiver(post_save,sender=Day)
def create_lectures(sender, **kwargs):
    if kwargs['created']:
        start_date = kwargs.get('instance').semester.start_date
        stop_date = kwargs.get('instance').semester.last_date
        
        for dt in daterange(start_date, stop_date):
            if dt.strftime("%A")[:3]==kwargs.get('instance').name:
                lecture = Lecture.objects.create(semester=kwargs.get('instance').semester,subject=kwargs.get('instance').period,date=dt)

