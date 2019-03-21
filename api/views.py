# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render
from cmdb.models import AnsibleGroup, AppInfo, PlatformType
from users.models import User, PermRule
from api.ansible.create_ansible_hosts_list import Generate_ansible_hosts
from django.contrib.auth.decorators import login_required
from celery.result import AsyncResult
from api.tasks import *
import logging
from tempfile import NamedTemporaryFile
import time
import json
import os


def create_ansible_hosts(inventory, playbook_file, group, roles, host_list, exe_mode='true'):
    """创建主机组清单文件"""
    try:
        ab_group = AnsibleGroup.objects.get(group=group)
        host_info = ab_group.serverinfos.all().values()
        if host_list == 'pcloud':
            data = [items for items in host_info]
        else:
            data = []
            for items in host_info:
                if set(host_list).intersection(items.values()):
                    data.append(items)
        host = [{'group': group, 'items': data}]
        generate_hosts = Generate_ansible_hosts(inventory)
        f = open(playbook_file, 'a+')
        f.truncate()
        if exe_mode == 'true':
            print >> f, "- hosts: {0}".format(group)
            print >> f, "  gather_facts:  false"
            print >> f, "  serial: 1"
            print >> f, "  roles:"
            print >> f, "    - {0}".format(roles)
            f.close()
        elif exe_mode == 'false':
            print >> f, "- hosts: {0}".format(group)
            print >> f, "  gather_facts:  false"
            print >> f, "  roles:"
            print >> f, "    - {0}".format(roles)
            f.close()           
        generate_hosts.create_all_servers(host)
    except Exception as err:
        logg = logging.getLogger('opsadmin')
        logg.error(err)

def create_ansible_variables(vars_file, kwargs):
    """生成ansible变量值"""
    try:
        f = open(vars_file, 'a+')
        f.truncate()
        f.write("---\n")
        for k, v in kwargs.items():
            print >> f, "{0}: {1}".format(k, v)
        f.close()
    except Exception as err:
        logg = logging.getLogger('opsadmin')
        logg.error(err)


def check_task_result(task_id):
    "get task result"
    res = AsyncResult(task_id)
    res_msg = res.result
    return res_msg
    

def check_task_state(task_id):
    """get task current status"""
    res = AsyncResult(task_id)
    return res.state


def execute_ansible_task(yml_file, hosts_file, timeout=180):
    """"execute task"""
    try:
        data = {}
        tempdir = "/tmp/ansible"
        data['yml_file'] = yml_file
        data['hosts_file'] = hosts_file
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        f = NamedTemporaryFile(delete=False, dir=tempdir)
        data['log_file'] = f.name
        data['timeout'] = timeout
        result = async_execute_ansible_job.delay(data)
        return result.task_id, f.name
    except:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())

@login_required(login_url='/login')
def revoke_ansible_task(request):
    """"revoke run task"""
    if request.method == 'POST':
        task_id = request.POST.get('task_id').encode('utf-8')
        try:
            AsyncResult(task_id).revoke(terminate=True, signal='SIGKILL')
            #celery_contorl = Control()
            #celery_contorl.revoke(task_id, terminate=True, signal='SIGKILL')
            return JsonResponse({"message": "取消任务完成", 'code': 200})
        except Exception as e:
            return JsonResponse({"message": u'取消任务失败.{0}'.format(e), 'code': 500})


@login_required(login_url='/login')
def upload_file_api(request):
    """上传文件"""
    if request.method == 'POST' and request.FILES:
        upload_path = request.POST.get('path', '')
        uploadfiles = request.FILES.getlist('file_data', None)
        try:
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
                
            for uploadfile in uploadfiles:
                
                file_save = "%s/%s" % (upload_path, uploadfile.name)
                if os.path.exists(file_save):
                    os.remove(file_save)    
                with open(file_save, 'wb+') as f:
                    for chunk in uploadfile.chunks():
                        f.write(chunk)  
        except Exception as E:
            error = json.dumps({"Failed": E.message})
            return HttpResponse(error)
        msg = json.dumps({'result': 'sucess'})
    return HttpResponse(msg)
      

@login_required(login_url='/login')
def get_ansible_group(request):
    app_type = request.GET.get('app_type')
    #group_type = request.GET.get('group_type')
    auth_app = get_app_type(request.session.get('name'))
    if auth_app.has_key(app_type):
        ansible_group = AnsibleGroup.objects.filter(app_type=app_type).values('group','comment')
        group_list = []
        for group_dict in ansible_group:
            ip_list = AnsibleGroup.objects.get(group=group_dict['group']).serverinfos.all()
            ips = []
            for ip in ip_list:
                ips.append(str(ip))
            group_dict['ip_set'] = ','.join(ips)
            group_list.append(group_dict)
    else:
        group_list = [{'group': '非授权主机', 'ip_set': '非授权主机','comment':"非授权主机"}]
    return render(request, 'api/group_list.html',locals())

@login_required(login_url='/login')
def get_service_list(request):
    #获取部署service路径
    app_type = request.GET.get('app_type')
    auth_app = get_app_type(request.session.get('name'))
    if auth_app.has_key(app_type):
        service_list = AppInfo.objects.filter(app_type=app_type).values('app_name').distinct()
    else:
        service_list = [{'app_name': '非授权项目'}]
    return render(request, 'api/service_list.html',locals())

def get_app_type(username):
    """"check permissions"""
    try:
        app_dict = {}
        user_obj = User.objects.filter(name=username)
        perm_set = PermRule.objects.filter(username=user_obj)
        for perms in perm_set:
            for perm in perms.platform.all():
                platform = perm.platform_name
                app_set  = PlatformType.objects.filter(platform_name=platform)
                for app in app_set:
                    app_type = app.short_name
                    app_dict[app_type] = platform
        return app_dict
    except Exception as err:
        logg = logging.getLogger('opsadmin')
        logg.error(err)  
        
 
def role_required(role='user'):
    """get user role"""
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if role == 'admin':
                if request.user.role == 'CU':
                    return HttpResponseRedirect(reverse('index'))
            elif role == 'super':
                if request.user.role in ['CU', 'AM']:
                    return HttpResponseRedirect(reverse('index'))
            return func(request, *args, **kwargs)

        return wrapper

    return decorator

def execute_release_task(playbook, inventory, job_name, app_type, task_detail, pid, release_tag):
    """"execute async task """
    try:
        task_id, log_file = execute_ansible_task(playbook, inventory)
        data = {"task_id": task_id, 
                'log_file': log_file, 
                'job_name':job_name, 
                'app_type':app_type, 
                'task_detail':task_detail, 
                'inventory': inventory, 
                'pid': pid,
                'release_tag': release_tag,
                'code': 200}
        return data
    except Exception as err:
        logg.error(err)

def get_app_detail(app_type, app_name):
    """get app deploy informain"""
    app_data = AppInfo.objects.filter(app_type=app_type, app_name=app_name).first()
    app_name = app_data.app_name
    app_port = app_data.run_port
    app_path = app_data.main_path
    app_bk = app_data.backup_path
    app_work = app_data.work_path 
    return app_name, app_port, app_path, app_bk, app_work
