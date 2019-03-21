# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class ServerLoadBalancer(models.Model):
    slb_name = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"SLB名称")
    slb_area = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"SLB区域") 
    slb_host = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"SLB地址")
    slb_port = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"SLB端口") 
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"SLB描述")
    def __unicode__(self):
        return self.slb_name
    class Meta:
        permissions = (
            ("has_read_slb", "读取SLB权限"),
            ("has_change_slb", "修改SLB权限"),
            ("has_add_slb", "添加SLB权限"),
            ("has_delete_slb", "删除SLB权限"),
        )
        verbose_name = u"负载均衡"
        verbose_name_plural = verbose_name
        db_table = "ops_slb"
        

class BackendServer(models.Model):
    server_name = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"后端主机名称")
    server_area = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"主机所在区域")
    slb_name = models.ForeignKey(ServerLoadBalancer, related_name='slb', verbose_name=u"负载均衡名称")
    server_ip = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"后端主机地址")
    server_port = models.CharField(max_length=16, blank=True, null=True, verbose_name=u"后端主机端口")
    weight = models.SmallIntegerField(blank=True, null=True, verbose_name=u"后端主机权重")
    max_fails = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"最大失败次数")
    fail_timeout = models.CharField(max_length=8, blank=True, null=True, verbose_name=u"后端主机超时")
    update_key = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"配置同步key")
    comment = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"后端主机描述")
    def __unicode__(self):
        return self.server_name
    class Meta:
        permissions = (
            ("has_read_backendserver", "读取BackendServer权限"),
            ("has_change_backendserver", "修改BackendServer权限"),
            ("has_add_backendserver", "添加BackendServer权限"),
            ("has_delete_backendserver", "删除BackendServer权限"),
        )
        verbose_name = u"负载均衡后端服务器"
        verbose_name_plural = verbose_name
        db_table = "ops_slb_backend_server"
        
        
        
        