# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from api.views import role_required
from opstask.models import JobLogs, AnsibleScripts
from cmdb.models import ServerInfo, AppInfo
from django.http import HttpResponse
import datetime
import logging, json

@login_required(login_url='/login')
@role_required(role='user')
def index(request):
    """create mysql connect
    db = pymysql.connect("192.168.10.222", "opsadmin", "12345678", "opsdb")
    cursor = db.cursor()
    """
    """calc task result count"""
    logg = logging.getLogger('opsadmin')
    username = request.session.get('name')
    try:
        year = datetime.datetime.now().strftime("%Y")
        month = datetime.datetime.now().strftime("%m")
        year_month = datetime.datetime.now().strftime("%Y-%m")
        sum_success_task = JobLogs.objects.filter(state='SUCCESS').filter(end_time__contains=year).count()
        if sum_success_task == 0:
            sum_success_task = 1
        sum_failed_task = JobLogs.objects.filter(state='FAILURE').filter(end_time__contains=year).count()
        sum_revoke_task = JobLogs.objects.filter(state='REVOKED').filter(end_time__contains=year).count()
        
        """statics update task"""
        if request.session.get('role_id') == 0:
            task_list = JobLogs.objects.values('id', 'job_name', 'excutor', 'end_time').order_by('-id')[0:8]
        else:
            task_list = JobLogs.objects.filter(excutor=username).values('id', 'job_name', 'excutor', 'end_time').order_by('-id')[0:8]
        """get host, project, task, job"""
        hosts = ServerInfo.objects.all().count()
        projects = AppInfo.objects.all().count()
        tasks = JobLogs.objects.all().count()
        jobs = AnsibleScripts.objects.all().count()
        """get percent"""
        if hosts and projects and tasks and jobs:
            tasks_percent = '%d%%' % ((JobLogs.objects.filter(end_time__contains=year_month).count() / float(tasks)) * 100)
            jobs_percent = '%d%%' % ((AnsibleScripts.objects.filter(create_time__contains=year_month).count() / float(jobs)) * 100)
            hosts_percent = '%d%%' % ((ServerInfo.objects.filter(create_time__year=year, create_time__month=month).count() / float(hosts)) * 100)
            projects_percent = '%d%%' % ((AppInfo.objects.filter(create_time__year=year).count() / float(projects)) * 100)
        else:
            tasks_percent = '0%'
            jobs_percent = '0%'
            hosts_percent = '0%'
            projects_percent = '0%'          
    except Exception, e:
        logg.error(e)
    return render(request, 'home/index.html', locals())

def get_chart_data(request):
    chart_data = []
    year = datetime.datetime.now().strftime("%Y")
    logg = logging.getLogger('opsadmin')
    try:
        for i in xrange(1,13):
            if len(str(i)) == 2:
                month_num = i
            else:
                month_num = "0%d" % i
            dt = "{0}-{1}".format(year, month_num)
            public = JobLogs.objects.filter(end_time__contains=dt, app_type="public_cloud").count()
            private = JobLogs.objects.filter(end_time__contains=dt, app_type="private_cloud").count()
            cms = JobLogs.objects.filter(end_time__contains=dt, app_type="cms").count()
            pay = JobLogs.objects.filter(end_time__contains=dt, app_type="pay").count()
            notify = JobLogs.objects.filter(end_time__contains=dt, app_type="notify").count()
            spay = JobLogs.objects.filter(end_time__contains=dt, app_type="spay").count()
            month="{0}月".format(i)
            data = {'x':month, 'a':private, 'b':public, 'c':pay, 'd':notify, 'e':cms, 'f':spay}
            chart_data.append(data)
        return HttpResponse(json.dumps(chart_data))
    except Exception,err:
        logg.error(err)
        
    
