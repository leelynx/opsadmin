"""opsadmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views import static
from django.views.generic.base import RedirectView
from . import views as auth_views
from opsadmin.dashboard.index import index, get_chart_data
from opsadmin.systools.tools import systools_upload_files
from opstask.views.ansible_ad_hoc import (ansible_create_script, 
                                  ansible_run_script, 
                                  ansible_polling_result, 
                                  ansible_edit_script ,
                                  ansible_del_script, 
                                  ansible_list_script,
                                  ansible_model_cmd)
from opstask.views import ansible_logs_record
from opstask.views.rollback import tomcat, play                      
                                  
urlpatterns = [

    url(r'^admin', include(admin.site.urls)),
    url(r'^forbidden', auth_views.auth_forbidden, name='auth_forbidden'),
    url(r'^favicon.ico', RedirectView.as_view(url=r'/static/img/favicon.ico')),
    url(r'^static/(?P<path>.*)$', static.serve, { 'document_root': settings.STATICFILES_DIRS}), 
	url(r'^login', auth_views.auth_login, name='login'),
    url(r'^logout', auth_views.auth_logout, name="logout"),
    url(r'^change_password', auth_views.change_password, name="change_password"),
    url(r'^$', index, name='index'),
    url(r'^index/chart/$', get_chart_data, name='get_chart_data'),
    url(r'^ops/create/script', ansible_create_script, name="ansible_create_script"),
    url(r'^ops/edit/script/(?P<pid>[0-9]+)', ansible_edit_script, name="ansible_edit_script"),
    url(r'^ops/del/script', ansible_del_script, name="ansible_del_script"),
    url(r'^ops/list/script', ansible_list_script, name="ansible_list_script"),
    url(r'^ops/run/script', ansible_run_script, name="ansible_run_script"),
    url(r'^ops/script/result', ansible_polling_result, name="ansible_polling_result"),
    url(r'^ops/play/', include('opstask.play.urls')),
    url(r'^ops/pcloud/', include('opstask.pcloud.urls')),
    url(r'^rollback/tomcat/(?P<pid>[0-9]+)', tomcat.tomcat_rollback_task, name="tomcat_rollback_task"),
    url(r'^rollback/play/(?P<pid>[0-9]+)', play.play_rollback_task, name="play_rollback_task"),
    url(r'^logs/playbook', ansible_logs_record.ansible_playbook_logs, name='ansible_playbook_logs'),
    url(r'^logs/script', ansible_logs_record.ansible_script_logs, name='ansible_script_logs'),
    url(r'^logs/detail/playbook', ansible_logs_record.ansible_playbook_logs_detail, name='ansible_playbook_logs_detail'),
    url(r'^logs/detail/script', ansible_logs_record.ansible_script_logs_detail, name='ansible_script_logs_detail'),
    url(r'^tools/upload/file', systools_upload_files, name='systools_upload_files'),
    url(r'^tools/ansible/cmd', ansible_model_cmd, name='ansible_model_cmd'),
    url(r'^cmdb/',include('cmdb.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^opstask/', include('opstask.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^config/',include('opsconfig.urls'))
]
