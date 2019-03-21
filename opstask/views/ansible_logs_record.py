# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from opstask.models import JobLogs, AnsibleModelRecord, Ansible_CallBack_Model_Result, AnsibleTaskRecord
from api.views import role_required
import traceback, logging
from django.core.cache import cache



@login_required(login_url='/login')
@role_required(role='user')
def ansible_playbook_logs(request):
    """
      列出ansible job logs
    """
    path1, path2 = u'任务执行历史', u'作业执行日志'
    pid = request.GET.get('id')
    #set cache key
    try:        
        if request.session.get('role_id') == 0:
            cache_key = 'key_all_task_logs'
            if pid:
                job_logs = JobLogs.objects.filter(id=pid)
            else:
               if cache_key in cache:
                   job_logs = cache.get(cache_key)
               else:
                   job_logs = JobLogs.objects.all()
                   cache.set(cache_key, job_logs, 60*60)
        else:
            username = request.session.get('name')
            cache_key = 'key_user_task_logs'
            if pid:
                job_logs = JobLogs.objects.filter(id=pid, excutor=username)
            else:
               if cache_key in cache:
                   job_logs = cache.get(cache_key)
               else:
                   job_logs = JobLogs.objects.filter(excutor=username)
                   cache.set(cache_key, job_logs, 60*60)
                
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc()) 
    return render(request, 'tasks/logs/ansible_playbook_logs.html',locals())



@login_required(login_url='/login')
@role_required(role='user')
def ansible_script_logs(request):
    """
      列出ansible job logs
    """
    path1, path2 = u'任务执行历史', u'脚本执行日志'
    
    try:
        if request.session.get('role_id') == 0:
            script_logs = AnsibleModelRecord.objects.all()
        else:
            username = request.session.get('name')
            script_logs = AnsibleModelRecord.objects.filter(ansible_user=username)
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc()) 
    return render(request, 'tasks/logs/ansible_script_logs.html',locals())


@login_required(login_url='/login')
@role_required(role='user')
def ansible_playbook_logs_detail(request):
    """
       ansible playbook logs detail
    """
    job_id = request.GET.get('id')
    job_logs = JobLogs.objects.get(pk=int(job_id))
    return render(request, 'tasks/logs/ansible_playbook_logs_detail.html',locals())

@login_required(login_url='/login')
@role_required(role='user')
def ansible_script_logs_detail(request):
    """
       ansible script logs detail
    """
    try:
        result = ''
        log_id = request.GET.get('id')
        ansible_log_id = AnsibleModelRecord.objects.get(id=log_id)
        ansible_log = Ansible_CallBack_Model_Result.objects.filter(log_id=ansible_log_id)
        for log in ansible_log:
            result += log.content
            result += '\n'
    except Exception as error:
        result = error
         
    return render(request, 'tasks/logs/ansible_script_logs_detail.html',locals())



@login_required(login_url='/login')
@role_required(role='user')
def ansible_task_record(request):
    """
       ansible job record
    """
    path1, path2 = u'任务执行历史', u'作业操作记录'
    try:
        if request.session.get('role_id') == 0:
            task_record = AnsibleTaskRecord.objects.all()
        else:
            username = request.session.get('name')
            task_record = AnsibleTaskRecord.objects.filter(ansible_user=username)
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())
    return render(request, 'tasks/logs/ansible_task_record.html',locals())


