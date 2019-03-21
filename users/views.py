# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from api.views import role_required
from users.models import User, UserGroup, PermRule
from cmdb.models import PlatformType
import logging, traceback
from django.http import HttpResponseRedirect
import datetime
from django.contrib.auth.models import Permission


@login_required(login_url='/login')
@role_required(role='super')
def user_group_add(request):
    """
       添加用户组
    """
    path1, path2 = u'用户权限管理', u'添加用户组'

    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        comment = request.POST.get('comment', '')
        get_group_name = UserGroup.objects.filter(name=group_name)
        if get_group_name:
            error = u"用户组: %s已存在" % group_name
        else:
            try:
                group = UserGroup(name=group_name, comment=comment)
                group.save()
                msg = u"用户组: %s添加成功" % group_name
            except Exception as err:
                error = u"用户组: %s添加失败, 错误原因: %s" % (group_name, err)
    
    return render(request, 'users/group_add.html',locals())

@login_required(login_url='/login')
@role_required(role='super')
def user_group_edit(request):
    """
       修改用户组
    """
    path1, path2 = u'用户权限管理', u'修改用户组'
    group_id = request.GET.get('id', '')
    group_list = UserGroup.objects.get(id=group_id)
    if request.method == 'POST':
        group_name = request.POST.get('group_name', '')
        comment = request.POST.get('comment', '')
        try:
            group = UserGroup.objects.filter(id=group_id).update(name=group_name, comment=comment)
            msg = u"用户组: %s修改成功" % group_name
        except Exception as err:
            error = u"用户组: %s修改失败, 错误原因: %s" % (group_name, err)
    
    return render(request, 'users/group_edit.html',locals())

@login_required(login_url='/login')
@role_required(role='super')
def user_group_list(request):
    path1, path2 = u'用户权限管理', u'用户组列表'
    try:
        groups = UserGroup.objects.all()
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())   
    return render(request, 'users/group_list.html',locals())

@login_required(login_url='/login')
@role_required(role='super')
def user_group_del(request):
    group_id = request.GET.get('id', '')
    group_id_list = group_id.split(',')

    for id_num in group_id_list:
        UserGroup.objects.filter(id=id_num).delete()
    return HttpResponseRedirect("/users/group/list/")

@login_required(login_url='/login')
@role_required(role='super')
def user_list(request):
    path1, path2 = u'用户权限管理', u'用户列表'
    try:
        users = User.objects.all()
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())      
    return render(request, 'users/user_list.html',locals())


@login_required(login_url='/login')
@role_required(role='super')
def user_add(request):
    path1, path2 = u'用户权限管理', u'添加用户'
    user_role = {'SU': u'超级管理员', 'CU': u'普通用户','AM': u'管理员'}
    group_all = UserGroup.objects.all()
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        group = request.POST.get('group', '')
        role = request.POST.get('role', 'CU')
        arg = request.POST.getlist('arg', [])
        is_active = False if '0' in arg else True
        try:
            check_user = User.objects.filter(username=username)
            if check_user:
                error = u'用户: %s已存在' % username
            else:
                group_id = UserGroup.objects.get(name=group)
                user = User(username=username, name=name, 
                            email=email, group=group_id, 
                            role=role, is_active=is_active, 
                            date_joined=datetime.datetime.now())
                user.set_password(password)
                user.save()
                msg = u"用户: %s添加成功" % username
        except Exception as error:
            error = u"用户: %s添加失败, 错误原因: %s" % (username, error)   
    return render(request, 'users/user_add.html',locals())
 
@login_required(login_url='/login')
@role_required(role='super')   
def user_del(request):
    user_id = request.GET.get('id', '')
    user_id_list = user_id.split(',')

    for id_num in user_id_list:
        User.objects.filter(id=id_num).delete()
    return HttpResponseRedirect("/users/user/list/")

@login_required(login_url='/login')
@role_required(role='super')
def user_edit(request):
    """
       修改用户信息
    """
    path1, path2 = u'用户权限管理', u'修改用户'
    user_role = {'SU': u'超级管理员', 'CU': u'普通用户','AM': u'管理员'}
    user_id = request.GET.get('id', '')
    user_list = User.objects.get(id=user_id)
    group_all = UserGroup.objects.all().exclude(name=user_list.group)
    perm_list = Permission.objects.filter(codename__startswith="has_")
    user_has_perms = [ u.get('id') for u in user_list.user_permissions.values()]
    for user_perm in perm_list:
        if user_perm.id in user_has_perms:
            user_perm.status = 1
        else:
            user_perm.status = 0 
    if request.method == 'POST':
        username = request.POST.get('username', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        group = request.POST.get('group', '')
        role = request.POST.get('role', 'CU')
        arg = request.POST.getlist('arg', [])
        perms = request.POST.getlist('perm')
        is_active = False if '0' in arg else True
        try:
            group_id = UserGroup.objects.get(name=group)
            User.objects.filter(id=user_id).update(username=username, name=name, group=group_id, email=email, role=role, is_active=is_active)
            if perms is None:
                User.objects.get(id=user_id).user_permissions.clear()
            else:
                user_perm_list = []
                for perm in User.objects.get(id=user_id).user_permissions.values():
                    user_perm_list.append(perm.get('id'))
                perm_list = [ int(i) for i in perms]
                add_perm_list = list(set(perm_list).difference(set(user_perm_list)))
                del_perm_list = list(set(user_perm_list).difference(set(perm_list)))
                #添加新增的权限
                for perm_id in add_perm_list:
                    perm = Permission.objects.get(id=perm_id)
                    User.objects.get(id=user_id).user_permissions.add(perm)
                #删除去掉的权限
                for perm_id in del_perm_list:
                    perm = Permission.objects.get(id=perm_id)
                    User.objects.get(id=user_id).user_permissions.remove(perm) 
            msg = u"用户: %s修改成功" % username
        except Exception as err:
            error = u"用户: %s修改失败, 错误原因: %s" % (username, err)    
    return render(request, 'users/user_edit.html', locals())

@login_required(login_url='/login')
@role_required(role='super')
def perm_rule_add(request):
    path1, path2 = u'用户权限管理', u'添加权限'
    user_list = User.objects.all()
    group_list = UserGroup.objects.all()
    project_list = PlatformType.objects.all()
    if request.method == 'POST':
        rule_name = request.POST.get('rule_name', '')
        users = request.POST.getlist('username', [])
        groups = request.POST.getlist('group', [])
        project_list = request.POST.getlist('project_selected', [])
        comment = request.POST.get('comment', '')
        try:
            check_rule = PermRule.objects.filter(rule_name=rule_name)
            if check_rule:
                error = u'权限: %s已存在' % rule_name
            else:
                user_obj = [User.objects.get(id=user_id) for user_id in users]
                group_obj = [UserGroup.objects.get(id=group_id) for group_id in groups]
                project_obj = [PlatformType.objects.get(platform_id=project_id) for project_id in project_list]
                perm = PermRule(rule_name=rule_name, comment=comment)
                perm.save()
                perm.platform = project_obj
                perm.username = user_obj
                perm.user_group = group_obj
                perm.save()
                msg = u"权限: %s添加成功" % rule_name
        except Exception as error:
            error = u"权限: %s添加失败, 错误原因: %s" % (rule_name, error)  
    return render(request, 'users/perm_rule_add.html',locals())

@login_required(login_url='/login')
@role_required(role='super')
def perm_rule_edit(request):
    path1, path2 = u'用户权限管理', u'修改权限'
    list1 =[]
    list2 = []
    rule_id = request.GET.get('id')
    user_list = User.objects.all()
    group_list = UserGroup.objects.all()
    if len(PermRule.objects.filter(id=rule_id)) == 1:
        perms = PermRule.objects.filter(id=rule_id)[0]
    else:
        perms = None
    for perm in perms.platform.all():
        list1.append(perm.platform_name)
    for platform in PlatformType.objects.all():
        list2.append(platform.platform_name)      
    projects_list = list(set(list2) - set(list1))
    if request.method == 'POST':
        rule_name = request.POST.get('rule_name', '')
        users = request.POST.getlist('username', [])
        groups = request.POST.getlist('group', [])
        project_list = request.POST.getlist('project_selected', [])
        comment = request.POST.get('comment', '')
        try:
            user_obj = [User.objects.get(id=user_id) for user_id in users]
            group_obj = [UserGroup.objects.get(id=group_id) for group_id in groups]
            project_obj = [PlatformType.objects.get(platform_name=project_name) for project_name in project_list]
            perms.rule_name = rule_name
            perms.comment = comment
            perms.platform = project_obj
            perms.username = user_obj
            perms.user_group = group_obj
            perms.save()
            msg = u"权限: %s修改成功" % rule_name
        except Exception as error:
            error = u"权限: %s修改失败, 错误原因: %s" % (rule_name, error)  
    return render(request, 'users/perm_rule_edit.html',locals())


@login_required(login_url='/login')
@role_required(role='super')
def perm_rule_list(request):
    path1, path2 = u'用户权限管理', u'权限列表'
    try:
        perms = PermRule.objects.all()
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())   
    return render(request, 'users/perm_rule_list.html',locals())

@login_required(login_url='/login')
@role_required(role='super')
def perm_rule_del(request):
    perm_id = request.GET.get('id', '')
    perm_id_list = perm_id.split(',')

    for id_num in perm_id_list:
        PermRule.objects.filter(id=id_num).delete()
    return HttpResponseRedirect("/users/perm/list/")

