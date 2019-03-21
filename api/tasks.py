# -*- coding: utf-8 -*-

#from celery import task
from __future__ import absolute_import, unicode_literals
from api.ansible.ansible_playbook_task import PlaybookTask
from billiard.exceptions import Terminated
from celery import shared_task
import traceback, logging
#import subprocess
import commands


@shared_task(throws=(Terminated,))
def execute_ansible_job(data):
    """create ansible run task for update"""
    try:
        ansi_playbook_task = PlaybookTask('%s' % data['yml_file'],'%s' % data['hosts_file'])
        code = ansi_playbook_task.run('%s' % data['log_file']) 
        return code
    except  Exception as err:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())         
        return err


@shared_task(throws=(Terminated,))
def add(x, y):
    return x + y


@shared_task(throws=(Terminated,))
def async_execute_ansible_job(data):
    """create ansible run task for update"""
    try:
        cmd = "set -o pipefail;ansible-playbook {0} -i {1} -v |tee -a {2}".format(data['yml_file'], data['hosts_file'], data['log_file'])
        #recode = subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        status, output = commands.getstatusoutput(cmd)
        return {'code': status}
    except  Exception as err:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())         
        return {'code': '500', 'msg': err}
