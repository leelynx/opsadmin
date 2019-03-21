# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from cmdb.models import PlatformType
from django.contrib.auth.models import AbstractUser

# Create your models here.
class UserGroup(models.Model):
    name = models.CharField(max_length=32, unique=True)
    comment = models.CharField(max_length=128, blank=True)

    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = u"user group"
        verbose_name_plural = verbose_name
        db_table = "ops_user_group"     


class User(AbstractUser):
    USER_ROLE_CHOICES = (
        ('SU', 'SuperUser'),
        ('AM', 'Admin'),
        ('CU', 'CommonUser'),
    )
    name = models.CharField(max_length=32)
    role = models.CharField(max_length=2, choices=USER_ROLE_CHOICES, default='CU')
    group = models.ForeignKey(UserGroup)
    def __unicode__(self):
        return self.username
    class Meta:
        verbose_name = u"user list"
        verbose_name_plural = verbose_name
        db_table = "ops_users"
    def get_name(self):
        return self.name

class PermRule(models.Model):
    rule_name = models.CharField(max_length=32, blank=False, null=False)
    user_group = models.ManyToManyField(UserGroup, blank=True)
    username = models.ManyToManyField(User, blank=True)
    platform = models.ManyToManyField(PlatformType, blank=True)
    comment = models.CharField(max_length=64, blank=True, null=True)
    def __unicode__(self):
        return self.rule_name
    class Meta:
        verbose_name = u"perm_rule"
        verbose_name_plural = verbose_name
        db_table = "ops_perm_rule"
