#!/usr/bin/env python  
# _*_ coding:utf-8 _*_ 

from opstask.models import AnsibleModelRecord
from opstask.models import Ansible_CallBack_Model_Result


class AnsibleSaveResult(object): 
    class Model(object): 
        @staticmethod
        def insert(logId, content):
            try:
                return Ansible_CallBack_Model_Result.objects.create(
                                    log_id= logId,
                                    content = content
                                              )
            except:
                return False
 
                
class AnsibleRecord(object):
    class Model(object):
        @staticmethod
        def insert(ansible_user, ansible_host, ansible_model, ansible_args, create_time):
            try:
                return AnsibleModelRecord.objects.create(
                                    ansible_user = ansible_user,
                                    ansible_host = ansible_host,
                                    ansible_model = ansible_model,
                                    ansible_args = ansible_args,
                                    create_time = create_time,
                                              )
            except:
                return False
