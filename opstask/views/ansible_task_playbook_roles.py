# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from cmdb.models import  ServerInfo, AppInfo, AnsibleGroup
from opstask.models import TaskTemplate, AnsibleTaskRecord, AnsibleTaskList
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from api.ansible import ansible_role_config
from api.views import role_required
from api.views import execute_release_task, get_app_type, execute_ansible_task
from api.opstask.views import PlayCreateTask, TomcatCreateTask
from api.views import create_ansible_variables
from api.views import create_ansible_hosts
from opsadmin.settings import MEDIA_ROOT
import datetime, os
import traceback, logging


# Create your views here.
def generate_ansible_roles(path, group):
    inventory = "{0}/inventory/{1}".format(ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH[path], group)
    playbook = "{0}/{1}.yml".format(ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH[path], group)
    vars_file = "{0}/group_vars/{1}.yml".format(ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH[path], group)
    if os.path.exists(vars_file):
        os.remove(vars_file)
    return  inventory, playbook, vars_file

@login_required(login_url='/login')
@role_required(role='admin')
def create_workflow_task(request):
    path1, path2 = u'项目任务流程', u'创建发布任务'
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    dic = {}
    if request.method == 'POST':
        try:
            task_name = request.POST.get('task_name')
            dic['temp_name'] = task_name
            result = TaskTemplate.objects.filter(temp_name=task_name)
            if not result:
                TaskTemplate.objects.create(**dic)
                msg = '任务创建成功，是否立即编排此任务？'
                return HttpResponse(msg)
            else:
                msg = '任务已存在'
        except Exception as  e:
            return HttpResponse(str(e))
            
    return render(request, 'tasks/jobs/create_workflow_task.html',locals())


@login_required(login_url='/login')
@role_required(role='admin')
def get_ansible_task_type(request):
    if request.method == 'POST':
        try:
            app_name = request.POST.get('app_name')
            arg = request.POST.get('arg')
            app_info = AppInfo.objects.filter(app_name=app_name).first()
            
            if app_info.frameworks == "tomcat":
                if arg == "full":
                    return render(request, 'tasks/tomcat_release.html', {'svn_path': app_info.svn_path, 'upload_path': MEDIA_ROOT})
                elif arg == "diff":
                    return render(request, 'tasks/tomcat_diff_update.html', {'upload_path': MEDIA_ROOT})
                else:
                    return render(request, 'tasks/tomcat_config_update.html', {'upload_path': MEDIA_ROOT})
            else:
                if arg == "full":
                    return render(request, 'tasks/play_release.html', {'svn_path': app_info.svn_path, 'upload_path': MEDIA_ROOT})
                else:
                    return render(request, 'tasks/play_diff_update.html', {'upload_path': MEDIA_ROOT})
        except:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc())               


@login_required(login_url='/login')
@role_required(role='admin')
def ansible_task_create(request):
    path1, path2 = u'项目任务流程', u'创建发布任务'
    try:
        app_list = []
        app_type_dict = get_app_type(request.session.get('name'))
        apps = list(AppInfo.objects.values('app_id', 'app_name', 'app_type', 'app_alias','frameworks', 'app_status'))
        for app_dict in apps:      
            if app_dict['app_status'] == 0 or app_dict['app_type'] == 'private_cloud':
                pass
            else:
                tag_dict = AnsibleTaskRecord.objects.filter(app_name=app_dict['app_name']).values('release_tag').order_by("-release_tag").first()
                if not tag_dict:
                    app_dict['release_tag'] = ""
                else:
                    app_dict['release_tag'] = tag_dict['release_tag']  
                for apps_type_key in app_type_dict.keys():
                    if apps_type_key in app_dict.values():
                        app_list.append(app_dict)
    except Exception as error:
        apps = [{'app_id':0, 'app_name': error, 'app_alias': error, 'frameworks': error}]
    return render(request, 'tasks/release/create_task_list.html',{'path1': path1, 'path2': path2, 'app_list': app_list})


@login_required(login_url='/login')
@role_required(role='admin')
def create_task_tomcat(request, pid):
    path1, path2 = u'项目任务流程', u'创建发布任务'
    apps = AppInfo.objects.get(app_id=pid)
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    if apps.app_type in app_type_dict.keys():
        app_name = apps.app_name
        app_type = apps.app_type
        group = AnsibleGroup.objects.get(app_type=app_type).group
        """检查项目当前状态"""
        if apps.app_status == 3:
           return HttpResponseRedirect(reverse('index'))
        hosts = AppInfo.objects.get(app_name=app_name).app_ip.all()
        app_ip_count = len(hosts)
        task_count = len(AnsibleTaskList.objects.filter(app_name=app_name, task_status=0))
        if task_count < app_ip_count:
            task_state = False
        else:
            task_state = True
    else:
        return HttpResponseRedirect(reverse('auth_forbidden'))
    if request.method == 'POST':
        host_select = request.POST.getlist('host_id_select')
        arg = request.POST.get('arg')
        exe_mode = request.POST.get('exe_mode', '')
        task_detail = request.POST.get('task_detail', '')
        app_ver = request.POST.get('app_ver', '')
        switch = request.POST.get('switch')
        task_name = "{0}-{1}".format(app_name, datetime.datetime.now().strftime("%Y%m%d%H%M"))
        create_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        release_tag = '{0}_{1}'.format(app_ver, create_date)
        svn_path = request.POST.get('svn_path')
        dst_path = request.POST.get('dst_path')
        if dst_path:
            dst_path = ''.join(request.POST.get('dst_path').split())
        action = request.POST.get('action')
        """创建发布任务，不立即执行"""
        if action == "save":
            save_task = {'app_id': pid, 'app_type': app_type, 'app_name': app_name, 'app_version': app_ver, 'creator': username, 'change_logs': task_detail, 'hosts_list': ','.join(host_select),
                         'release_type': arg, 'svn_path': svn_path, 'ansible_group': group, 'reload_switch': switch, 'task_run_type': exe_mode, 'create_time': create_date,
                         "get_code" : request.POST.get('mode_tomcat')}
            try:
                AnsibleTaskList.objects.create(**save_task)
                return JsonResponse({'code': 200})
            except Exception as err:
                logg = logging.getLogger('opsadmin')
                logg.error('%s' % traceback.format_exc()) 
                return JsonResponse({'error':str(err), 'code': 500}) 
        else:
            """创建发布任务，立即执行"""
            try:
                if apps.app_name in set(ansible_role_config.UNIQUE_APP_LIST):
                    inventory, playbook, vars_file = generate_ansible_roles('abroad_root_path', group)
                else:    
                    inventory, playbook, vars_file = generate_ansible_roles('tomcat_path', group)
                """delete old variables if exists, for safety"""
                if os.path.exists(vars_file):
                    os.remove(vars_file)
                task_create = TomcatCreateTask(app_type, app_name, group, inventory, playbook, vars_file, exe_mode, host_select, create_date)
                if arg == "full":
                    mode = request.POST.get('mode_tomcat')
                    if mode == "svn":
                        task_create.tomcat_full_release_task(mode, svn_path=svn_path, switch=switch, username=username, app_ver=app_ver)
                    elif mode == "trans":
                        trans_path = "{0}/{1}".format(MEDIA_ROOT, app_name)
                        task_create.tomcat_full_release_task(mode, trans_path=trans_path, switch=switch, username=username, app_ver=app_ver)
                elif arg == "diff":
                    mode = request.POST.get('mode_t_jar')
                    if mode == "add":
                        if not dst_path.split('/')[-1]:
                            dst_path = dst_path[:-1] 
                        task_create.tomcat_increment_update_task(mode, dst_path=dst_path, switch=switch, username=username, app_ver=app_ver)
                    elif mode == "del":
                        if not dst_path.split('/')[-1]:
                            dst_path = dst_path[:-1] 
                        del_file = request.POST.get('del_file')
                        task_create.tomcat_increment_update_task(mode, dst_path=dst_path, switch=switch, del_file=del_file, username=username, app_ver=app_ver)
                    elif mode == "iter":
                        if not dst_path.split('/')[-1]:
                            dst_path = dst_path[:-1]
                        old_file = request.POST.get('old_file')
                        new_file = request.POST.get('new_file')
                        task_create.tomcat_increment_update_task(mode, dst_path=dst_path, switch=switch, old_file=old_file, new_file=new_file, username=username, app_ver=app_ver)
                else:
                    mode = request.POST.get('mode_t_cfg')
                    if mode == "add":
                        add_arg = request.POST.get('add_arg')
                        task_create.tomcat_config_update_task(mode, add_config=add_arg, switch=switch, username=username, app_ver=app_ver)
                    elif mode == "mod":
                        mod_arg = request.POST.get('mod_arg')
                        task_create.tomcat_config_update_task(mode, mod_config=mod_arg, switch=switch, username=username, app_ver=app_ver)
                """执行发布任务"""
                data = execute_release_task(playbook, inventory, task_name, app_type, task_detail, pid, release_tag)
                AppInfo.objects.filter(app_id=pid).update(app_status=3)
                return JsonResponse(data, safe=False)
            except Exception as err:
                logg = logging.getLogger('opsadmin')
                logg.error('%s' % traceback.format_exc()) 
                return JsonResponse({'error':str(err), 'code': 500})                                           
    return render(request, 'tasks/release/task_create_tomcat.html', {'path1': path1, 'path2': path2, 'app_type': app_type,'app_name': app_name ,'app_id': apps.app_id, 'task_state': task_state, 'hosts': hosts})

@login_required(login_url='/login')
@role_required(role='admin')
def create_task_play(request, pid):
    path1, path2 = u'项目任务流程', u'创建发布任务'
    apps = AppInfo.objects.get(app_id=pid)
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    if apps.app_type in app_type_dict.keys():
        app_name = apps.app_name
        app_type = apps.app_type
        group = AnsibleGroup.objects.get(app_type=app_type).group
        """检查项目当前状态"""
        if apps.app_status == 3:
           return HttpResponseRedirect(reverse('index')) 
        #task_state = AnsibleTaskList.objects.filter(app_name=app_name, task_status=0)
        hosts = AppInfo.objects.get(app_name=app_name).app_ip.all()
        app_ip_count = len(hosts)
        task_count = len(AnsibleTaskList.objects.filter(app_name=app_name, task_status=0))
        if task_count < app_ip_count:
            task_state = False
        else:
            task_state = True
    else:
        return HttpResponseRedirect(reverse('auth_forbidden'))
    if request.method == 'POST':
        host_select = request.POST.getlist('host_id_select')
        arg = request.POST.get('arg')
        exe_mode = request.POST.get('exe_mode', '')
        task_detail = request.POST.get('task_detail', '')
        app_ver = request.POST.get('app_ver', '')
        switch = request.POST.get('switch')
        task_name = "{0}-{1}".format(app_name, datetime.datetime.now().strftime("%Y%m%d%H%M"))            
        inventory, playbook, vars_file = generate_ansible_roles('play_path', group)
        create_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        release_tag = "{0}_{1}".format(app_ver, create_date)
        action = request.POST.get('action')
        svn_path = request.POST.get('svn_path')
        """创建发布任务，不立即执行"""
        if action == "save":
            save_task = {'app_id': pid, 'app_name': app_name, 'app_type': app_type, 'app_version': app_ver, 'creator': username, 'change_logs': task_detail, 'hosts_list': ','.join(host_select),
                         'release_type': arg, 'svn_path': svn_path, 'ansible_group': group, 'reload_switch': switch, 'task_run_type': exe_mode, 'create_time': create_date, 
                         'get_code': request.POST.get('mode_play')}
            try:
                AnsibleTaskList.objects.create(**save_task)
                return JsonResponse({'code': 200})
            except Exception as err:
                logg = logging.getLogger('opsadmin')
                logg.error('%s' % traceback.format_exc()) 
                return JsonResponse({'error':str(err), 'code': 500})
        else:
            """创建发布任务，立即执行"""       
            try:
                """delete old variables if exists, for safety"""
                if os.path.exists(vars_file):
                    os.remove(vars_file)
                task_create = PlayCreateTask(app_type, app_name, group, inventory, playbook, vars_file, exe_mode, host_select, create_date)
                if arg == "full":
                    mode = request.POST.get('mode_play')
                    if mode == "svn":
                        task_create.play_full_release_task(mode, svn_path=svn_path, switch=switch, username=username, app_ver=app_ver)
                    elif mode == "trans":
                        trans_path = "{0}/{1}".format(MEDIA_ROOT, app_name)
                        task_create.play_full_release_task(mode, trans_path=trans_path, switch=switch, username=username, app_ver=app_ver)        
                elif arg == "diff":
                    mode = request.POST.get('mode_play_jar')
                    if mode == "add":
                        lib = request.POST.get('lib_type')
                        plugins = request.POST.get('plugins_type')
                        task_create.play_increment_update_task(mode=mode, lib=lib, plugins=plugins, switch=switch, username=username, app_ver=app_ver)
                    elif mode == "iter":
                        old_file = request.POST.get('old_file', '')
                        new_file = request.POST.get('new_file', '')
                        dst_path = request.POST.get('dst_path', '')
                        task_create.play_increment_update_task(mode=mode, dst_path=dst_path, old_file=old_file, new_file=new_file, switch=switch, username=username, app_ver=app_ver)
                """执行发布任务"""
                data = execute_release_task(playbook, inventory, task_name, app_type, task_detail, pid, release_tag)
                AppInfo.objects.filter(app_id=pid).update(app_status=3)
                return JsonResponse(data, safe=False)
            except Exception as err:
                logg = logging.getLogger('opsadmin')
                logg.error('%s' % traceback.format_exc()) 
                return JsonResponse({'error':str(err), 'code': 500})                                           
    return render(request, 'tasks/release/task_create_play.html', {'path1': path1, 'path2': path2, 'app_type': app_type,'app_name': app_name ,'app_id': apps.app_id, 'task_state': task_state, 'hosts': hosts})


@login_required(login_url='/login')
@role_required(role='admin')
def create_process_control_task(request, pid):
    path1, path2 = u'项目任务流程', u'应用重启'
    apps = AppInfo.objects.get(app_id=pid)
    username = request.session.get('name')
    app_type_dict = get_app_type(username)
    if apps.app_type in app_type_dict.keys():
        app_name = apps.app_name
        app_id = apps.app_id
        app_type = apps.app_type
        group = AnsibleGroup.objects.get(app_type=app_type).group
        hosts = AppInfo.objects.get(app_name=app_name).app_ip.all()
        """检查项目当前状态"""
        if apps.app_status == 3:
           return HttpResponseRedirect(reverse('index'))
       
    else:
        return HttpResponseRedirect(reverse('auth_forbidden'))
    if request.method == 'POST':
        try:
            content = {}
            """ansible task path"""
            host_select = request.POST.getlist('host_id_select')
            switch = request.POST.get('switch', '')
            exe_mode = request.POST.get('exe_mode', '')
            job_name = "{0}-{1}".format(app_name, datetime.datetime.now().strftime("%Y%m%d%H%M"))
            if  apps.frameworks == "play":
                inventory, playbook, vars_file = generate_ansible_roles('play_path', group)
                task_role = ansible_role_config.ANSIBLE_PLAY_ROLES['play_restart_task']
                content['play_path'] = apps.main_path
                content['play_name'] = app_name
                content['play_port'] = apps.run_port
            else:    
                inventory, playbook, vars_file = generate_ansible_roles('tomcat_path', group)
                task_role = ansible_role_config.ANSIBLE_TOMCAT_ROLES['tomcat_restart_task']
                content['deploy_path'] = apps.main_path
                content['app_name'] = app_name
            """创建主机资源组"""
            create_ansible_hosts(inventory, playbook, group, task_role, host_select, exe_mode=exe_mode) 
            content['reload_control'] = switch
            """create variables"""    
            create_ansible_variables(vars_file, content)
            task_id, log_file = execute_ansible_task(playbook, inventory)
            AppInfo.objects.filter(app_id=pid).update(app_status=3)
            return JsonResponse({"task_id": task_id, 'log_file': log_file,  'app_type':app_type, 'job_name':job_name, 'inventory': inventory, 'pid': pid, 'code': 200})
        except Exception as err:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 
            return JsonResponse({'error':str(err), 'code': 500})  
    return render(request, 'tasks/restart/create_restart_task.html',locals())


def ansible_task_manager(request, pid=None, action=None):
    path1, path2 = u'项目任务流程', u'发布任务列表'
    username = request.session.get('name')
    if request.session.get('role_id') == 0:
        task_list = AnsibleTaskList.objects.all()
    else:
        task_list = AnsibleTaskList.objects.filter(creator=username)
    """发布任务,或取消发布任务"""
    if pid:        
        if action == "excute" and request.is_ajax():
            """任务发布"""
            task = AnsibleTaskList.objects.filter(id=pid).first()
            app_framwork = AppInfo.objects.filter(app_name=task.app_name).first()
            create_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            release_tag = "{0}_{1}".format(task.app_version, create_date)
            task_name = "{0}-{1}".format(task.app_name, datetime.datetime.now().strftime("%Y%m%d%H%M"))
            host_select = task.hosts_list.split(',')
            """tomcat框架项目发布"""
            if app_framwork.frameworks == 'tomcat':
                try:
                    if task.app_name in set(ansible_role_config.UNIQUE_APP_LIST):
                        inventory, playbook, vars_file = generate_ansible_roles('abroad_root_path', task.ansible_group)
                    else:    
                        inventory, playbook, vars_file = generate_ansible_roles('tomcat_path', task.ansible_group)
                    """delete old variables if exists, for safety"""
                    if os.path.exists(vars_file):
                        os.remove(vars_file)
                    task_create = TomcatCreateTask(task.app_type, task.app_name, task.ansible_group, inventory, playbook, vars_file, task.task_run_type, host_select, create_date)
                    if task.release_type == "full":
                        if task.get_code == "svn":
                            task_create.tomcat_full_release_task(task.get_code, svn_path=task.svn_path, switch=task.reload_switch, username=username, app_ver=task.app_version)
                        elif task.get_code == "trans":
                            trans_path = "{0}/{1}".format(MEDIA_ROOT, task.app_name)
                            task_create.tomcat_full_release_task(task.get_code, trans_path=trans_path, switch=task.reload_switch, username=username, app_ver=task.app_version)
                    """执行发布任务"""
                    data = execute_release_task(playbook, inventory, task_name, task.app_type, task.change_logs, task.app_id, release_tag)
                    AppInfo.objects.filter(app_id=task.app_id).update(app_status=3)
                    AnsibleTaskList.objects.filter(id=pid).update(task_status=1)
                    return JsonResponse(data, safe=False)
                except Exception as err:
                    logg = logging.getLogger('opsadmin')
                    logg.error('%s' % traceback.format_exc()) 
                    return JsonResponse({'error':str(err), 'code': 500}) 
            else:
                try:
                    inventory, playbook, vars_file = generate_ansible_roles('play_path', task.ansible_group)
                    if os.path.exists(vars_file):
                        os.remove(vars_file)
                    task_create = PlayCreateTask(task.app_type, task.app_name, task.ansible_group, inventory, playbook, vars_file, task.task_run_type, host_select, create_date)
                    if task.release_type == "full":
                        if task.get_code == "svn":
                            task_create.play_full_release_task(task.get_code, svn_path=task.svn_path, switch=task.reload_switch, username=username, app_ver=task.app_version)
                        elif task.get_code == "trans":
                            trans_path = "{0}/{1}".format(MEDIA_ROOT, task.app_name)
                            task_create.play_full_release_task(task.get_code, trans_path=trans_path, switch=task.reload_switch, username=username, app_ver=task.app_version)        
                    """执行发布任务"""
                    data = execute_release_task(playbook, inventory, task_name, task.app_type, task.change_logs, task.app_id, release_tag)
                    AppInfo.objects.filter(app_id=task.app_id).update(app_status=3)
                    AnsibleTaskList.objects.filter(id=pid).update(task_status=1)
                    return JsonResponse(data, safe=False)
                except Exception as err:
                    logg = logging.getLogger('opsadmin')
                    logg.error('%s' % traceback.format_exc()) 
                    return JsonResponse({'error':str(err), 'code': 500})                 
        elif action == "cancel":
            """取消任务发布"""
            AnsibleTaskList.objects.filter(id=pid).update(task_status=2)
            return HttpResponseRedirect(reverse('task_sheet_list'))    
        return render(request, 'tasks/release/task_excute.html', locals())
    return render(request, 'tasks/release/task_sheet_list.html',{'path1': path1, 'path2': path2, 'task_list': task_list})