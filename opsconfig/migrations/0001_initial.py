# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-27 10:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BackendServer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_name', models.CharField(blank=True, max_length=16, null=True, verbose_name='\u540e\u7aef\u4e3b\u673a\u540d\u79f0')),
                ('server_area', models.CharField(blank=True, max_length=8, null=True, verbose_name='\u4e3b\u673a\u6240\u5728\u533a\u57df')),
                ('server_ip', models.CharField(blank=True, max_length=16, null=True, verbose_name='\u540e\u7aef\u4e3b\u673a\u5730\u5740')),
                ('server_port', models.CharField(blank=True, max_length=16, null=True, verbose_name='\u540e\u7aef\u4e3b\u673a\u7aef\u53e3')),
                ('weight', models.CharField(blank=True, max_length=8, null=True, verbose_name='\u540e\u7aef\u4e3b\u673a\u6743\u91cd')),
                ('max_fails', models.CharField(blank=True, max_length=8, null=True, verbose_name='\u6700\u5927\u5931\u8d25\u6b21\u6570')),
                ('fail_timeout', models.CharField(blank=True, max_length=8, null=True, verbose_name='\u540e\u7aef\u4e3b\u673a\u8d85\u65f6')),
                ('update_key', models.CharField(blank=True, max_length=128, null=True, verbose_name='\u914d\u7f6e\u540c\u6b65key')),
                ('comment', models.CharField(blank=True, max_length=128, null=True, verbose_name='\u540e\u7aef\u4e3b\u673a\u63cf\u8ff0')),
            ],
            options={
                'db_table': 'ops_slb_backend_server',
                'verbose_name': '\u8d1f\u8f7d\u5747\u8861\u540e\u7aef\u670d\u52a1\u5668',
                'verbose_name_plural': '\u8d1f\u8f7d\u5747\u8861\u540e\u7aef\u670d\u52a1\u5668',
            },
        ),
        migrations.CreateModel(
            name='ServerLoadBalancer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slb_name', models.CharField(blank=True, max_length=16, null=True, verbose_name='SLB\u540d\u79f0')),
                ('slb_area', models.CharField(blank=True, max_length=8, null=True, verbose_name='SLB\u533a\u57df')),
                ('slb_host', models.CharField(blank=True, max_length=16, null=True, verbose_name='SLB\u5730\u5740')),
                ('slb_port', models.CharField(blank=True, max_length=8, null=True, verbose_name='SLB\u7aef\u53e3')),
                ('comment', models.CharField(blank=True, max_length=128, null=True, verbose_name='SLB\u63cf\u8ff0')),
            ],
            options={
                'db_table': 'ops_slb',
                'verbose_name': '\u8d1f\u8f7d\u5747\u8861',
                'verbose_name_plural': '\u8d1f\u8f7d\u5747\u8861',
            },
        ),
        migrations.AddField(
            model_name='backendserver',
            name='slb_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='slb', to='opsconfig.ServerLoadBalancer', verbose_name='\u8d1f\u8f7d\u5747\u8861\u540d\u79f0'),
        ),
    ]
