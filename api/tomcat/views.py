#!/usr/local/python/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from api.views import check_task_result, check_task_state
from django.http import HttpResponse
from opstask.models  import JobLogs
from api.views import role_required
from api.views  import  create_ansible_variables
import os, datetime, json
import logging
import traceback

class CreateTomcatVariables(object):
    """"
    Create the ansbile variable for call ansible task
    """
    def __init__(self, data):
        self.content = {}
        self.data = data
        self.content['code_workspace'] = data['code_workspace']
        self.content['backup_path'] = data['backup_path']
        self.content['app_name'] = data['app_name']
        self.content['deploy_path'] = data['deploy_path']
        self.content['curr_dt'] = data['curr_dt']
        self.content['reload_control'] = data['reload_control']
        
    def tomcat_full_release_variables(self, arg):
        """
        Creating variables for the full release of the Java program,
        divided into SVN updates and manually uploaded updates
        """
        self.arg = arg
        if self.arg == "svn":
            self.content['svn_path'] = self.data['svn_path']
        elif self.arg == 'trans':
            self.content['trans_path'] = self.data['trans_path']
        """create variables"""           
        create_ansible_variables(self.data['vars_file'], self.content)        
        
    def tomcat_increment_update_variables(self, mode):
        """
        Create variables when updating the java packages
        """
        self.mode = mode
        self.content['dst_path'] = self.data['dst_path']
        if self.mode == "add":
            self.content['local_path'] = self.data['local_path']
            self.content['add_file'] = self.data['add_file']
        elif self.mode == "del":
            self.content['del_file'] = self.data['del_file']
        elif self.mode == "iter":
            self.content['old_file'] = self.data['old_file']
            self.content['new_file'] = self.data['new_file']
            self.content['local_path'] = self.data['local_path']           
            """create variables"""              
        create_ansible_variables(self.data['vars_file'], self.content)        
    
    def tomcat_config_update_varibales(self, mode):
        """
        Create variables when updating the configuration file
        """
        self.mode = mode
        self.content['config_file'] = self.data['config_file']
        if self.mode == "add":
            self.content['add_config'] = self.data['add_config']
        elif self.mode == "mod":
            self.content['mod_config'] = self.data['mod_config']
        """create variables"""              
        create_ansible_variables(self.data['vars_file'], self.content)
        
        
