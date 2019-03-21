# -*- coding: utf-8 -*-
#descriptions:  some variables use to  ansible task 


"""
  定义任务中ansible playbook 运行脚本变量
"""

######################product####################################
"""ansible脚本存储路径"""

ANSIBLE_PLAYBOOK_REPOSITORY_PATH = {
    'play_path': '/opt/tasks/play', 
    'tomcat_path': '/opt/tasks/tomcat', 
    'pcloud_path': '/opt/tasks/pcloud',
    'abroad_root_path': '/opt/tasks/abroad-root'
 }

######################development################################
"""ansible脚本存储路径"""
"""
ANSIBLE_PLAYBOOK_REPOSITORY_PATH = {
    'play_path': '/devops/frameworks/play', 
    'tomcat_path': '/devops/frameworks/tomcat', 
    'pcloud_path': '/devops/frameworks/pcloud',
    'abroad_root_path': '/devops/frameworks/abroad-root-tomcat'
  }
"""
"""支付网关play容器目录结构"""
PLAY_FRAMEWORK = {'config': 'conf', 'lib_path': 'lib', 'plugins_path': 'plugins', 'log': 'logs', 'temp': 'temp'}
PLAY_CONFIG_TYPE = {'app': 'application.conf', 'api': 'thirdplay-api.conf', 'cache': 'cache.conf', 'reload': 'reloadable.conf'}
PLAY_CONFIG_FILE = ['application.conf', 'thirdpay-api.conf', 'cache.conf',  'reloadable.conf']

"""play框架ansible发布任务角色分类"""
ANSIBLE_PLAY_ROLES = {
    'play_svn_release_task': 'Play_svn_release_task', 
    'play_trans_release_task':'Play_trans_release_task', 
    'play_increment_release_task': 'Play_increment_release_task', 
    'play_config_release_task': 'Play_config_release_task',
    'play_restart_task': 'Play_restart_task',
    'play_rollback_task': 'Play_rollback_task'
  }

"""tomcat 框架目录结构"""
TOMCAT_FRAMEWORK = {'config':'conf','bin':'bin','webapps':'webapps','log':'logs','lib':'lib'}
TOMCAT_CONFIG_TYPE = {'server.xml':'server.xml', 'cache':'cache.properties', 'log':'log4j2.xml', 'app':'app-config.properties'}

"""私有云ansible专属任务角色分类"""
ANSIBLE_PCLOUD_ROLES = {
    'pcloud_svn_release_task': 'Pcloud_svn_release_task', 
    'pcloud_trans_release_task': 'Pcloud_trans_release_task', 
    'pcloud_jar_add_task': 'Pcloud_jar_add_task',
    'pcloud_jar_delete_task': 'Pcloud_jar_delete_task',
    'pcloud_config_add_task': 'Pcloud_config_add_task',
    'pcloud_config_delete_task': 'Pcloud_config_delete_task',
    'pcloud_config_mod_task': 'Pcloud_config_mod_task', 
    'pcloud_restart_task': 'Pcloud_restart_task',
    'pcloud_rollback_config_task':'Pcloud_rollback_config_task',
    'pcloud_rollback_pack_task': 'Pcloud_rollback_pack_task'
  }
PCLOUD_APP_TYPE = ['private_cloud']



"""tomcat框架 ansible 通用任务角色分类"""
ANSIBLE_TOMCAT_ROLES = {
    'tomcat_svn_release_task':'Tomcat_svn_release_task', 
    'tomcat_trans_release_task':'Tomcat_trans_release_task',
    'tomcat_pack_add_task':'Tomcat_pack_add_task',
    'tomcat_pack_del_task':'Tomcat_pack_del_task',
    'tomcat_config_add_task':'Tomcat_config_add_task',
    'tomcat_config_mod_task':'Tomcat_config_mod_task',
    'tomcat_restart_task': 'Tomcat_restart_task',
    'tomcat_rollback_pack_task':'Tomcat_rollback_pack_task',
    'tomcat_rollback_config_task':'Tomcat_rollback_config_task'
  }

"""独立脚本发布项目"""
UNIQUE_APP_LIST = ['abroad-root-tomcat', 'unionpass-root-tomcat', 'hase-root-tomcat']
