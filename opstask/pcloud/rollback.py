# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from api.views import create_ansible_variables
from cmdb.models import AnsibleGroup, BackupLogs
from api.views import create_ansible_hosts
from api.pcloud.views import pcloud_execute_ansible_job
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from api.views import role_required,get_app_type
from api.ansible import ansible_role_config
import json, datetime, time, os
import traceback, logging


@login_required(login_url='/login')
@role_required(role='admin')
def pcloud_rollback_code(request):
    """
      创建ansible job
    """
    path1, path2, path3 = u'项目变更回退', u'私有云项目', '程序包回退'
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    #ansible_group = AnsibleGroup.objects.filter(app_type="private_cloud", group_type="rollback")
    role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_rollback_pack_task']
    project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['pcloud_path']
    """"auth check"""
    if len(set(app_type_dict.keys()).intersection(set(ansible_role_config.PCLOUD_APP_TYPE))) == 0:
        if username == "管理员":
            pass
        else:
            return render(request, 'error/403.html')
    job_name = "private_cloud-jar-rollback-{0}".format(datetime.datetime.now().strftime("%Y%m%d%H%M"))
    if request.method == 'POST':
        try:
            bk_file = []
            content = {}
            group = request.POST.get('ab_group', '')
            bkfile_list = request.POST.getlist('bk_file')
            switch = request.POST.get('switch')
            rollback_path = request.POST.get('rollback_path')
            inventory = "{0}/inventory/{1}".format(project_path, group)
            playbook = "{0}/{1}.yml".format(project_path, group)
            vars_file = "{0}/group_vars/{1}.yml".format(project_path, group)
            """create host"""
            create_ansible_hosts(inventory, playbook, group, role, 'pcloud')
            """创建调用变量"""
            """delete old variables if exists, for safety"""
            if os.path.exists(vars_file):
                os.remove(vars_file)
            if bkfile_list:
                for bkfile in bkfile_list:
                    bk_file.append(bkfile.encode('utf8'))
            content['bk_pack_file'] = bk_file
            content['rollback_pack_path'] = rollback_path.strip()
            content['reload_pack'] = switch            
            create_ansible_variables(vars_file, content)

            """创建发布task"""
            task_id, log_file = pcloud_execute_ansible_job(playbook, inventory)
            return JsonResponse({"task_id": task_id, 'log_file': log_file, 'job_name':job_name, 'inventory': inventory, 'code': 200})
        except Exception as err:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 
            return JsonResponse({'error':str(err), 'code': 500}) 
    
    return render(request, 'pcloud/rollback/rollback_code.html',locals())

@login_required(login_url='/login')
@role_required(role='admin')
def pcloud_rollback_config(request):
    """
      创建ansible job
    """
    path1, path2, path3 = u'项目变更回退', u'私有云项目', '配置文件回退'
    #ansible_group = AnsibleGroup.objects.filter(app_type="private_cloud", group_type="rollback")
    role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_rollback_config_task']
    project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['pcloud_path']
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    """"auth check"""
    if len(set(app_type_dict.keys()).intersection(set(ansible_role_config.PCLOUD_APP_TYPE))) == 0:
        if username == "管理员":
            pass
        else:
            return render(request, 'error/403.html')
    job_name = "private_cloud-cfg-rollback-{0}".format(datetime.datetime.now().strftime("%Y%m%d%H%M"))
    if request.method == 'POST':
        try:
            content = {}
            bk_config_list = []
            group = request.POST.get('ab_group', '')
            bk_config = request.POST.getlist('bk_config')
            rollback_path = request.POST.get('rollback_path')
            switch = request.POST.get('switch')
            inventory = "{0}/inventory/{1}".format(project_path, group)
            playbook = "{0}/{1}.yml".format(project_path, group)
            """create host"""
            create_ansible_hosts(inventory, playbook, group, role, 'pcloud')
            vars_file = "{0}/group_vars/{1}.yml".format(project_path, group)
            """创建调用变量"""
            """delete old variables if exists, for safety"""
            if os.path.exists(vars_file):
                os.remove(vars_file)
            if bk_config:
                for bk_cfg in bk_config:
                    bk_config_list.append(bk_cfg.encode('utf8'))
            content['bk_cfg_file'] = bk_config_list
            content['rollback_cfg_path'] = rollback_path.strip()
            content['reload_rb_cfg'] = switch              
            create_ansible_variables(vars_file, content)

            """创建发布task"""
            task_id, log_file = pcloud_execute_ansible_job(playbook, inventory)
            return JsonResponse({"task_id": task_id, 'log_file': log_file, 'job_name':job_name, 'inventory': inventory, 'code': 200})
        except Exception as err:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 
            return JsonResponse({'error':str(err), 'code': 500})
    
    return render(request, 'pcloud/rollback/rollback_config.html',locals())


#@login_required(login_url='/login')
@role_required(role='admin')
def pcloud_get_backup_file(request):
    rollback_type = request.GET.get('rb_type')
    if rollback_type == 'code':
        backup_list = BackupLogs.objects.filter(project='pcloud').exclude(backup_file__contains='config')
        return render(request, 'pcloud/backup_app_list.html',locals())
    elif rollback_type == 'config':
        backup_list = BackupLogs.objects.filter(project='pcloud', backup_file__contains='config')
        return render(request, 'pcloud/backup_config_list.html',locals())


