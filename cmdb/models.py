    # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.timezone import now

# Create your models here.

CMDB_TYPE = (
    (1, u"私有云"),
    (2, u"支付平台"),
    (3, u"SPAY支付"),
    (4, u"3.5平台"),
    (5, u"其他项目"),
    )
class AnsibleGroup(models.Model):
    """
    ansible host group
    """
    group_id = models.AutoField(primary_key=True)
    group = models.CharField(max_length=32, unique=True)
    app_type = models.CharField(max_length=32, blank=True, null=True)
    comment = models.CharField(max_length=128, blank=True, null=True)
    def __unicode__(self):
        return self.group
    class Meta:
        permissions = (
            ("has_read_ansible_group", "读取ansible组权限"),
            ("has_change_ansible_group", "修改ansible组权限"),
            ("has_add_ansible_group", "添加ansible组权限"),
            ("has_delete_ansible_group", "删除ansible组权限"),
        )
        verbose_name = u"ansible分组"
        verbose_name_plural = verbose_name
        db_table = "ops_hosts_group" 

class PlatformType(models.Model):
    """
    project classification
    """
    platform_id  = models.AutoField(primary_key=True)
    platform_name = models.CharField(max_length=16, unique=True)
    short_name = models.CharField(max_length=16, blank=True)
    comment = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return self.platform_name
    class Meta:
        permissions = (
            ("has_read_project", "读取项目权限"),
            ("has_change_project", "修改项目权限"),
            ("has_add_project", "添加项目权限"),
            ("has_delete_project", "删除项目权限"),
        )
        verbose_name = u"项目分类"
        verbose_name_plural = verbose_name
        db_table = "ops_platform" 

class ServerInfo(models.Model):
    """
    server host information
    """
    server_id = models.AutoField(primary_key=True)
    private_ip = models.CharField(max_length=16, verbose_name=u"私网地址")
    resource_area = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"所在区域")
    hostname = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"主机名称")
    username = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"SSH用户")
    password = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"SSH密码")
    rsa_key = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"SSH密钥")
    host_port = models.IntegerField(blank=True, null=True, verbose_name=u"SSH端口")
    platform = models.ForeignKey(PlatformType, blank=True, null=True, verbose_name=u'项目平台')
    ab_group= models.ManyToManyField(AnsibleGroup, related_name='serverinfos', verbose_name=u'Ansible分组')
    create_time = models.DateTimeField(default=now, blank=True, verbose_name="创建时间")
    def __unicode__(self):
        return self.private_ip
    class Meta:
        permissions = (
            ("has_read_server", "读取主机权限"),
            ("has_change_server", "修改主机权限"),
            ("has_add_server", "添加主机权限"),
            ("has_delete_server", "删除主机权限"),
        )
        verbose_name = u"服务器信息"
        verbose_name_plural = verbose_name
        db_table = "ops_hosts"


class AppInfo(models.Model):
    """
    app information
    """
    STATUS_TYPE = (
        (0, u"禁用"),
        (1, u"启用"),
        (2, u"初始化"),
        (3, u"发布中"),
        (4, u"发布完成"),
    )
    app_id = models.AutoField(primary_key=True)
    app_ip = models.ManyToManyField(ServerInfo, related_name='app_server_ip', verbose_name=u"应用地址")
    app_name = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"应用名称")
    app_alias = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"项目名称")
    app_type = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"应用类型")
    app_status = models.SmallIntegerField(blank=True, null=True, choices=STATUS_TYPE, verbose_name=u"应用状态")
    frameworks = models.CharField(max_length=10, blank=True, null=True, verbose_name=u"框架类型")
    main_path = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"部署路径")
    service_path = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"私有云service路径")
    root_path = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"私有云root路径")
    run_port = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"程序端口")
    svn_path = models.CharField(max_length=512, blank=True, null=True, verbose_name=u"SVN链接")
    backup_path = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"备份路径")
    work_path = models.CharField(max_length=32, blank=True, null=True, verbose_name=u"工作区间")
    create_time = models.DateTimeField(default=now, blank=True, verbose_name="创建时间")

    def __unicode__(self):
        return self.app_name
   
    class Meta:
        permissions = (
            ("has_read_app", "读取应用权限"),
            ("has_change_app", "修改应用权限"),
            ("has_add_app", "添加应用权限"),
            ("has_delete_app", "删除应用权限"),
        )
        verbose_name = u"程序应用信息"
        verbose_name_plural = verbose_name
        db_table = "ops_apps"


class BackupLogs(models.Model):
    """
    project releasse backup records
    """
    backup_id = models.AutoField(primary_key=True)
    app_name = models.CharField(max_length=32, blank=True, null=True)
    project = models.CharField(max_length=32, blank=True, null=True)
    backup_file = models.CharField(max_length=256, blank=True, null=True)
    create_date = models.CharField(max_length=32, blank=True, null=True)
    
    def __unicode__(self):
        return self.app_name

    
    class Meta:
        verbose_name = u"文件备份信息"
        verbose_name_plural = verbose_name
        db_table = "ops_backup_log"
        
