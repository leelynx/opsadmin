# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from api.data.Redis_API import RedisAPI
from opsadmin.settings import ANSIBLE_SCRIPTS
from django.http import JsonResponse
from cmdb.models import ServerInfo
from api.ansible.ansible_api_v2 import ANSRunner
from api.data.MySQL_API import AnsibleRecord
from opstask.models import AnsibleScripts, AnsibleModelRecord
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from api.views import role_required
from django.db.models import Q
import datetime, os, uuid
import traceback, logging
import base64



def save_script(content, filepath):
    if not os.path.isdir(os.path.dirname(filepath)):
        os.makedirs(os.path.dirname(filepath))
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath


@login_required(login_url='/login')
@role_required(role='super')
def ansible_create_script(request):
    """
      新建ansible脚本作业
    """
    path1, path2 = u'作业管理中心', u'新建作业脚本'
    try:
        username = request.session.get('name')
        task_uuid = uuid.uuid1()
        create_time = modify_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if request.method == 'GET':
            return render(request, 'tasks/jobs/script/ansible_create_script.html', locals())
        if request.method == 'POST':
            filename = "{path}/script-{random_num}".format(path=ANSIBLE_SCRIPTS, random_num=uuid.uuid1().hex[0:8])
            save_script(request.POST.get('code').encode('utf-8'), filename)
            job_list = request.POST.getlist('job')
            debug_mode = request.POST.get('ansible_debug')
            if AnsibleScripts.objects.filter(script_name=job_list[0]):
                return JsonResponse({'msg': "脚本名称重复", 'code': 500, 'data': []})
            AnsibleScripts.objects.create(
                                        script_name = job_list[0],
                                        script_uuid = request.POST.get('task_uuid'),
                                        exec_host = str(request.POST.get('host')),
                                        script_arg = job_list[1],
                                        exec_timeout = job_list[2],
                                        script_file = filename,
                                        creator = username,
                                        create_time = create_time,
                                        modifier = username,
                                        modify_time = modify_time,
                                        debug_mode = debug_mode,
                                        state= "create"
                                    )
            return JsonResponse({'msg': "脚本保存成功", 'code': 200, 'data': []})
    except Exception as error:
        return JsonResponse({'msg': error, 'code': 500, 'data': []})      

@login_required(login_url='/login')
@role_required(role='super')  
def ansible_edit_script(request, pid):
    """
      修改ansible脚本作业
    """
    path1, path2 = u'作业管理中心', u'修改作业脚本'
    try:
        scripts = AnsibleScripts.objects.get(id=pid)
        script_file = scripts.script_file
        username = request.session.get('name')
        if request.method == 'GET':

            host_list = scripts.exec_host.split(',')
            if os.path.exists(scripts.script_file):
                content = ""
                with open(scripts.script_file, 'r') as f:
                    if 'bash' in f.readline():
                        scripts.script_type = 'shell'
                        content = "#!/bin/bash\n"
                    else:
                        scripts.script_type = 'python'
                        content = "#!/usr/bin/env python\n"
                    for line in f.readlines():
                        content = content + line
                scripts.code = content
            
            return render(request, 'tasks/jobs/script/ansible_edit_script.html', {'path1': path1, 'path2': path2, 'scripts': scripts, 'host_list': host_list})
        if request.method == 'POST':
            save_script(request.POST.get('code').encode('utf-8'), script_file)
            job_list = request.POST.getlist('job')
            debug_mode = request.POST.get('ansible_debug')
            AnsibleScripts.objects.filter(id=pid).update(
                                        script_name = job_list[0],
                                        exec_host = str(request.POST.get('host')),
                                        script_arg = job_list[1],
                                        exec_timeout = job_list[2],
                                        script_file = script_file,
                                        modifier = username,
                                        modify_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        debug_mode = debug_mode,
                                        state= "update"
                                    )
            return JsonResponse({'msg': "脚本保存成功", 'code': 200, 'data': []})
    except Exception as error:
        return JsonResponse({'msg': error, 'code': 500, 'data': []})   
 
@login_required(login_url='/login')
@role_required(role='super')      
def ansible_del_script(request):
    script_id = request.GET.get('id', '')
    AnsibleScripts.objects.filter(id=script_id).delete()
    return HttpResponseRedirect(reverse('ansible_list_script'))


@login_required(login_url='/login')
@role_required(role='super')
def ansible_list_script(request):
    """
      ansible脚本库
    """
    path1, path2 = u'作业管理中心', u'作业脚本库'
    try:
        scripts = AnsibleScripts.objects.all()
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())
    return render(request, 'tasks/jobs/script/ansible_list_script.html', locals())
    

@login_required(login_url='/login')
@role_required(role='super')
def ansible_run_script(request):
    """
    执行ansible作业脚本
    """
    path1, path2 = u'作业管理中心', u'执行作业脚本'
    try:
        username = request.session.get('name')
        if request.method == 'GET':
            task_uuid = request.GET.get('task_uuid')
            return render(request, 'tasks/jobs/script/ansible_run_script.html', locals())
        if request.method == 'POST':
            task_uuid = request.POST.get('task_uuid')
            resource = []
            script_list = AnsibleScripts.objects.filter(script_uuid=task_uuid)
            for script in script_list:
                if script.script_arg:
                    module_args = "{filepath} {arg}".format(filepath=script.script_file, arg=script.script_arg)
                else:
                    module_args = script.script_file
                logId = AnsibleRecord.Model.insert(ansible_user=username, ansible_host=script.exec_host, ansible_model='script', ansible_args=module_args, create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                AnsibleScripts.objects.filter(script_uuid=task_uuid).update(state="executing")
                RedisAPI.AnsibleModel.delete(task_uuid)
                RedisAPI.AnsibleModel.lpush(task_uuid, "[Start] Ansible Model: {model}  Script:{script}".format(model='script', script=script.script_file))
                for host in script.exec_host.split(','):
                    server_info = ServerInfo.objects.filter(private_ip=host)
                    for server in server_info:
                        passwd = base64.b64decode(server.password.encode('utf-8'))
                        resource.append({"hostname": host, "port": "{port}".format(port=server.host_port), "username": server.username, "password": passwd})           
                if script.debug_mode == 'on':
                    ANS = ANSRunner(resource, task_uuid, logId, verbosity=4)
                else:
                    ANS = ANSRunner(resource, task_uuid, logId)
                ANS.run_model(host_list=script.exec_host.split(','), module_name='script',module_args=module_args)
                RedisAPI.AnsibleModel.lpush(task_uuid, "[Done] Ansible Done.")
                AnsibleModelRecord.objects.filter(ansible_args=module_args).update(end_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                AnsibleScripts.objects.filter(script_uuid=task_uuid).update(state="finished")
            return JsonResponse({'msg':"操作成功","code":200,'data':[]})
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())
        return JsonResponse({'msg': error, 'code': 500, 'data': []})
    

@login_required(login_url='/login')
@role_required(role='super')
def ansible_polling_result(request):
    """
    轮询读取ansible执行结果日志
    """
    if request.method == "POST":
        task_uuid = request.POST.get('task_uuid')          
        msg = RedisAPI.AnsibleModel.rpop(task_uuid)
        if msg:
            return JsonResponse({'msg':msg,"code":200,'data':[]}) 
        else:
            return JsonResponse({'msg':None,"code":200,'data':[]})

@login_required(login_url='/login')
@role_required(role='super')
def ansible_model_cmd(request):
    """
    执行ansible命令
    """
    path1, path2 = u'系统管理工具', u'远程执行命令'
    try:
        username = request.session.get('name')
        if request.method == 'GET':
            task_uuid = uuid.uuid1()
            return render(request, 'tools/ansible_run_cmd.html', locals())
        if request.method == 'POST':
            task_uuid = request.POST.get('task_uuid')
            host_list = str(request.POST.get('host',''))
            resource = []
            module_args = request.POST.get('ansible_args',None)
            if 'rm' in module_args.split() or '/bin/rm' in module_args.split():
                print module_args.split()
                return JsonResponse({'msg':"含有非法操作命令rm","code":500,'data':[]})
            if len(request.POST.get('custom_model')) > 0:
                model_name = request.POST.get('custom_model')
            else:
                model_name = request.POST.get('ansible_model',None)
            logId = AnsibleRecord.Model.insert(ansible_user=username, ansible_host=host_list, ansible_model=model_name, ansible_args=module_args, create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            RedisAPI.AnsibleModel.delete(task_uuid)
            RedisAPI.AnsibleModel.lpush(task_uuid, "[Start] Ansible Model: {model}  Args: {args}".format(model=model_name, args=module_args))
            for host in host_list.split(','):
                server_info = ServerInfo.objects.filter(private_ip=host)
                for server in server_info:
                    passwd = base64.b64decode(server.password.encode('utf-8'))
                    resource.append({"hostname": host, "port": "{port}".format(port=server.host_port), "username": server.username, "password": passwd})           
            if request.POST.get('debug_mode') == 'on':
                ANS = ANSRunner(resource, task_uuid, logId, verbosity=4)
            else:
                ANS = ANSRunner(resource, task_uuid, logId)
            ANS.run_model(host_list=host_list.split(','), module_name=model_name, module_args=module_args)
            RedisAPI.AnsibleModel.lpush(task_uuid, "[Done] Ansible Done.")
            AnsibleModelRecord.objects.filter(ansible_args=module_args).update(end_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            return JsonResponse({'msg':"操作成功","code":200,'data':[]})
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())
        return JsonResponse({'msg': error, 'code': 500, 'data': []}) 
    

@login_required(login_url='/login')
@role_required(role='admin')
def get_host_list(request):
    host_list = ServerInfo.objects.values('private_ip', 'hostname', 'resource_area')
    return  render(request, 'tasks/host_list.html', locals())

