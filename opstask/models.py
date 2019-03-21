# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class TaskTemplate(models.Model):
    temp_name = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"发布模板名称")
    app_name = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"发布程序名称")
    app_type = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"项目类型")
    frame_type = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"程序框架")
    release_type = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"发布方式")
    host_group = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"发布主机组")
    playbook = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"发布任务信息")
    inventory = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"发布主机信息")
    update_time = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"模板更新时间")
    get_code = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"获取代码方式")
    code_path = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"代码存储路径")
    creator = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"模板创建者")
    state = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"流程状态")
    comment = models.CharField(max_length=256, blank=True, null=True)
    
    def __unicode__(self):
        return self.temp_name, self.app_name
    class Meta:
        verbose_name = u"任务模板"
        verbose_name_plural = verbose_name
        db_table = "ops_task_template"
              
        
class JobLogs(models.Model):
    """
    ansible execute logs
    """
    job_name = models.CharField(max_length=64, blank=True, null=True)
    job_uuid = models.CharField(max_length=64, blank=True, null=True)
    app_type = models.CharField(max_length=32, blank=True, null=True)
    start_time = models.CharField(max_length=32, blank=True, null=True)
    end_time = models.CharField(max_length=32, blank=True, null=True)
    runtime = models.CharField(max_length=8, blank=True, null=True)
    state = models.CharField(max_length=8, blank=True, null=True)
    excutor = models.CharField(max_length=16, blank=True, null=True)
    version_description = models.TextField(blank=True, null=True)
    detail = models.TextField(blank=True, null=True)
    
    
    def __unicode__(self):
        return self.job_name 
    class Meta:
        verbose_name = u"作业执行历史"
        verbose_name_plural = verbose_name
        db_table = "ops_job_logs"

 
class AnsibleTaskRecord(models.Model):
    app_name = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"程序名称")
    app_type = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"项目类型")
    ansible_group = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"执行主机组")
    hosts_list = models.TextField(blank=True, null=True, verbose_name=u"执行主机列表")
    app_path = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"程序路径")
    release_path = models.CharField(max_length=512, blank=True, null=True, verbose_name=u"程序目标更新路径")
    update_file_type = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"发布包类型")
    backup_path = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"程序备份路径")
    backup_file = models.CharField(max_length=512, blank=True, null=True, verbose_name=u"程序备份文件") 
    ansible_user = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'操作用户')
    frameworks = models.CharField(max_length=10, blank=True, null=True, verbose_name=u"框架类型")
    release_tag = models.CharField(max_length=64, blank=True, null=True, verbose_name='发行版本tag')  
    create_time = models.CharField(max_length=32, blank=True, null=True, verbose_name='执行时间')
    state = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"回退状态")
    class Meta:
        db_table = 'ops_ansible_task_record'
        verbose_name = 'Ansible任务执行记录表'  
        verbose_name_plural = verbose_name 


class AnsibleScripts(models.Model):
    """
    ansible script
    """
    script_name = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"脚本名称")
    script_uuid = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"脚本uuid")
    exec_host = models.TextField(blank=True, null=True, verbose_name=u"脚本执行主机")
    script_file = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"脚本文件")
    script_arg = models.CharField(max_length=256, blank=True, null=True, verbose_name=u"脚本参数")
    exec_timeout = models.CharField(max_length=4, blank=True, null=True, verbose_name=u"脚本执行超时时间")
    creator = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"脚本创建者")
    create_time = models.CharField(max_length=32, blank=True, null=True, verbose_name="脚本创建时间")
    modifier = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"脚本修改者")
    modify_time = models.CharField(max_length=32, blank=True, null=True, verbose_name="脚本修改时间")
    debug_mode = models.CharField(max_length=4, default='off', verbose_name="脚本调试模式")
    state = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"脚本状态")
    def __unicode__(self):
        return self.script_name
    class Meta:
        verbose_name = u"ansible作业脚本"
        verbose_name_plural = verbose_name
        db_table = "ops_ansible_scripts"


class AnsibleModelRecord(models.Model): 
    ansible_user = models.CharField(max_length=16, verbose_name='操作用户', default=None)
    ansible_host = models.TextField(blank=True, null=True, verbose_name=u"脚本执行主机")
    ansible_model = models.CharField(max_length=16, blank=True, null=True, verbose_name='模块名称',)
    ansible_args = models.CharField(max_length=500, blank=True,null=True, verbose_name='模块参数',default=None)
    create_time = models.CharField(max_length=32, blank=True, null=True, verbose_name='执行时间')
    end_time = models.CharField(max_length=32, blank=True, null=True, verbose_name='结束时间')
    class Meta:
        db_table = 'ops_ansible_model_record'
        verbose_name = 'Ansible模块执行记录表'  
        verbose_name_plural = verbose_name 

       
class Ansible_CallBack_Model_Result(models.Model):
    log_id = models.ForeignKey('AnsibleModelRecord')
    content = models.TextField(verbose_name='输出内容',blank=True,null=True)
    class Meta:
        db_table = 'ops_ansible_model_result'
        verbose_name = 'Ansible模块执行结果日志'  
        verbose_name_plural = verbose_name   

class AnsibleTaskList(models.Model):
    app_id = models.SmallIntegerField(verbose_name=u"应用ID")
    app_type = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"项目类型")
    app_name = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"程序名称")
    app_version = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"程序版本")
    creator = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'任务创建者')
    change_logs = models.TextField(blank=True, null=True, verbose_name=u"程序版本变更日志")
    release_type = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"发布类型")
    get_code = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"获取代码方式")
    svn_path = models.CharField(max_length=256, blank=True, null=True, verbose_name=u"svn路径")
    dst_path = models.CharField(max_length=256, blank=True, null=True, verbose_name=u"增量发布包路径")
    ansible_group = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"执行主机组")
    hosts_list = models.TextField(blank=True, null=True, verbose_name=u"执行主机列表")
    reload_switch = models.CharField(max_length=4, blank=True, null=True, verbose_name=u"程序重启开关")
    task_run_type = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"ansible任务运行方式")
    task_status = models.SmallIntegerField(default=0, verbose_name=u"任务状态")
    create_time = models.CharField(max_length=32, blank=True, null=True, verbose_name='执行时间')

    class Meta:
        db_table = 'ops_ansible_task_list'
        verbose_name = 'Ansible任务表'  
        verbose_name_plural = verbose_name 
