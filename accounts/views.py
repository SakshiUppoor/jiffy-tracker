from django.shortcuts import render,redirect,HttpResponseRedirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.urls import reverse
# Create your views here.

def register(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1==password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return HttpResponseRedirect(reverse('accounts:register'))
            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return HttpResponseRedirect(reverse('accounts:register'))
            else:
                user = User.objects.create_user(username=username,email=email,password=password1)
                user.save();
                return HttpResponseRedirect(reverse('seminfo:sem'))
        else:
            messages.info(request,'Password not matching')
            return HttpResponseRedirect(reverse('accounts:register'))
        return redirect('../')

    else:
        return render(request,'join.html')

def user_login(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect(reverse('seminfo:scheduleDefault'))
        else:
            messages.info(request,'Username or password incorrect')
            return redirect('accounts:user_login')
    else:
        return render(request,'login.html')


def user_logout(request):
    auth.logout(request)
    return redirect(reverse('accounts:user_login'))