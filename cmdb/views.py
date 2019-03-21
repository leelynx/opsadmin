# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from api.views import role_required
from cmdb.models import ServerInfo, AppInfo, PlatformType, AnsibleGroup
from cmdb.forms import ServerInfoForm, AppInfoForm
from django.contrib.auth.decorators import permission_required
import logging, traceback

# Create your views here.
@login_required(login_url='/login')
@permission_required('cmdb.has_read_server',login_url='/forbidden/')
def cmdb_server_list(request):
    """
      列出服务器主机信息
    """
    path1, path2 = u'CMDB资源管理', u'主机列表'
    try:
        servers = ServerInfo.objects.all()
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())  
    return render(request, 'cmdb/server_list.html',locals())

@login_required(login_url='/login')
@permission_required('cmdb.has_add_server',login_url='/forbidden/')
def cmdb_server_add(request):
    """
       添加主机资源
    """
    path1, path2 = u'CMDB资源管理', u'添加主机'
    server_form = ServerInfoForm()
    if request.method == 'POST':
        ip = request.POST.get('private_ip', '')
        form = ServerInfoForm(request.POST)
        if form.is_valid():
            server_form_save = form.save(commit=False)
            server_form_save.save()
            form.save_m2m()
            msg = u'主机 %s 添加成功' % ip
        else:
            error = u'主机 %s 添加失败' % ip
    
    return render(request, 'cmdb/server_add.html',locals())

@login_required(login_url='/login')
@permission_required('cmdb.has_chanage_server',login_url='/forbidden/')
def cmdb_server_edit(request):
    """
       修改主机资源
    """
    path1, path2 = u'CMDB资源管理', u'修改主机'
    server_id = request.GET.get('id', '')
    server = ServerInfo.objects.get(server_id=server_id)
    server_form = ServerInfoForm(instance=server)
    try:
        if request.method == 'POST':
            server_post = ServerInfoForm(request.POST, instance=server)
            ip = request.POST.get('private_ip', '')
            hostname = request.POST.get('hostname', '')
            if server_post.is_valid():
                server_form_save = server_post.save(commit=False)
                server_form_save.save()
                server_post.save_m2m()                
                msg = u'主机 %s 修改成功' % ip
            else:
                error = u'主机 %s 修改失败' % ip
    except:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())    
    return render(request, 'cmdb/server_edit.html',locals())


@login_required(login_url='/login')
@permission_required('cmdb.has_delete_server',login_url='/forbidden/')
def cmdb_server_del(request):
    """
       删除主机信息
    """
    server_id = request.GET.get('id', '')
    server_id_list = server_id.split(',')

    for id_num in server_id_list:
        ServerInfo.objects.filter(server_id=id_num).delete()    
    return HttpResponseRedirect("/cmdb/server/list/")

@login_required(login_url='/login')
@permission_required('cmdb.has_read_server',login_url='/forbidden/')
def cmdb_server_detail(request):
    """
       主机详细信息
    """
    server_id = request.GET.get('id')
    server_list = ServerInfo.objects.get(pk=int(server_id))    
    return render(request, 'cmdb/server_detail.html',locals()) 



"""项目分类"""
@login_required(login_url='/login')
@permission_required('cmdb.has_read_project',login_url='/forbidden/')
def cmdb_project_list(request):
    """
      列出服务器主机信息
    """
    path1, path2 = u'CMDB资源管理', u'项目列表'
    try:
        projects = PlatformType.objects.all()
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())       
    return render(request, 'cmdb/project_list.html',locals())

@login_required(login_url='/login')
@permission_required('cmdb.has_add_project',login_url='/forbidden/')
def cmdb_project_add(request):
    """
       添加项目
    """
    path1, path2 = u'CMDB资源管理', u'添加项目'

    if request.method == 'POST':
        project_name = request.POST.get('project_name', '')
        short_name = request.POST.get('short_name', '')
        comment = request.POST.get('comment', '')
        get_project_name = PlatformType.objects.filter(platform_name=project_name)
        if get_project_name:
            error = u"项目类: %s已存在" % project_name
        else:
            try:
                project = PlatformType(platform_name=project_name, short_name=short_name, comment=comment)
                project.save()
                msg = u"项目类: %s添加成功" % project_name
            except Exception,err:
                error = u"项目类: %s添加失败, 错误原因: %s" % (project_name, err)
    
    return render(request, 'cmdb/project_add.html',locals())

@login_required(login_url='/login')
@permission_required('cmdb.has_chanage_project',login_url='/forbidden/')
def cmdb_project_edit(request):
    """
       修改项目信息
    """
    path1, path2 = u'CMDB资源管理', u'修改项目'
    project_id = request.GET.get('id', '')
    project = PlatformType.objects.get(platform_id=project_id)
    if request.method == 'POST':
        project_name = request.POST.get('project_name', '')
        short_name = request.POST.get('short_name', '')
        comment = request.POST.get('comment', '')
        try:
            PlatformType.objects.filter(platform_id=project_id).update(platform_name=project_name, short_name=short_name, comment=comment)
            msg = u"项目类: %s修改成功" % project_name
        except Exception,err:
            error = u"项目类: %s修改失败, 错误原因: %s" % (project_name, err)     
    return render(request, 'cmdb/project_edit.html',locals())

@login_required(login_url='/login')
@permission_required('cmdb.has_delete_project',login_url='/forbidden/')
def cmdb_project_del(request):
    """
       删除项目信息
    """
    projects_id = request.GET.get('id', '')
    project_id_list = projects_id.split(',')
    print projects_id

    for id_num in project_id_list:
        PlatformType.objects.filter(platform_id=id_num).delete()
    return HttpResponseRedirect("/cmdb/project/list/")


"""应用管理"""
@login_required(login_url='/login')
@permission_required('cmdb.has_read_app',login_url='/forbidden/')
def cmdb_app_list(request):
    """
       部署应用信息
    """
    path1, path2 = u'CMDB资源管理', u'应用列表'
    try:
        apps = AppInfo.objects.all()
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())    
    return render(request, 'cmdb/app_list.html',locals())

@login_required(login_url='/login')
@permission_required('cmdb.has_add_app',login_url='/forbidden/')
def cmdb_app_add(request):
    """
       添加应用资源
    """
    path1, path2 = u'CMDB资源管理', u'添加应用'
    #app = AppInfo.objects.all()
    app_form = AppInfoForm()
    if request.method == 'POST':
        app_name = request.POST.get('app_name', '')
        form = AppInfoForm(request.POST)
        if form.is_valid():
            app_form_save = form.save(commit=False)
            app_form_save.save()
            form.save_m2m()
            msg = u'应用 %s 添加成功' % app_name
        else:
            error = u'应用 %s 添加失败' % app_name
    
    return render(request, 'cmdb/app_add.html',locals())

@login_required(login_url='/login')
@permission_required('cmdb.has_chanage_app',login_url='/forbidden/')
def cmdb_app_edit(request):
    """
       修改主机资源
    """
    path1, path2 = u'CMDB资源管理', u'修改应用'
    app_id = request.GET.get('id', '')
    app = AppInfo.objects.get(app_id=app_id)
    app_form = AppInfoForm(instance=app)
    try:
        if request.method == 'POST':
            app_post = AppInfoForm(request.POST, instance=app)
            app_name = request.POST.get('app_name', '')
            if app_post.is_valid():
                app_form_save = app_post.save(commit=False)
                app_form_save.save()
                app_post.save_m2m()                
                msg = u'应用信息 %s 修改成功' % app_name
            else:
                error = u'应用信息%s 修改失败' % app_name
    except Exception as error:
        error = error
    return render(request, 'cmdb/app_edit.html',locals())


@login_required(login_url='/login')
@permission_required('cmdb.has_delete_app',login_url='/forbidden/')
def cmdb_app_del(request):
    """
       删除应用信息
    """
    app_id = request.GET.get('id', '')
    app_id_list = app_id.split(',')

    for id_num in app_id_list:
        AppInfo.objects.filter(app_id=id_num).delete()    
    return HttpResponseRedirect("/cmdb/app/list/")


@login_required(login_url='/login')
@permission_required('cmdb.has_read_app',login_url='/forbidden/')
def cmdb_app_detail(request):
    """
       应用详细信息
    """
    app_id = request.GET.get('id')
    app_list = AppInfo.objects.get(pk=int(app_id))    
    return render(request, 'cmdb/app_detail.html',locals()) 



"""Ansible分组"""
@login_required(login_url='/login')
@permission_required('cmdb.has_read_ansible_group',login_url='/forbidden/')
def cmdb_ansible_list(request):
    """
      列出ansible分组列表
    """
    path1, path2 = u'CMDB资源管理', u'ansible分组列表'
    try:
        ansibles = AnsibleGroup.objects.all()
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc()) 
    return render(request, 'cmdb/ansible_list.html',locals())

@login_required(login_url='/login')
@permission_required('cmdb.has_add_ansible_group',login_url='/forbidden/')
def cmdb_ansible_add(request):
    """
       添加分组
    """
    path1, path2 = u'CMDB资源管理', u'添加ansible分组'

    if request.method == 'POST':
        ansible_group = request.POST.get('ansible_group', '')
        app_type = request.POST.get('app_type', '')
        comment = request.POST.get('comment', '')
        get_ansible_name = AnsibleGroup.objects.filter(group=ansible_group)
        if get_ansible_name:
            error = u"ansible分组: %s已存在" % ansible_group
        else:
            try:
                ansible = AnsibleGroup(group=ansible_group,  app_type=app_type, comment=comment)
                ansible.save()
                msg = u"ansible分组: %s添加成功" % ansible_group
            except Exception,err:
                error = u"ansible分组: %s添加失败, 错误原因: %s" % (ansible_group, err)
    
    return render(request, 'cmdb/ansible_add.html',locals())

@login_required(login_url='/login')
@permission_required('cmdb.has_delete_ansible_group',login_url='/forbidden/')
def cmdb_ansible_del(request):
    """
       删除ansible分组
    """
    ansibles_id = request.GET.get('id', '')
    ansible_id_list = ansibles_id.split(',')

    for id_num in ansible_id_list:
        AnsibleGroup.objects.filter(group_id=id_num).delete()
    return HttpResponseRedirect("/cmdb/ansible/list/")

@login_required(login_url='/login')
@permission_required('cmdb.has_change_ansible_group',login_url='/forbidden/')
def cmdb_ansible_edit(request):
    """
       修改分组信息
    """
    path1, path2 = u'CMDB资源管理', u'修改分组'
    ansible_id = request.GET.get('id', '')
    ansible_group = AnsibleGroup.objects.get(group_id=ansible_id)
    if request.method == 'POST':
        group = request.POST.get('ansible_group', '')
        app_type = request.POST.get('app_type', '')
        comment = request.POST.get('comment', '')
        try:
            AnsibleGroup.objects.filter(group_id=ansible_id).update(group=group, app_type=app_type, comment=comment)
            msg = u"分组: %s修改成功" % group
        except Exception,err:
            error = u"分组: %s修改失败, 错误原因: %s" % (group, err)    
    return render(request, 'cmdb/ansible_edit.html', locals())
