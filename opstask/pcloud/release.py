# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from cmdb.models import AnsibleGroup, AppInfo
from api.views import create_ansible_variables
from api.views import create_ansible_hosts
from api.pcloud.views import pcloud_execute_ansible_job
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from api.views import role_required, get_app_type
from api.ansible import ansible_role_config
from opsadmin.settings import MEDIA_ROOT
import traceback, logging
from tempfile import NamedTemporaryFile
from api.tasks import *
import datetime
import os

# Create your views here.
"""pcloud全量发布"""

@login_required(login_url='/login')
@role_required(role='admin')
def pcloud_release_code(request):
    path1, path2, path3 = u'项目平台更新', u'私有云项目', '全量发布源码'
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    app_info_list = AppInfo.objects.filter(app_type="private_cloud").values('backup_path','work_path').distinct()
    job_name = "private_cloud-full-release-{0}".format(datetime.datetime.now().strftime("%Y%m%d%H%M"))
    app_type = ansible_role_config.PCLOUD_APP_TYPE[0]
    """"auth check"""
    if len(set(app_type_dict.keys()).intersection(set(ansible_role_config.PCLOUD_APP_TYPE))) == 0:
        if username == "管理员":
            pass
        else:
            return render(request, 'error/403.html')
    if request.method == 'POST':
        try:
            content = {}
            root_list = []    #define root program list
            service_list = [] #define service program list
            interface_list = []
            """ansible task path"""
            curr_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['pcloud_path']
            group = request.POST.get('ab_group', '')
            root_path = request.POST.getlist('root_path')
            service_path = request.POST.getlist('service_path')
            interface_path = request.POST.getlist('interface_path')
            pcloud = request.POST.getlist('pcloud')
            action = request.POST.get('action')
            arg = request.POST.get('arg', '')
            exe_mode = request.POST.get('exe_mode', '')
            switch = request.POST.get('switch')
            inventory = "{0}/inventory/{1}".format(project_path, group)
            playbook = "{0}/{1}.yml".format(project_path, group)
            vars_file = "{0}/group_vars/{1}.yml".format(project_path, group)
            content['curr_dt'] = curr_date
            content['reload_app'] = switch
            """创建调用变量"""
            """delete old variables if exists, for safety"""
            if os.path.exists(vars_file):
                os.remove(vars_file)
            if root_path:
                for root in root_path:
                    root_list.append(root.encode('utf8'))
                content['root_path'] = root_list
            if service_path:
                for service in service_path:
                    service_list.append(service.encode('utf8'))
                content['service_path'] = service_list
            if interface_path:
                for interface in interface_path:
                    interface_list.append(interface.encode('utf8'))
                content['interface_path'] = interface_list
            for app in app_info_list:
                content['code_workspace'] = app['work_path']
                content['bk_path'] = app['backup_path']
            if arg == "svn":
                task_role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_svn_release_task']
                """创建主机资源组"""
                create_ansible_hosts(inventory, playbook, group, task_role, "pcloud", exe_mode=exe_mode)
                content['svn_path'] = pcloud[0]
                if pcloud[1]:
                    content['svn_service'] = pcloud[1]
                if pcloud[2]:
                    content['svn_root'] = pcloud[2]
                if pcloud[3]:
                    content['svn_interface'] = pcloud[3]

                """create variables"""              
                create_ansible_variables(vars_file, content)
            elif arg == 'trans':
                task_role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_trans_release_task']
                """创建主机资源组"""
                create_ansible_hosts(inventory, playbook, group, task_role, "pcloud", exe_mode=exe_mode)
                content['trans_path'] = "{0}/{1}".format(MEDIA_ROOT, app_type)
                """create variables"""              
                create_ansible_variables(vars_file, content)
            task_id, log_file = pcloud_execute_ansible_job(playbook, inventory)
            return JsonResponse({"task_id": task_id, 'log_file': log_file, 'job_name':job_name, 'inventory': inventory, 'code': 200})
        except Exception as  err:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 
            return JsonResponse({'error':str(err), 'code': 500})
    
    return render(request, 'pcloud/release/release_code.html',locals())



"""pcloud动态文件批量更新 jar"""
@login_required(login_url='/login')
@role_required(role='admin')
def pcloud_increment_release_code(request):
    path1, path2, path3 = u'项目平台更新', u'私有云项目', '增量更新程序'
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    app_info_list = AppInfo.objects.filter(app_type="private_cloud").values('backup_path','work_path').distinct()
    job_name = "private_cloud-jar-update-{0}".format(datetime.datetime.now().strftime("%Y%m%d%H%M"))
    app_type = ansible_role_config.PCLOUD_APP_TYPE[0]
    """"auth check"""
    if len(set(app_type_dict.keys()).intersection(set(ansible_role_config.PCLOUD_APP_TYPE))) == 0:
        if username == "管理员":
            pass
        else:
            return render(request, 'error/403.html')
    if request.method == 'POST':
        try:
            content = {}
            root_list = [] #define root program list
            service_list = [] #define service program list
            interface_list = []
            """ansible task path"""
            curr_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['pcloud_path']
            group = request.POST.get('ab_group', '')
            root_path = request.POST.getlist('root_path')
            service_path = request.POST.getlist('service_path')
            interface_path = request.POST.getlist('interface_path')
            dst_path = request.POST.get('dst_path')
            mode = request.POST.get('mode')
            exe_mode = request.POST.get('exe_mode', '')
            switch = request.POST.get('switch')
            """"define ansible task role file"""
            inventory = "{0}/inventory/{1}".format(project_path, group)
            playbook = "{0}/{1}.yml".format(project_path, group)
            vars_file = "{0}/group_vars/{1}.yml".format(project_path, group)
            """创建调用变量dict"""
            content['dst_path'] = ''.join(dst_path.split())
            content['curr_dt'] = curr_date
            content['reload_jar'] = switch
            """delete old variables if exists, for safety"""
            if os.path.exists(vars_file):
                os.remove(vars_file)
            for app in app_info_list:
                content['bk_path'] = app['backup_path']
                content['code_workspace'] = app['work_path']
            if root_path:
                for root in root_path:
                    root_list.append(root.encode('utf8'))
                content['root_path'] = root_list
            if service_path:
                for service in service_path:
                    service_list.append(service.encode('utf8'))
                content['service_path'] = service_list
            if interface_path:
                for interface in interface_path:
                    interface_list.append(interface.encode('utf8'))
                content['interface_path'] = interface_list

            """"define update scene"""
            if mode == 'add':
                content['local_path'] = "{0}/{1}".format(MEDIA_ROOT, app_type)
                content['add_file'] = '"None"'
                """创建主机资源组"""
                task_role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_jar_add_task']
                create_ansible_hosts(inventory, playbook, group, task_role, "pcloud", exe_mode=exe_mode)                
            elif mode == 'del':
                del_file = request.POST.get('del_file').split('\r')
                content['del_file'] = '"%s"' % ''.join(del_file)
                task_role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_jar_delete_task']
                create_ansible_hosts(inventory, playbook, group, task_role, exe_mode=exe_mode) 
            elif mode == 'iter':
                old_file = request.POST.get('old_file').strip()
                new_file = request.POST.get('new_file').strip()
                content['old_file'] = old_file
                content['new_file'] = new_file
                content['local_path'] = "{0}/{1}".format(MEDIA_ROOT, app_type)
                task_role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_jar_add_task']
                create_ansible_hosts(inventory, playbook, group, task_role, "pcloud", exe_mode=exe_mode) 
        
            """create variables file"""              
            create_ansible_variables(vars_file, content)
            """"execute ansible job"""
            task_id, log_file = pcloud_execute_ansible_job(playbook, inventory)
            return JsonResponse({"task_id": task_id, 'log_file': log_file, 'job_name':job_name, 'inventory': inventory, 'code': 200})
        except Exception as err:
            return JsonResponse({'error':str(err), 'code': 500})
    
    return render(request, 'pcloud/update/increment_release_code.html',locals())


"""pcloud配置文件批量更新"""
@login_required(login_url='/login')
@role_required(role='admin')
def pcloud_release_config(request):
    path1, path2, path3 = u'项目平台更新', u'私有云项目', '配置文件更新'
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    app_info_list = AppInfo.objects.filter(app_type="private_cloud").values('backup_path','work_path').distinct()
    job_name = "private_cloud-cfg-update-{0}".format(datetime.datetime.now().strftime("%Y%m%d%H%M"))
    app_type = ansible_role_config.PCLOUD_APP_TYPE[0]
    """"auth check"""
    if len(set(app_type_dict.keys()).intersection(set(ansible_role_config.PCLOUD_APP_TYPE))) == 0:
        if username == "管理员":
            pass
        else:
            return render(request, 'error/403.html')
    if request.method == 'POST':
        try:
            content = {}
            root_list = [] #define root program list
            service_list = [] #define service program list
            interface_list = []
            """ansible task path"""
            project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['pcloud_path']
            curr_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            group = request.POST.get('ab_group', '')
            root_path = request.POST.getlist('root_path')
            service_path = request.POST.getlist('service_path')
            interface_path = request.POST.getlist('interface_path')
            arg = request.POST.get('arg')
            switch = request.POST.get('switch')
            exe_mode = request.POST.get('exe_mode', '')
            """"define ansible task role file"""
            inventory = "{0}/inventory/{1}".format(project_path, group)
            playbook = "{0}/{1}.yml".format(project_path, group)
            vars_file = "{0}/group_vars/{1}.yml".format(project_path, group)
            """创建调用变量"""
            """delete old variables if exists, for safety"""
            if os.path.exists(vars_file):
                os.remove(vars_file)            
            if arg == "add":
                #批量添加固定参数
                fix_arg = request.POST.get('add_arg').split('\r')
                content['fix_arg'] = '"%s"' % ''.join(fix_arg)
                """创建主机资源组"""
                task_role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_config_add_task']               
                create_ansible_hosts(inventory, playbook, group, task_role, "pcloud", exe_mode=exe_mode)
            elif arg == 'add_p':
                #批量添加变量参数
                batch_arg = request.POST.get('add_p_arg').split('\r')
                content['batch_arg'] =  '"%s"' % '\n'.join(batch_arg)
                """创建主机资源组"""
                task_role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_config_add_task']
                create_ansible_hosts(inventory, playbook, group, task_role, "pcloud", exe_mode=exe_mode) 
            elif arg == 'del':
                express_del = request.POST.get('del_arg')
                content['express_del'] = express_del
                """创建主机资源组"""
                task_role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_config_delete_task']
                create_ansible_hosts(inventory, playbook, group, task_role, "pcloud", exe_mode=exe_mode) 
            else:
                express_mod = request.POST.get('mod_arg')
                content['express_mod'] = express_mod
                """创建主机资源组"""
                task_role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_config_mod_task']
                create_ansible_hosts(inventory, playbook, group, task_role, "pcloud", exe_mode=exe_mode)  

            if root_path:
                for root in root_path:
                    root_list.append(root.encode('utf8'))
                content['root_path'] = root_list
            if service_path:
                for service in service_path:
                    service_list.append(service.encode('utf8'))
                content['service_path'] = service_list
            if interface_path:
                for interface in interface_path:
                    interface_list.append(interface.encode('utf8'))
                content['interface_path'] = interface_list
            for app in app_info_list:
                content['bk_path'] = app['backup_path']
            content['curr_dt'] = curr_date
            content['root_path'] = root_list
            content['service_path'] = service_list
            content['config_file'] = '{0}/{1}'.format(ansible_role_config.TOMCAT_FRAMEWORK['config'], ansible_role_config.TOMCAT_CONFIG_TYPE['app'])
            content['reload_cfg'] = switch
            """create variables file"""              
            create_ansible_variables(vars_file, content)
            """"execute ansible job"""
            task_id, log_file = pcloud_execute_ansible_job(playbook, inventory)
            return JsonResponse({"task_id": task_id, 'log_file': log_file, 'job_name':job_name, 'inventory': inventory, 'code': 200})
        except Exception as err:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 
            return JsonResponse({'error':str(err), 'code': 500})
    
    return render(request, 'pcloud/update/release_config.html',locals())

@login_required(login_url='/login')
@role_required(role='admin')
def pcloud_restart_process(request):
    path1, path2, path3 = u'项目平台更新', u'私有云项目', '批量重启服务'
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    job_name = "private_cloud-restart-{0}".format(datetime.datetime.now().strftime("%Y%m%d%H%M"))
    app_type = ansible_role_config.PCLOUD_APP_TYPE[0]
    """"auth check"""
    if len(set(app_type_dict.keys()).intersection(set(ansible_role_config.PCLOUD_APP_TYPE))) == 0:
        if username == "管理员":
            pass
        else:
            return render(request, 'error/403.html')
    if request.method == 'POST':
        try:
            content = {}
            root_list = [] #define root program list
            service_list = [] #define service program list
            interface_list = []
            """ansible task path"""
            curr_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['pcloud_path']
            group = request.POST.get('ab_group', '')
            root_path = request.POST.getlist('root_path')
            service_path = request.POST.getlist('service_path')
            interface_path = request.POST.getlist('interface_path')
            switch = request.POST.get('switch', '')
            exe_mode = request.POST.get('exe_mode', '')
            inventory = "{0}/inventory/{1}".format(project_path, group)
            playbook = "{0}/{1}.yml".format(project_path, group)
            vars_file = "{0}/group_vars/{1}.yml".format(project_path, group)
            """创建主机资源组"""
            task_role = ansible_role_config.ANSIBLE_PCLOUD_ROLES['pcloud_restart_task']
            create_ansible_hosts(inventory, playbook, group, task_role, "pcloud", exe_mode=exe_mode) 
            """创建调用变量"""
            """delete old variables if exists, for safety"""
            if os.path.exists(vars_file):
                os.remove(vars_file)
            if root_path:
                for root in root_path:
                    root_list.append(root.encode('utf8'))
                content['root_path'] = root_list
            if service_path:
                for service in service_path:
                    service_list.append(service.encode('utf8'))
                content['service_path'] = service_list
            if interface_path:
                for interface in interface_path:
                    interface_list.append(interface.encode('utf8'))
                content['interface_path'] = interface_list
            content['reload_do'] = switch
            """create variables"""    
            create_ansible_variables(vars_file, content)
            task_id, log_file = pcloud_execute_ansible_job(playbook, inventory)
            return JsonResponse({"task_id": task_id, 'log_file': log_file,  'job_name':job_name, 'inventory': inventory, 'code': 200})
        except Exception as err:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 
            return JsonResponse({'error':str(err), 'code': 500})  
    return render(request, 'pcloud/restart/restart_process.html',locals())


@role_required(role='admin')
def pcloud_get_app_list(request):
    """获取部署路径"""
    app_type = request.GET.get('app_type')
    app = request.GET.get('app')
    if app == "root":
        app_list = AppInfo.objects.filter(app_type=app_type)
        return render(request, 'pcloud/root_list.html',locals())
    if app == "service":
        app_list = AppInfo.objects.filter(app_type=app_type)
        return render(request, 'pcloud/service_list.html',locals())
    if app == "interface":
        app_list = AppInfo.objects.filter(app_type=app_type)
        return render(request, 'pcloud/interface_list.html',locals())    


@login_required(login_url='/login')
@role_required(role='admin')
def pcloud_get_ansible_group(request):
    """get ansible group"""
    ansible_group = AnsibleGroup.objects.filter(app_type="private_cloud").values('group','comment')
    group_list = []
    for group_dict in ansible_group:
        ip_list = AnsibleGroup.objects.get(group=group_dict['group']).serverinfos.all()
        ips = []
        for ip in ip_list:
            ips.append(str(ip))
        group_dict['ip_set'] = ','.join(ips)
        group_list.append(group_dict)
    return render(request, 'pcloud/group_list.html',locals())
