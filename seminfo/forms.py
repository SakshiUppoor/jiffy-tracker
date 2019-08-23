from django import forms
import datetime

class CreateNewForm(forms.Form):
    sem_name = forms.CharField(max_length=20)
    Subjects = forms.CharField(max_length=20)
    start_date = forms.DateField()
    last_date = forms.DateField()
    min_att = forms.IntegerField()

class CreateNewTT(forms.Form):
    pass