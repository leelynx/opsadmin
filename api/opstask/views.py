# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from api.views import check_task_result, check_task_state
from django.http import HttpResponse
from api.views import role_required
from opstask.models  import JobLogs
import os, json ,datetime
from cmdb.models import AppInfo
from opsadmin.settings import MEDIA_ROOT
from api.ansible import ansible_role_config
from api.play.views import CreatePlayVariables
from api.tomcat.views import CreateTomcatVariables
from api.views import create_ansible_hosts
from opstask.models import AnsibleTaskRecord
import logging
import traceback


def execute_log_insert_to_db(data, task_id, log_file, project, inventory, job_name, task_detail, start_time, username, pid, release_tag):
    """
    check task state , inserting the log into MySQL
    """
    data['state']= check_task_state(task_id)
    result_msg = check_task_result(task_id)
    dic = {}
    dic['job_name'] = job_name
    dic['app_type'] = project
    dic['job_uuid'] = task_id
    dic['start_time'] = start_time
    dic['excutor'] = username
    dic['version_description'] = task_detail
    if data['state'] in ['SUCCESS']:
        AppInfo.objects.filter(app_id=pid).update(app_status=4)
        data['read_flag'] = False
        os.remove(inventory)
        with open(log_file, 'r') as f_res:
            content = f_res.read()
        """check job if run success"""
        dic['end_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dic['detail'] = content
        if result_msg['code'] == 0:
            dic['state'] = "SUCCESS"
        else:
            dic['state'] = "FAILURE"
            AnsibleTaskRecord.objects.filter(release_tag=release_tag).delete()
        JobLogs.objects.create(**dic)          
    elif data['state'] in ['FAILURE', 'REVOKED']:
        AppInfo.objects.filter(app_id=pid).update(app_status=4)
        AnsibleTaskRecord.objects.filter(release_tag=release_tag).delete()
        data['read_flag'] = False
        with open(log_file, 'r') as f_res:
            content = f_res.read()
        dic['end_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dic['state'] = data['state']
        dic['detail'] = content
        JobLogs.objects.create(**dic)
    else:
        data['read_flag'] = True
    
    return data   


@login_required(login_url='/login')
@role_required(role='admin')
def read_ansible_execute_log(request):
    """
    Read the ansible execution log and insert the detailed log into the MySQL database
    """
    username = request.session['name']
    data = {}
    if request.method == 'POST':
        try:
            log_file = request.POST.get('log_file')
            seek = request.POST.get('seek')
            task_id = request.POST.get('task_id')
            project = request.POST.get('app_type')
            task_detail =  request.POST.get('task_detail')
            job_name = request.POST.get('job_name')
            inventory = request.POST.get('inventory')
            pid = request.POST.get('pid')
            release_tag = request.POST.get('release_tag')
            start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['task_id'] = task_id
            if not os.path.exists(log_file):
                data['read_flag'] = True
                data['logs'] = ''
                return HttpResponse(data)
            with open(log_file, 'r') as f:
                f.seek(int(seek))
                data['logs'] = f.read()
                data['seek'] = f.tell()
            data = execute_log_insert_to_db(data, task_id, log_file, project, inventory, job_name, task_detail, start_time, username, pid, release_tag)
            return HttpResponse(json.dumps(data))
        except Exception, err:
            data['error'] = str(err)
            return HttpResponse(json.dumps(data))


class AnsibleCreateTask(object):
    """
    create ansible task
    """
    def __init__(self, app_type, app_name, group, inventory, playbook, vars_file, exec_mode, host_list, create_date):  
        #self.create_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.inventory = inventory
        self.playbook = playbook
        self.vars_file = vars_file
        self.app_type = app_type
        self.app_name = app_name
        self.group = group
        self.exec_mode = exec_mode
        self.host_list = host_list
        self.create_date = create_date
        
    def get_app_deploy(self, frame_type):
        """get app deploy information"""
        app_data = AppInfo.objects.filter(app_type=self.app_type, app_name=self.app_name).first()
        app_name = app_data.app_name
        app_port = app_data.run_port
        app_path = app_data.main_path
        app_bk = app_data.backup_path
        app_work = app_data.work_path
        if frame_type == "play":
            return app_name, app_port, app_path, app_bk, app_work
        elif frame_type == "tomcat":
            return app_name, app_path, app_bk, app_work    

class PlayCreateTask(AnsibleCreateTask):
    """play task"""
    def __init__(self, app_type, app_name, group, inventory, playbook, vars_file, exec_mode, host_list, create_date):
        super(PlayCreateTask, self).__init__(app_type, app_name, group, inventory, playbook, vars_file, exec_mode, host_list, create_date)
        self.curr_dt = self.create_date
    def play_full_release_task(self, mode, **kw):
        """
        create variables for the play framework
        """
        try:
            app_name, app_port, app_path, app_bk, app_work = self.get_app_deploy('play')
            lib_path = "{0}/{1}".format(app_path, ansible_role_config.PLAY_FRAMEWORK['lib_path'])
            plugins_path = "{0}/{1}".format(app_path, ansible_role_config.PLAY_FRAMEWORK['plugins_path'])
            lib_path = ''.join(lib_path.split())
            plugins_path = ''.join(plugins_path.split())
            data_dict = {}
            """获取程序更新变量"""
            data_dict['vars_file'] = self.vars_file
            data_dict['app_name'] = app_name
            data_dict['app_port'] = app_port
            data_dict['app_path'] = app_path
            data_dict['app_bk'] = app_bk
            data_dict['app_work'] = app_work
            data_dict['lib_path'] = lib_path
            data_dict['curr_dt'] = self.curr_dt
            data_dict['plugins_path'] =plugins_path
            data_dict['reload_control'] = kw['switch']
            if mode == "svn":
                data_dict['svn_path'] = kw['svn_path']
                """创建主机资源组"""
                task_role = ansible_role_config.ANSIBLE_PLAY_ROLES['play_svn_release_task']
                create_ansible_hosts(self.inventory, self.playbook, self.group, task_role, self.host_list, exe_mode = self.exec_mode)
            elif mode == "trans":
                data_dict['trans_path'] = kw['trans_path']
                """创建主机资源组"""
                task_role = ansible_role_config.ANSIBLE_PLAY_ROLES['play_trans_release_task']
                create_ansible_hosts(self.inventory, self.playbook, self.group, task_role, self.host_list, exe_mode = self.exec_mode)
            create_variables = CreatePlayVariables(data_dict, mode)
            create_variables.play_full_release_variables()
            AnsibleTaskRecord.objects.create(app_name = app_name, app_type=self.app_type, ansible_group = self.group, hosts_list = ','.join(self.host_list),
                                             app_path = app_path,
                                             frameworks = 'play',
                                             release_path = '{0},{1}'.format(plugins_path, lib_path),
                                             update_file_type = 'pack', ansible_user = kw['username'],
                                             release_tag = '{0}_{1}'.format(kw['app_ver'], self.curr_dt),
                                             backup_path = app_bk,
                                             backup_file = 'plugins_full_{0},lib_full_{1}'.format(self.curr_dt, self.curr_dt),
                                             state="release",
                                             create_time = self.curr_dt)			
        except:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 

    def play_increment_update_task(self, mode, **kw):
        """
        create variables for the play framework
        """
        try:
            app_name, app_port, app_path, app_bk, app_work = self.get_app_deploy('play')
            """创建主机资源组"""
            data_dict = {}
            task_role = ansible_role_config.ANSIBLE_PLAY_ROLES['play_increment_release_task']
            create_ansible_hosts(self.inventory, self.playbook, self.group, task_role, self.host_list, exe_mode = self.exec_mode)
            """ 获取程序更新变量"""
            data_dict['vars_file'] = self.vars_file
            data_dict['app_name'] = app_name
            data_dict['app_port'] = app_port
            data_dict['app_path'] = app_path
            data_dict['app_bk'] = app_bk
            data_dict['app_work'] = app_work
            data_dict['curr_dt'] = self.curr_dt
            data_dict['reload_control'] = kw['switch']
            data_dict['trans_path'] = "{0}/{1}".format(MEDIA_ROOT, app_name)
            if mode == "add":
                data_dict['lib'] = kw['lib']
                data_dict['plugins'] =  kw['plugins']
                if kw['lib'] and kw['plugins']:
                    plugins_path = '{0}/{1}'.format(app_path,kw['plugins'])
                    lib_path = '{0}/{1}'.format(app_path,kw['lib'])
                    release_path = '{0},{1}'.format(plugins_path, lib_path)
                    backup_file = 'plugins_incr_{0},lib_incr_{1}'.format(self.curr_dt, self.curr_dt)
                elif kw['plugins'] and kw['lib'] is None:
                    release_path = '{0}/{1}'.format(app_path,kw['plugins'])
                    backup_file = 'plugins_incr_{0}'.format(self.curr_dt)
                elif kw['lib'] and kw['plugins'] is None:
                    release_path = '{0}/{1}'.format(app_path,kw['lib'])
                    backup_file = 'lib_incr_{0}'.format(self.curr_dt)             
            elif mode == "iter":
                data_dict['dst_path'] = kw['dst_path']
                data_dict['old_file'] = kw['old_file']
                data_dict['new_file'] = kw['new_file']
                release_path = '{0}/{1}'.format(app_path, kw['dst_path'].split('/')[0])
                backup_file = '{0}_iter_{1}'.format(kw['dst_path'].split('/')[0], self.curr_dt)
            create_variables = CreatePlayVariables(data_dict, '')
            create_variables.play_increment_update_variables(mode)
            AnsibleTaskRecord.objects.create(app_name = app_name, app_type=self.app_type, ansible_group = self.group, hosts_list = ','.join(self.host_list),
                                             app_path = app_path,
                                             frameworks = 'play',
                                             release_path = release_path,
                                             update_file_type = 'pack', ansible_user = kw['username'],
                                             backup_path = app_bk,
                                             backup_file = backup_file,
                                             release_tag = '{0}_{1}'.format(kw['app_ver'], self.curr_dt),
                                             state="release",
                                             create_time = self.curr_dt)          
        except:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 


class TomcatCreateTask(AnsibleCreateTask):
    """tomcat task"""
    def __init__(self, app_type, app_name, group, inventory, playbook, vars_file, exec_mode, host_list, create_date):
        super(TomcatCreateTask, self).__init__(app_type, app_name, group, inventory, playbook, vars_file, exec_mode, host_list, create_date)
        self.curr_dt = self.create_date
        
    def tomcat_full_release_task(self, mode, **kw):
        """
        create variables for the tomcat framework
        """
        try:
            app_name, app_path, app_bk, app_work = self.get_app_deploy('tomcat')
            data_dict = {}
            data_dict['curr_dt'] = self.curr_dt
            data_dict['vars_file'] = self.vars_file
            data_dict['code_workspace'] =  app_work
            data_dict['backup_path'] = app_bk 
            data_dict['app_name'] = app_name 
            data_dict['deploy_path'] = app_path
            data_dict['reload_control'] = kw['switch']
            if mode == "svn":
                data_dict['svn_path'] = kw['svn_path']
                """创建主机资源组"""
                task_role = ansible_role_config.ANSIBLE_TOMCAT_ROLES['tomcat_svn_release_task']
                create_ansible_hosts(self.inventory, self.playbook, self.group, task_role, self.host_list, exe_mode = self.exec_mode)
            elif mode == "trans":
                data_dict['trans_path'] = kw['trans_path']
                """创建主机资源组"""
                task_role = ansible_role_config.ANSIBLE_TOMCAT_ROLES['tomcat_trans_release_task']
                create_ansible_hosts(self.inventory, self.playbook, self.group, task_role, self.host_list, exe_mode = self.exec_mode)
            """create variables"""              
            create_variables = CreateTomcatVariables(data_dict)
            create_variables.tomcat_full_release_variables(mode)
            AnsibleTaskRecord.objects.create(app_name = app_name, app_type=self.app_type, ansible_group = self.group, hosts_list = ','.join(self.host_list),
                                             app_path = app_path,
                                             release_path = 'webapps',
                                             frameworks = 'tomcat',
                                             update_file_type = 'pack', ansible_user = kw['username'],
                                             backup_path = '{0}/{1}'.format(app_bk, app_name),
                                             backup_file = 'webapps_{0}'.format(self.curr_dt),
                                             release_tag = '{0}_{1}'.format(kw['app_ver'], self.curr_dt),
                                             state="release",
                                             create_time = self.curr_dt)
        except Exception as err:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc()) 

    def tomcat_increment_update_task(self, mode, **kw):
        """
        create variables for the tomcat framework
        """
        try:
            app_name, app_path, app_bk, app_work = self.get_app_deploy('tomcat')
            if mode == "add":
                task_role = ansible_role_config.ANSIBLE_TOMCAT_ROLES['tomcat_pack_add_task']
                """创建主机资源组"""
                create_ansible_hosts(self.inventory, self.playbook, self.group, task_role, self.host_list, exe_mode = self.exec_mode)
                data_dict = {'vars_file': self.vars_file, 
                             'code_workspace': app_work, 
                             'backup_path': app_bk, 
                             'app_name': app_name, 
                             'deploy_path': app_path,
                             'curr_dt': self.curr_dt,
                             'dst_path': kw['dst_path'],
                             'reload_control': kw['switch'],
                             'local_path': "{0}/{1}".format(MEDIA_ROOT, app_name),
                             'add_file': '"None"'}
                """create variables"""              
                create_variables = CreateTomcatVariables(data_dict)
                create_variables.tomcat_increment_update_variables(mode)
                backup_file = 'increment/{0}_{1}'.format(kw['dst_path'].split('/')[-1], self.curr_dt)
                release_path = kw['dst_path'] 
            elif mode == "del":
                task_role = ansible_role_config.ANSIBLE_TOMCAT_ROLES['tomcat_pack_del_task']
                """创建主机资源组"""
                create_ansible_hosts(self.inventory, self.playbook, self.group, task_role, self.host_list, exe_mode = self.exec_mode)
                data_dict = {'vars_file': self.vars_file, 
                             'code_workspace': app_work, 
                             'backup_path': app_bk, 
                             'app_name': app_name, 
                             'deploy_path': app_path,
                             'curr_dt': self.curr_dt,
                             'dst_path': kw['dst_path'],
                             'reload_control': kw['switch'],
                             'del_file': '"%s"' % ''.join(kw['del_file'])}
                """create variables"""              
                create_variables = CreateTomcatVariables(data_dict)
                create_variables.tomcat_increment_update_variables(mode)
                backup_file = 'increment/{0}_{1}'.format(kw['dst_path'].split('/')[-1], self.curr_dt)
                release_path = kw['dst_path']
            elif mode == "iter" :
                task_role = ansible_role_config.ANSIBLE_TOMCAT_ROLES['tomcat_pack_add_task']
                """创建主机资源组"""
                create_ansible_hosts(self.inventory, self.playbook, self.group, task_role, self.host_list, exe_mode = self.exec_mode)
                data_dict = {'vars_file': self.vars_file, 
                             'code_workspace': app_work, 
                             'backup_path': app_bk, 
                             'app_name': app_name, 
                             'deploy_path': app_path,
                             'curr_dt': self.curr_dt,
                             'dst_path': kw['dst_path'],
                             'reload_control': kw['switch'],
                             'local_path': "{0}/{1}".format(MEDIA_ROOT, app_name),
                             'old_file': ''.join(kw['old_file'].split()),
                             'new_file': ''.join(kw['new_file'].split())}
                """create variables"""              
                create_variables = CreateTomcatVariables(data_dict)
                create_variables.tomcat_increment_update_variables(mode)
                backup_file = '{0}_{1}'.format(''.join(kw['old_file'].split()), self.curr_dt)
                release_path = '{0}/{1}'.format(kw['dst_path'], ''.join(kw['new_file'].split()))
            AnsibleTaskRecord.objects.create(app_name = app_name, app_type=self.app_type, ansible_group = self.group, hosts_list = ','.join(self.host_list),
                                             app_path = app_path,
                                             frameworks = 'tomcat',
                                             release_path = release_path,
                                             update_file_type = 'pack', ansible_user = kw['username'],
                                             backup_path = '{0}/{1}'.format(app_bk, app_name),
                                             backup_file = backup_file,
                                             release_tag = '{0}_{1}'.format(kw['app_ver'], self.curr_dt),
                                             state="release",
                                             create_time = self.curr_dt)                              
        except:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc())     

    def tomcat_config_update_task(self, mode, **kw):
        try:
            app_name, app_path, app_bk, app_work = self.get_app_deploy('tomcat')
            if mode == "add":
                task_role = ansible_role_config.ANSIBLE_TOMCAT_ROLES['tomcat_config_add_task']               
                create_ansible_hosts(self.inventory, self.playbook, self.group, task_role, self.host_list, exe_mode = self.exec_mode)
                data_dict = {'vars_file': self.vars_file, 
                            'code_workspace': app_work, 
                            'backup_path': app_bk, 
                            'app_name': app_name, 
                            'deploy_path': app_path,
                            'curr_dt': self.curr_dt,
                            'reload_control': kw['switch'],
                            'add_config': '"%s"' % ''.join(kw['add_config']),
                            'config_file': '{0}/{1}'.format(ansible_role_config.TOMCAT_FRAMEWORK['config'], ansible_role_config.TOMCAT_CONFIG_TYPE['app'])}
                create_variables = CreateTomcatVariables(data_dict)
                create_variables.tomcat_config_update_varibales(mode)
            elif mode == "mod":
                task_role = ansible_role_config.ANSIBLE_TOMCAT_ROLES['tomcat_config_mod_task']
                create_ansible_hosts(self.inventory, self.playbook, self.group, task_role, self.host_list, exe_mode = self.exec_mode)
                data_dict = {'vars_file': self.vars_file, 
                             'code_workspace': app_work, 
                             'backup_path': app_bk, 
                             'app_name': app_name, 
                             'deploy_path': app_path,
                             'curr_dt': self.curr_dt,
                             'reload_control': kw['switch'],
                             'mod_config': kw['mod_config'],
                             'config_file': '{0}/{1}'.format(ansible_role_config.TOMCAT_FRAMEWORK['config'], ansible_role_config.TOMCAT_CONFIG_TYPE['app'])}
                """create variables""" 
                create_variables = CreateTomcatVariables(data_dict)
                create_variables.tomcat_config_update_varibales(mode)
            AnsibleTaskRecord.objects.create(app_name = app_name, app_type=self.app_type, ansible_group = self.group, hosts_list = ','.join(self.host_list),
                                             app_path = app_path,
                                             frameworks = 'tomcat',
                                             release_path = '{0}/{1}'.format(ansible_role_config.TOMCAT_FRAMEWORK['config'], ansible_role_config.TOMCAT_CONFIG_TYPE['app']),
                                             update_file_type = 'config', ansible_user = kw['username'],
                                             backup_path = '{0}/{1}'.format(app_bk, app_name),
                                             backup_file = '{0}_{1}'.format(ansible_role_config.TOMCAT_CONFIG_TYPE['app'], self.curr_dt),
                                             release_tag = '{0}_{1}'.format(kw['app_ver'], self.curr_dt),
                                             state="release",
                                             create_time = self.curr_dt)
        except:
            logg = logging.getLogger('opsadmin')
            logg.error('%s' % traceback.format_exc())    