# -*- coding: utf-8 -*-

import os
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.utils.display import log_file
from ansible.errors import AnsibleParserError


class PlaybookTask(object):

    def __init__(self, playbook, host_list, timeout=180, extra_vars={}, connection='paramiko',become=False, become_user=None,
                        module_path=None,
                        fork=50,
                        ansible_cfg="/etc/ansible/ansible.cfg",   #os.environ["ANSIBLE_CONFIG"] = None
                        passwords={},
                        check=False):
        self.playbook = playbook
        self.extra_vars = extra_vars
        self.passwords = passwords
        self.host_list = host_list
	self.timeout = timeout
        Options = namedtuple('Options',
                   ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path',
                   'forks', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
                      'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check', 'timeout'])
        self.options = Options(listtags=False, listtasks=False, 
                              listhosts=False, syntax=False, 
                              connection=connection, module_path=module_path, 
                              forks=fork, private_key_file=None, 
                              ssh_common_args=None, ssh_extra_args=None, 
                              sftp_extra_args=None, scp_extra_args=None, 
                              become=become, become_method=None, 
                              become_user=become_user, 
                              verbosity=5, check=check, timeout=self.timeout)
        if ansible_cfg != None:
            os.environ["ANSIBLE_CONFIG"] = ansible_cfg
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager,  host_list=self.host_list)
    
    def run(self, log):
        if log:
            log_file.append(log)
        if not os.path.exists(self.playbook):
            code = 1000
            result = 'not exists playbook: ' + self.playbook
            return code, result
        pbex = PlaybookExecutor(playbooks=[self.playbook],
                                inventory=self.inventory,
                                variable_manager=self.variable_manager,
                                loader=self.loader,
                                options=self.options,
                                passwords=self.passwords)
        try:
            code = pbex.run()
        except AnsibleParserError:
            code = 1001
            result = 'syntax problems in ' + self.playbook
            return  code, result
        stats = pbex._tqm._stats
        hosts = sorted(stats.processed.keys())
        results = [{h: stats.summarize(h)} for h in hosts]
        if not results:
            code = 1002
            result = 'no host executed in ' + self.playbook
            return  code, result
        return code,results
"""
if __name__ == '__main__':
    book2 = PlaybookTask('/devops/frameworks/pcloud/pcloud-release-gray-1.yml','/devops/frameworks/pcloud/inventory/pcloud-release-gray-1')
    code = book2.run('/tmp/aa.log')   #  get simple result about playbook, and log detail in log_file
    print code
"""
