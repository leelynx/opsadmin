# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from api.views import check_task_result, check_task_state
from django.http import HttpResponse
from cmdb.models import AnsibleGroup, AppInfo
from opstask.models  import JobLogs
from api.views import role_required
from api.views  import  create_ansible_variables
import datetime, logging, traceback
from opsadmin.settings import MEDIA_ROOT
from api.ansible import ansible_role_config
import paramiko
import json
import shutil
import os

class CreatePlayVariables(object):
    """"
    Create the ansbile variable for call ansible task,
    Play framework
    """
    def __init__(self, data, arg):
        self.content = {}
        self.data = data
        self.content['play_name'] = data['app_name']
        self.content['play_port'] = data['app_port']
        self.content['play_path'] = data['app_path']
        self.content['curr_dt'] = data['curr_dt']
        self.content['reload_control'] = data['reload_control']
        self.arg = arg
        
    def play_full_release_variables(self):
        """
        Creating variables for the full release of the Java program,
        divided into SVN updates and manually uploaded updates
        """
        self.content['play_workspace'] = self.data['app_work']
        self.content['play_bk_dir'] = self.data['app_bk']
        self.content['play_lib_release'] = self.data['lib_path']
        self.content['play_plugins_release'] = self.data['plugins_path']
        if self.arg == "svn":
            self.content['svn_path'] = self.data['svn_path']  
        elif self.arg == 'trans':
            self.content['trans_path'] = self.data['trans_path']
        """create variables"""           
        create_ansible_variables(self.data['vars_file'], self.content)        
        
    def play_increment_update_variables(self, mode):
        """
        Create variables when updating the java packages
        """
        self.content['play_workspace'] = self.data['app_work']
        self.content['play_bk_dir'] = self.data['app_bk']
        self.content['jar_path'] = self.data['trans_path']
        if mode == "add":
            if self.data['lib'] and self.data['plugins'] is None:
                self.content['lib_type'] = self.data['lib']
            elif self.data['lib'] is None and self.data['plugins']:
                self.content['plugins_type'] = self.data['plugins']      
            elif self.data['lib'] and self.data['plugins']:
                self.content['lib_type'] = self.data['lib']
                self.content['plugins_type'] = self.data['plugins']
        elif mode == "iter":
            self.content['jar_path'] = self.data['trans_path']
            self.content['dst_path'] = self.data['dst_path']
            self.content['old_file'] = self.data['old_file']
            self.content['new_file'] = self.data['new_file']       
        """create variables"""              
        create_ansible_variables(self.data['vars_file'], self.content)        
    
    def play_config_update_varibales(self):
        """
        Create variables when updating the configuration file
        """
        conf_path = "{0}/{1}/{2}".format(MEDIA_ROOT, self.data['app_name'], ansible_role_config.PLAY_FRAMEWORK['config'])
        play_config= "{0}/{1}".format(self.data['app_path'], ansible_role_config.PLAY_FRAMEWORK['config'])
        self.content['play_bk_dir'] = self.data['app_bk']
        self.content['play_config'] = play_config
        if self.data['config'] == ansible_role_config.PLAY_CONFIG_TYPE['app']:
            self.content['app_config'] = '{0}/{1}'.format(conf_path, self.data['config'])
        elif self.data['config'] == ansible_role_config.PLAY_CONFIG_TYPE['api']:
            self.content['api_config'] = "{0}/{1}".format(conf_path, self.data['config'])
        elif self.data['config'] == ansible_role_config.PLAY_CONFIG_TYPE['reload']:
            self.content['reloadable_config'] = "{0}/{1}".format(conf_path, self.data['config'])
        """create variables"""              
        create_ansible_variables(self.data['vars_file'], self.content)

@login_required(login_url='/login')
@role_required(role='admin')
def play_config_get(request):
    """"
    Getting the remote host program configuration file
    """
    try:
        filename = request.GET.get('filename')
        get_path = request.GET.get('path')
        group = request.GET.get('group')
        app_name = request.GET.get('app_name')
        """define local path for save config file"""
        path = "{0}/{1}".format(get_path, app_name)
        config_path = "{0}/{1}/".format(path, ansible_role_config.PLAY_FRAMEWORK['config'])
        r_file = config_path + filename
        """get deploy path of program"""
        app_info = AppInfo.objects.filter(app_name=app_name).first()
        deploy_path = app_info.main_path
        
        """query data for build ssh connect"""
        ab_group = AnsibleGroup.objects.get(group=group)
        host_dict = ab_group.serverinfos.all().values()[0]
        """define local config path to save"""
        src_file = "{0}/{1}/{2}".format(deploy_path, ansible_role_config.PLAY_FRAMEWORK['config'], filename)
        
        """"get config from remote host and write local host"""
        if not os.path.exists(config_path):
            os.makedirs(config_path)
        transport = paramiko.Transport((host_dict['private_ip'], host_dict['host_port']))
        transport.connect(username=host_dict['username'], password=host_dict['password'])
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(src_file, r_file)
        f_p = open(r_file, 'r')
        content = f_p.readlines()
        f_p.close()
        transport.close()
        return HttpResponse(content)
    except Exception as err:
        error = "Error: " +str(err)
        return HttpResponse(error)

@login_required(login_url='/login')
@role_required(role='admin')
def play_config_save(request):
    """
    Save the modified configuration file to the local
    """
    try:
        if request.method == "POST":
            app_name = request.POST.get('app_name', '')
            content = request.POST.get('config_text').encode('utf-8')
            filename = request.POST.get('config')
            """save path on localhost"""
            local_path = "{0}/{1}".format(MEDIA_ROOT, app_name)
            conf_path = "{0}/{1}".format(local_path, ansible_role_config.PLAY_FRAMEWORK['config'])
            new_config = "{0}/{1}".format(conf_path, filename)
            """backup config on localhost"""
            bk_config = "{0}-{1}".format(new_config, "old")
            """"write new config"""
            if os.path.exists(new_config):
                shutil.move(new_config, bk_config)
            with open(new_config, 'wb+') as conf:
                conf.write(content)
        return HttpResponse("保存修改配置成功")
    except Exception,e:
        return HttpResponse(e)    


def ansible_log_insert_to_db(data, task_id, log_file, inventory, project, job_name, start_time, username):
    """
    check task state , inserting the log into MySQL
    """
    try:
        data['state']= check_task_state(task_id)
        result_msg = check_task_result(task_id)
        dic = {}
        dic['job_name'] = job_name
        dic['app_type'] = project
        dic['job_uuid'] = task_id
        dic['start_time'] = start_time
        dic['excutor'] = username
        if data['state'] in ['SUCCESS']:
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
            JobLogs.objects.create(**dic)              
        elif data['state'] in ['FAILURE', 'REVOKED']:
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
    except:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc()) 

@login_required(login_url='/login')
@role_required(role='admin')
def play_read_ansible_log(request):
    """
    Read the ansible execution log and insert the detailed log into the MySQL database
    """
    username = request.session['name']
    if request.method == 'POST':
        try:
            data = {}
            log_file = request.POST.get('log_file')
            seek = request.POST.get('seek')
            task_id = request.POST.get('task_id')
            project = request.POST.get('app_type')
            job_name = request.POST.get('job_name')
            inventory = request.POST.get('inventory')
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
            data = ansible_log_insert_to_db(data, task_id, log_file, inventory, project, job_name, start_time, username)
            return HttpResponse(json.dumps(data))
        except Exception, err:
            data['error'] = str(err)
            return HttpResponse(json.dumps(data))
    
    
    
    















