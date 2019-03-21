# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
from api.views import create_ansible_hosts
from api.views import get_app_type
from django.contrib.auth.decorators import login_required
from api.play.views import CreatePlayVariables
from api.views import role_required, execute_release_task, get_app_detail
from opstask.models import AnsibleTaskRecord
from opsadmin.settings import MEDIA_ROOT
from api.ansible import ansible_role_config
from cmdb.models import AnsibleGroup, AppInfo
import datetime
import json, os
import traceback, logging

# Create your views here.
"""支付接口配置增量更新"""
@login_required(login_url='/login')
@role_required(role='admin')
def play_release_config(request):
    path1, path2, path3 = u'项目平台更新', u'play框架项目', '增量发布配置'
    username = request.session.get('name')
    file_path = MEDIA_ROOT
    play_config = ansible_role_config.PLAY_CONFIG_FILE
    app_type_dict = get_app_type(username)
    play_app_type = ['pay']
    hosts = AppInfo.objects.get(app_type=play_app_type[0]).app_ip.all()
    """"auth check"""
    if len(set(app_type_dict.keys()).intersection(set(play_app_type))) == 0:
        if username == "管理员":
            pass
        else:
            return render(request, 'error/403.html')
    if request.method == 'POST':
        try:
            curr_dt = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            project_path = ansible_role_config.ANSIBLE_PLAYBOOK_REPOSITORY_PATH['play_path']
            group = request.POST.get('ab_group', '')
            host_select = request.POST.getlist('host_id_select')
            app_name = request.POST.get('app_name')
            cfg = request.POST.get('config')
            switch = request.POST.get('switch')
            app_type = request.POST.get('app_type', '')
            inventory = "{0}/inventory/{1}".format(project_path, group)
            playbook = "{0}/{1}.yml".format(project_path, group)
            job_name = "{0}-cfg-update-{1}".format(app_name, datetime.datetime.now().strftime("%Y%m%d%H%M"))
            task_role = ansible_role_config.ANSIBLE_PLAY_ROLES['play_config_release_task']
 
            """创建主机资源组"""
            create_ansible_hosts(inventory, playbook, group, task_role, host_select)
            """创建调用变量"""
            vars_file = "{0}/group_vars/{1}.yml".format(project_path, group)
            """delete old variables if exists, for safety"""
            if os.path.exists(vars_file):
                os.remove(vars_file)
            app_name, app_port, app_path, app_bk, app_work = get_app_detail(app_type, app_name)
            data_dict = {'vars_file': vars_file, 'app_name':app_name,'app_port': app_port, 'app_path': app_path, 'app_bk': app_bk, 'config': cfg, 'reload_control': switch, 'curr_dt':curr_dt}
            create_variables = CreatePlayVariables(data_dict, '')
            create_variables.play_config_update_varibales()
                
            """创建发布task"""
            data = execute_release_task(playbook, inventory, job_name, app_type, "", "", "")
            AnsibleTaskRecord.objects.create(app_name = app_name, app_type=app_type, ansible_group = group, 
                                             app_path = app_path,
                                             release_path = '{0}/{1}'.format(app_path, ansible_role_config.PLAY_FRAMEWORK['config']),
                                             update_file_type = 'config', ansible_user = username,
                                             backup_path = app_bk,
                                             backup_file = "conf_full_{0}".format(curr_dt),
                                             state="release",
                                             create_time = curr_dt)
            return JsonResponse(data)
        except Exception as err:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 
            return JsonResponse({'error':str(err), 'code': 500})
    
    return render(request, 'tasks/release/config/release_config.html',locals())


@login_required(login_url='/login')
@role_required(role='admin')
def play_config_compare(request):
    """
     compare config file
    """
    try:
        app_name = request.GET.get('app_name', '')
        filename = request.GET.get('filename', '')
        """new config"""
        local_path = "{0}/{1}".format(MEDIA_ROOT, app_name)
        config_file = "{0}/{1}/{2}".format(local_path, ansible_role_config.PLAY_FRAMEWORK['config'], filename)
        """old config"""
        old_config = "{0}/{1}/{2}-old".format(local_path, ansible_role_config.PLAY_FRAMEWORK['config'], filename)
        if os.path.exists(config_file):
            f1 = open(config_file, 'r')
            new_content = f1.read()
            f1.close()
        if os.path.exists(old_config):
            f2 = open(old_config, 'r')
            old_content = f2.read()
            f2.close()
    except Exception as e:
        return HttpResponse(json.dumps({'Error':str(e)}))
    return render(request, 'tasks/release/config/compare_config.html',locals())

