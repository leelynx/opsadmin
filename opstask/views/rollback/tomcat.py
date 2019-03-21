# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from api.views import create_ansible_variables
from api.views import create_ansible_hosts, execute_ansible_task
from django.contrib.auth.decorators import login_required
from opstask.models import AnsibleTaskRecord
from django.http import JsonResponse, HttpResponseRedirect
from api.views import get_app_type
from django.core.urlresolvers import reverse
from api.views import role_required
from api.ansible import ansible_role_config
import datetime, os
import logging
import traceback



@login_required(login_url='/login')
@role_required(role='admin')
def tomcat_rollback_task(request, pid):
    """
      创建ansible rollback task
    """
    path1, path2, path3 = u'项目变更回退', u'tomcat框架项目', '程序回退'
    task_record = AnsibleTaskRecord.objects.get(id=pid)
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    if task_record.app_type not in app_type_dict.keys():
        return HttpResponseRedirect(reverse('auth_forbidden'))
    if request.method == 'POST':
        try:
            switch = request.POST.get('switch')
            backup_file = request.POST.get('backup_file')
            group = task_record.ansible_group
            host_list = task_record.hosts_list.split(',')
            bk_file = '{0}/{1}'.format(task_record.backup_path, backup_file)
            app_name = task_record.app_name
            deploy_path = task_record.app_path
            rollback_path = '{0}/{1}'.format(task_record.app_path, task_record.release_path)
            update_file_type = task_record.update_file_type
            if update_file_type == 'pack':
                task_id, log_file, job_name, inventory  =  tomcat_rollback_pack(group=group, app_name=app_name, deploy_path=deploy_path, bk_file=bk_file, rollback_path=rollback_path, switch=switch, host_list=host_list)
            else:
                task_id, log_file, job_name, inventory  =  tomcat_rollback_config(group=group, app_name=app_name, deploy_path=deploy_path, bk_file=bk_file, rollback_path=rollback_path, switch=switch, host_list=host_list)
            
            AnsibleTaskRecord.objects.filter(id=pid).update(state="rollback")    
            return JsonResponse({"task_id": task_id, 'log_file': log_file, 'job_name':job_name, 'inventory': inventory, 'code': 200})   
        except Exception as err:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 
            return JsonResponse({'error': err, 'code': 500}) 
    
    return render(request, 'tasks/rollback/tomcat_rollback_task.html',locals())


def tomcat_rollback_pack(**kwargs):
    try:
        content = {}
        if kwargs['app_name'] == "abroad-root-tomcat":
            project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['abroad_root_path']
        else:
            project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['tomcat_path']
        role = ansible_role_config.ANSIBLE_TOMCAT_ROLES['tomcat_rollback_pack_task']
        inventory = "{0}/inventory/{1}".format(project_path, kwargs['group'])
        playbook = "{0}/{1}.yml".format(project_path, kwargs['group'])
        vars_file = "{0}/group_vars/{1}.yml".format(project_path, kwargs['group']) 
        job_name = "{0}-code-rollback-{1}".format(kwargs['app_name'], datetime.datetime.now().strftime("%Y%m%d%H%M"))

        """create host"""
        create_ansible_hosts(inventory, playbook, kwargs['group'], role, kwargs['host_list'])
        """创建调用变量"""
        if os.path.exists(vars_file):
            os.remove(vars_file)
        content['deploy_path'] = kwargs['deploy_path']
        content['backup_file'] = kwargs['bk_file']
        content['rollback_war_path'] = kwargs['rollback_path']
        content['reload_control'] = kwargs['switch']
        content['app_name'] = kwargs['app_name']         
        create_ansible_variables(vars_file, content)
        """创建回退task"""
        task_id, log_file = execute_ansible_task(playbook, inventory)
        return task_id, log_file, job_name, inventory
    except:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())       


def tomcat_rollback_config(**kwargs):
    try:
        content = {}
        project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['tomcat_path']
        role = ansible_role_config.ANSIBLE_TOMCAT_ROLES['tomcat_rollback_config_task']
        inventory = "{0}/inventory/{1}".format(project_path, kwargs['group'])
        playbook = "{0}/{1}.yml".format(project_path, kwargs['group'])
        """create host"""
        create_ansible_hosts(inventory, playbook, kwargs['group'], role, kwargs['host_list'])
        vars_file = "{0}/group_vars/{1}.yml".format(project_path, kwargs['group'])
        job_name = "{0}-cfg-rollback-{1}".format(kwargs['app_name'], datetime.datetime.now().strftime("%Y%m%d%H%M"))
        """创建调用变量"""
        if os.path.exists(vars_file):
            os.remove(vars_file)
        content['deploy_path'] = kwargs['deploy_path']
        content['backup_cfg_file'] = kwargs['bk_file']
        content['rollback_cfg_path'] = kwargs['rollback_path']
        content['reload_control'] = kwargs['switch']
        content['app_name'] = kwargs['app_name']        
        create_ansible_variables(vars_file, content)

        """创建回退task"""
        task_id, log_file = execute_ansible_task(playbook, inventory)
        return task_id, log_file, job_name, inventory
    except:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())

