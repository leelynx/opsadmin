from django.conf.urls import url
from opstask.views import ansible_task_playbook_roles, ansible_logs_record, ansible_ad_hoc
urlpatterns = [
#   url(r'^flow/list/$', views.ansible_task_list, name='ansible_task_list'),
    #url(r'^create/task/$', ansible_task_playbook_roles.ansible_task_create, name='ansible_task_create'),
#    url(r'^flow/release/$', views.ansible_task_release, name='ansible_task_release'),
#    url(r'^flow/del/$', views.ansible_task_del, name='ansible_task_del'),
#    url(r'^flow/edit/$', views.ansible_task_edit, name='ansible_task_edit'),
    url(r'^get/host', ansible_ad_hoc.get_host_list, name='get_host_list'),
    url(r'^workflow/create', ansible_task_playbook_roles.create_workflow_task, name='create_workflow_task'),
    url(r'^release/type', ansible_task_playbook_roles.get_ansible_task_type, name="get_ansible_task_type"),
    url(r'^create/task', ansible_task_playbook_roles.ansible_task_create, name="ansible_task_create"),
    url(r'^do/(?P<pid>\d+)/(?P<action>[a-z]+)', ansible_task_playbook_roles.ansible_task_manager, name="ansible_task_manager"),
    url(r'^task/list', ansible_task_playbook_roles.ansible_task_manager, name="task_sheet_list"),
    url(r'^record/list', ansible_logs_record.ansible_task_record, name='ansible_task_record'),
    url(r'^tomcat/task/(?P<pid>[0-9]+)', ansible_task_playbook_roles.create_task_tomcat, name='create_task_tomcat'),
    url(r'^play/task/(?P<pid>[0-9]+)', ansible_task_playbook_roles.create_task_play, name='create_task_play'),
    url(r'^restart/(?P<pid>[0-9]+)',ansible_task_playbook_roles.create_process_control_task, name="create_process_control_task"),
]