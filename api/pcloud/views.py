# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from api.views import check_task_result, check_task_state
from cmdb.models import BackupLogs
from tempfile import NamedTemporaryFile
from django.http import HttpResponse, JsonResponse
from celery.result import AsyncResult
from opstask.models  import JobLogs
from api.views import role_required
from api.tasks import *
import traceback, logging
import json
import datetime
import os
import re

logg = logging.getLogger('opsadmin')

def pcloud_execute_ansible_job(yml_file, hosts_file):
    """
    Asynchronous execution of tasks using celery
    """

    try:
        data = {}
        tempdir = "/tmp/ansible"
        data['yml_file'] = yml_file
        data['hosts_file'] = hosts_file
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)
        f = NamedTemporaryFile(delete=False, dir=tempdir)
        data['log_file'] = f.name
        result = async_execute_ansible_job.delay(data)
        return result.task_id, f.name
    except:
        logg.error('%s' % traceback.format_exc())

def pcloud_log_insert_to_db(data, task_id, log_file, action, inventory, job_name, start_time, username):
    """
    check task state , inserting the log into MySQL
    """
    data['state']= check_task_state(task_id)
    result_msg = check_task_result(task_id)
    dic = {}
    dic['job_name'] = job_name
    dic['app_type'] = "private_cloud"
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
            if action != "rollback":
                pcloud_backup_insert_db(content)
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

@login_required(login_url='/login')
@role_required(role='admin')
def pcloud_read_ansible_log(request):
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
            data['task_id'] = task_id
            t = request.POST.get('time')
            job_name = request.POST.get('job_name')
            inventory = request.POST.get('inventory')
            action = request.POST.get('action')
            start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if not os.path.exists(log_file):
                data['read_flag'] = True
                data['logs'] = ''
                return HttpResponse(data)
            with open(log_file, 'r') as f:
                f.seek(int(seek))
                data['logs'] = f.read()
                data['seek'] = f.tell()
            data = pcloud_log_insert_to_db(data, task_id, log_file, action, inventory, job_name, start_time, username)
            return HttpResponse(json.dumps(data))
        except Exception as err:
            data['error'] = str(err)
            logg.error('%s' % traceback.format_exc())
            return HttpResponse(json.dumps(data))
        
@login_required(login_url='/login')
@role_required(role='admin')
def pcloud_revoke_ansible_job(request):
    """"
    Revocation of the running task
    """
    if request.method == 'POST':
        task_id = request.POST.get('task_id').encode('utf-8')
        try:
            AsyncResult(task_id).revoke(terminate=True, signal='SIGKILL')
            #celery_contorl = Control()
            #celery_contorl.revoke(task_id, terminate=True, signal='SIGKILL')
            return JsonResponse({"message": "取消任务完成", 'code': 200})
        except Exception,e:
            return JsonResponse({"message": u'取消任务失败.{0}'.format(e), 'code': 500})
    

def pcloud_backup_insert_db(content):
    """
    Get the backup information and insert the MySQL database
    """
    try:
        logg = logging.getLogger('opsadmin')
        create_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        re_match = re.compile('\{.*/backup/.*\}')
        result = re_match.findall(content)
        if len(result) > 0:
            for res_list in result:
                #ansible log of stdout_lines
                res = json.loads(res_list)
                bk_result = res['stdout_lines'][0].encode('utf-8')
                app_name = bk_result.split('/')[4]
                q = BackupLogs.objects.filter(backup_file=bk_result)
                if len(q) == 0:
                    bk_info = {'app_name': app_name, 'project':'pcloud', 'backup_file':bk_result, 'create_date':create_date}
                    BackupLogs.objects.create(**bk_info)
        else:
            pass
    except:
        logg.error('%s' % traceback.format_exc())

   
   
    
    
    
    
    
    
    
    
