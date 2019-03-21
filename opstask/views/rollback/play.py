# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from cmdb.models import AppInfo
from api.views import role_required
from api.views import create_ansible_hosts, execute_ansible_task
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from api.views import get_app_type
from django.core.urlresolvers import reverse
from api.ansible import ansible_role_config
import datetime, os
from opstask.models import AnsibleTaskRecord
from api.views import create_ansible_variables
import logging
import traceback

"""支付框架程序回退"""
@login_required(login_url='/login')
@role_required(role='admin')
def play_rollback_task(request, pid):
    path1, path2, path3 = u'项目变更回退', u'play框架项目', '程序回退'
    task_record = AnsibleTaskRecord.objects.get(id=pid)
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    if task_record.app_type not in app_type_dict.keys():
        return HttpResponseRedirect(reverse('auth_forbidden'))
    if request.method == 'POST':
        try:
            content = []
            switch = request.POST.get('switch')
            backup_file = request.POST.get('backup_file')
            update_file_type = task_record.update_file_type
            app_data = AppInfo.objects.filter(app_name=task_record.app_name).first()
            app_port = app_data.run_port
            """创建调用变量"""

            if update_file_type == 'pack':
                task_id, log_file, job_name, inventory = play_rollback_pack(group=task_record.ansible_group, app_name=task_record.app_name,
                                                                            release_path=task_record.release_path, backup_path=task_record.backup_path,
                                                                            backup_file=backup_file, app_path=task_record.app_path,
                                                                            app_port=app_port, switch=switch, host_list=task_record.hosts_list.split(','))                 
            else:
                task_id, log_file, job_name, inventory = play_rollback_config(group=task_record.ansible_group, app_name=task_record.app_name,
                                                                            release_path=task_record.release_path,backup_path=task_record.backup_path,
                                                                            backup_file=backup_file, app_path=task_record.app_path,
                                                                            app_port=app_port, switch=switch, host_list=task_record.hosts_list.split(','))

            """创建回退task"""
            AnsibleTaskRecord.objects.filter(id=pid).update(state="rollback")
            return JsonResponse({"task_id": task_id, 'log_file': log_file, 'job_name':job_name, 'inventory': inventory, 'code': 200}) 
        except Exception as err:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 
            return JsonResponse({'error': err, 'code': 500})
    return render(request, 'tasks/rollback/play_rollback_task.html',locals())


def play_rollback_pack(**kwargs):
    try:
        content = {}
        project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['play_path']
        role = ansible_role_config.ANSIBLE_PLAY_ROLES['play_rollback_task']
        inventory = "{0}/inventory/{1}".format(project_path, kwargs['group'])
        playbook = "{0}/{1}.yml".format(project_path, kwargs['group'])
        vars_file = "{0}/group_vars/{1}.yml".format(project_path, kwargs['group']) 
        job_name = "{0}-war-rollback-{1}".format(kwargs['app_name'], datetime.datetime.now().strftime("%Y%m%d%H%M")) 

        """create host"""
        create_ansible_hosts(inventory, playbook, kwargs['group'], role, kwargs['host_list'])
        """创建调用变量"""
        if os.path.exists(vars_file):
            os.remove(vars_file)
        if len(kwargs['release_path'].split(',')) == 2:
            content['play_plugins_rollback'] = kwargs['release_path'].split(',')[0]
            content['play_lib_rollback'] = kwargs['release_path'].split(',')[1]
            content['plugins_bk_file'] = '{0}/{1}'.format(kwargs['backup_path'], kwargs['backup_file'].split(',')[0])
            content['lib_bk_file'] = '{0}/{1}'.format(kwargs['backup_path'], kwargs['backup_file'].split(',')[1])
        else:
            if 'lib' in kwargs['backup_file'] and 'incr' in kwargs['backup_file']:
                content['play_lib_rollback'] = kwargs['release_path']
                content['lib_bk_file'] = '{0}/{1}'.format(kwargs['backup_path'], kwargs['backup_file'])
            elif 'plugins' in kwargs['backup_file'] and 'incr' in kwargs['backup_file']:
                content['play_plugins_rollback'] = kwargs['release_path']
                content['plugins_bk_file'] = '{0}/{1}'.format(kwargs['backup_path'], kwargs['backup_file'])
            elif 'lib' in kwargs['backup_file'] and 'iter' in kwargs['backup_file']:
                content['play_lib_rollback'] = kwargs['release_path']
                content['lib_bk_file'] = '{0}/{1}'.format(kwargs['backup_path'], kwargs['backup_file'])
            elif 'plugins' in kwargs['backup_file'] and 'iter' in kwargs['backup_file']:
                content['play_plugins_rollback'] = kwargs['release_path']
                content['plugins_bk_file'] = '{0}/{1}'.format(kwargs['backup_path'], kwargs['backup_file']) 
        content['reload_control'] = kwargs['switch']
        content['play_name'] = kwargs['app_name']
        content['play_port'] = kwargs['app_port']
        content['play_path'] = kwargs['app_path']       
        create_ansible_variables(vars_file, content)
        """创建回退task"""
        task_id, log_file = execute_ansible_task(playbook, inventory)
        return task_id, log_file, job_name, inventory
    except:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())   

def play_rollback_config(**kwargs):
    try:
        content = {}
        project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['play_path']
        role = ansible_role_config.ANSIBLE_PLAY_ROLES['play_rollback_task']
        inventory = "{0}/inventory/{1}".format(project_path, kwargs['group'])
        playbook = "{0}/{1}.yml".format(project_path, kwargs['group'])
        vars_file = "{0}/group_vars/{1}.yml".format(project_path, kwargs['group']) 
        job_name = "{0}-config-rollback-{1}".format(kwargs['app_name'], datetime.datetime.now().strftime("%Y%m%d%H%M")) 

        """create host"""
        create_ansible_hosts(inventory, playbook, kwargs['group'], role, kwargs['host_list'])
        """创建调用变量"""
        if os.path.exists(vars_file):
            os.remove(vars_file)
        content['play_config'] = kwargs['release_path']
        content['play_bk_config'] = '{0}/{1}'.format(kwargs['backup_path'], kwargs['backup_file'])
        content['reload_control'] = kwargs['switch']
        content['play_name'] = kwargs['app_name']
        content['play_port'] = kwargs['app_port']
        content['play_path'] = kwargs['app_path']
        content['reload_control'] = kwargs['switch']    
        create_ansible_variables(vars_file, content)
        """创建回退task"""
        task_id, log_file = execute_ansible_task(playbook, inventory)
        return task_id, log_file, job_name, inventory
    except:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())  


