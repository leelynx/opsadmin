# -*- coding: utf-8 -*-
from django.contrib import auth
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

@login_required(login_url='/login')
def auth_forbidden(request):
    return render(request, 'error/403.html')


def auth_login(request):
    redirect_field_name = 'next'
    redirect_path = request.GET.get(redirect_field_name, '/')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = auth.authenticate(username=username, password=password)
        if user is not None: 
            if user.is_active:
                auth.login(request, user)
                request.session['name'] = user.get_name()
                redirect_path = request.POST.get(redirect_field_name, redirect_path)
                
                if user.role == 'SU':
                    request.session['role_id'] = 0
                elif user.role == 'AM':
                    request.session['role_id'] = 1
                else:
                    request.session['role_id'] = 2
                return HttpResponseRedirect(redirect_path)
            else:
                error = 'User account is not activated'
        else:
            error = 'Please enter the correct username and password. Note that both fields may be case-sensitive.'
    return render(request, 'login.html', locals())

@login_required(login_url='/login')
def auth_logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))

@login_required(login_url='/login')
def change_password(request):
    if request.method == "POST":
        username = request.user.username
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')
        user = auth.authenticate(username=username, password=old_password)
        if user is not None and user.is_active:
            if new_password == confirm_pass:
                user.set_password(new_password)
                user.save()
                msg = u'密码修改成功'
            else:
                error = u'两次输入新密码不一致'
        else:
            error = u'旧密码错误'
    
    return render(request, 'change_password.html', locals())
    