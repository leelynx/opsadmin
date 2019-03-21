#!/usr/bin/env python
# -*- coding=utf-8 -*-
import json
from collections import namedtuple
from ansible import constants
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory,Host,Group
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from api.data.Redis_API import RedisAPI 
from api.data.MySQL_API import AnsibleSaveResult



class MyInventory(Inventory):  
    """ 
    this is my ansible inventory object. 
    """  
    def __init__(self, resource, loader, variable_manager):  
        """ 
        resource的数据格式是一个列表字典，比如 
            { 
                "group1": { 
                    "hosts": [{"hostname": "10.0.0.0", "port": "22", "username": "test", "password": "pass"}, ...], 
                    "vars": {"var1": value1, "var2": value2, ...} 
                } 
            } 
            如果你只传入1个列表，这默认该列表内的所有主机属于my_group组,比如 
            [{"hostname": "10.0.0.0", "port": "22", "username": "test", "password": "pass"}, ...] 
        """  
        self.resource = resource  
        self.inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=[])  
        self.dynamic_inventory()  
  
    def add_dynamic_group(self, hosts, groupname, groupvars=None):  
        """ 
            add hosts to a group 
        """  
        my_group = Group(name=groupname)  
  
        # if group variables exists, add them to group  
        if groupvars:  
            for key, value in groupvars.iteritems():  
                my_group.set_variable(key, value)  
  
        # add hosts to group  
        for host in hosts:  
            # set connection variables  
            hostname = host.get("hostname")  
            hostip = host.get('ip', hostname)  
            hostport = host.get("port")  
            username = host.get("username")  
            password = host.get("password")
            if username == 'root':
                keyfile = "/root/.ssh/id_rsa"
            else:
                keyfile = "/home/{user}/.ssh/id_rsa".format(user=username)  
            ssh_key = host.get("ssh_key",keyfile)  
            my_host = Host(name=hostname, port=hostport)  
            my_host.set_variable('ansible_ssh_host', hostip)  
            my_host.set_variable('ansible_ssh_port', hostport)  
            my_host.set_variable('ansible_ssh_user', username)  
            my_host.set_variable('ansible_ssh_pass', password)  
            my_host.set_variable('ansible_ssh_private_key_file', ssh_key)  

  
            # set other variables  
            for key, value in host.iteritems():  
                if key not in ["hostname", "port", "username", "password"]:  
                    my_host.set_variable(key, value)  
            # add to group  
            my_group.add_host(my_host)  
  
        self.inventory.add_group(my_group)  
  
    def dynamic_inventory(self):  
        """ 
            add hosts to inventory. 
        """  
        if isinstance(self.resource, list):  
            self.add_dynamic_group(self.resource, 'default_group')  
        elif isinstance(self.resource, dict):  
            for groupname, hosts_and_vars in self.resource.iteritems():  
                self.add_dynamic_group(hosts_and_vars.get("hosts"), groupname, hosts_and_vars.get("vars")) 


class ModelResultsCollector(CallbackBase):  
  
    def __init__(self, *args, **kwargs):  
        super(ModelResultsCollector, self).__init__(*args, **kwargs)  
        self.host_ok = {}  
        self.host_unreachable = {}  
        self.host_failed = {}  
  
    def v2_runner_on_unreachable(self, result):  
        self.host_unreachable[result._host.get_name()] = result 
  
    def v2_runner_on_ok(self, result,  *args, **kwargs):  
        self.host_ok[result._host.get_name()] = result  

  
    def v2_runner_on_failed(self, result,  *args, **kwargs):  
        self.host_failed[result._host.get_name()] = result  

        
class ModelResultsCollectorToSave(CallbackBase):  
  
    def __init__(self, redisKey,logId,*args, **kwargs):
        super(ModelResultsCollectorToSave, self).__init__(*args, **kwargs)  
        self.host_ok = {}  
        self.host_unreachable = {}  
        self.host_failed = {}  
        self.redisKey = redisKey
        self.logId = logId
        
    def v2_runner_on_unreachable(self, result):  
        for remove_key in ('changed', 'invocation'):
            if remove_key in result._result:
                del result._result[remove_key] 
        data = "{host} | UNREACHABLE! => {stdout}".format(host=result._host.get_name(),stdout=json.dumps(result._result,indent=4))    
        RedisAPI.AnsibleModel.lpush(self.redisKey,data) 
        if self.logId:
            AnsibleSaveResult.Model.insert(self.logId, data)
   
        
    def v2_runner_on_ok(self, result,  *args, **kwargs):   
        for remove_key in ('changed', 'invocation'):
            if remove_key in result._result:
                del result._result[remove_key]       
        if result._result.has_key('rc') and result._result.has_key('stdout'):
            data = "{host} | SUCCESS | rc={rc} >> \n{stdout}".format(host=result._host.get_name(),rc=result._result.get('rc'),stdout=result._result.get('stdout'))
        else:
            data = "{host} | SUCCESS >> {stdout}".format(host=result._host.get_name(),stdout=json.dumps(result._result,indent=4))
        RedisAPI.AnsibleModel.lpush(self.redisKey,data)
        if self.logId:
            AnsibleSaveResult.Model.insert(self.logId, data)
  
    def v2_runner_on_failed(self, result,  *args, **kwargs):   
        for remove_key in ('changed', 'invocation'):
            if remove_key in result._result:
                del result._result[remove_key]
        if result._result.has_key('rc') and result._result.has_key('stdout'):
            data = "{host} | FAILED | rc={rc} >> \n{stdout}".format(host=result._host.get_name(),rc=result._result.get('rc'),stdout=result._result.get('stdout'))
        else:
            data = "{host} | FAILED! => {stdout}".format(host=result._host.get_name(),stdout=json.dumps(result._result,indent=4))
        RedisAPI.AnsibleModel.lpush(self.redisKey,data)
        if self.logId:
            AnsibleSaveResult.Model.insert(self.logId, data)

            
class ANSRunner(object):  
    """ 
    This is a General object for parallel execute modules. 
    """  
    def __init__(self,resource,redisKey=None,logId=None,*args, **kwargs):  
        self.resource = resource  
        self.inventory = None  
        self.variable_manager = None  
        self.loader = None  
        self.options = None  
        self.passwords = None  
        self.callback = None  
        self.__initializeData(kwargs)  
        self.results_raw = {}  
        self.redisKey = redisKey
        self.logId = logId
  
    def __initializeData(self,kwargs):
        """ 初始化ansible """  
        """
        Options = namedtuple('Options', ['connection','module_path', 'forks', 'timeout',  'remote_user',  
                'ask_pass', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',  
                'scp_extra_args', 'become', 'become_method', 'become_user', 'ask_value_pass', 'verbosity',  
                'check', 'listhosts', 'listtasks', 'listtags', 'syntax'])  
        """
        Options = namedtuple('Options', ['connection','module_path', 'forks', 'timeout',  
                'ask_pass', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',  
                'scp_extra_args', 'become', 'become_method', 'become_user', 'ask_value_pass', 'verbosity',  
                'check', 'listhosts', 'listtasks', 'listtags', 'syntax'])  
        self.variable_manager = VariableManager()  
        self.loader = DataLoader()  
        """
        self.options = Options(connection='smart', module_path=None, forks=100, timeout=10,  
                remote_user=kwargs.get('remote_user','root'), ask_pass=False, private_key_file=None, ssh_common_args=None, 
                ssh_extra_args=None,sftp_extra_args=None, scp_extra_args=None, become=True,
                become_method=kwargs.get('become_method','sudo'),become_user=kwargs.get('become_user','root'), 
                verbosity=kwargs.get('verbosity',None),check=False, listhosts=False,
                listtasks=False, listtags=False, syntax=False,ask_value_pass=False, )  
        """
        self.options = Options(connection='smart', module_path=None, forks=100, timeout=10,  
                ask_pass=False, private_key_file=None, ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, 
                scp_extra_args=None, become=False, become_method=None,become_user=None, 
                verbosity=kwargs.get('verbosity',None),check=False, listhosts=False,
                listtasks=False, listtags=False, syntax=False,ask_value_pass=False, )        
        self.passwords = dict(sshpass=None, becomepass=None)  
        self.inventory = MyInventory(self.resource, self.loader, self.variable_manager).inventory
        self.variable_manager.set_inventory(self.inventory)  
  
    def run_model(self, host_list, module_name, module_args):  
        """ 
        run module from andible ad-hoc. 
        module_name: ansible module_name 
        module_args: ansible module args 
        """  
        play_source = dict(  
                name="Ansible Play",  
                hosts=host_list,  
                gather_facts='no',  
                tasks=[dict(action=dict(module=module_name, args=module_args))]  
        )
         
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)  
        tqm = None  
        if self.redisKey or self.logId:
            self.callback = ModelResultsCollectorToSave(self.redisKey,self.logId)  
        else:
            self.callback = ModelResultsCollector()  
        try:  
            tqm = TaskQueueManager(  
                    inventory=self.inventory,  
                    variable_manager=self.variable_manager,  
                    loader=self.loader,  
                    options=self.options,  
                    passwords=self.passwords,  
            )  
            tqm._stdout_callback = self.callback  
            constants.HOST_KEY_CHECKING = False #关闭第一次使用ansible连接客户端是输入命令
            tqm.run(play)  
        except Exception as err: 
            if self.redisKey:
                RedisAPI.AnsibleModel.lpush(self.redisKey,data=err)
            if self.logId:
                AnsibleSaveResult.Model.insert(self.logId, err)              
        finally:  
            if tqm is not None:  
                tqm.cleanup()  
      
        
if __name__ == '__main__':
    resource = [
                 {"hostname": "192.168.100.129", "port": "22", "username": "zhifu_v35", "password": "12345678"},
                 ]
    rbt = ANSRunner(resource,redisKey='1')
    rbt.run_model(host_list=["192.168.100.129"],module_name='yum',module_args="name=htop state=present")
