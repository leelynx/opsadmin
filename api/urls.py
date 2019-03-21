from django.conf.urls import url

from api.play import views as play_views
from api.pcloud import views as pcloud_views
from api.tomcat import views as tomcat_views
from api.opstask import views as tasks_views
from . import views
urlpatterns = [
    url(r'^create/hosts', views.create_ansible_hosts, name='create_ansible_hosts'),
    url(r'^upload/file', views.upload_file_api, name='upload_file_api'),
	url(r'^play/get/config', play_views.play_config_get, name="play_config_get"),
    url(r'^play/save/config', play_views.play_config_save, name="play_config_save"), 
    url(r'^pcloud/log', pcloud_views.pcloud_read_ansible_log, name="pcloud_read_ansible_log"),
    url(r'^pcloud/revoke/job', pcloud_views.pcloud_revoke_ansible_job, name="pcloud_revoke_ansible_job"),
    url(r'^play/log', play_views.play_read_ansible_log, name="play_read_ansible_log"),
    url(r'^revoke/job', views.revoke_ansible_task, name="revoke_ansible_task"),
    url(r'^get/group', views.get_ansible_group, name='get_ansible_group'),
    url(r'^service/list',views.get_service_list, name="get_service_list"),
    url(r'^task/log',tasks_views.read_ansible_execute_log, name="read_ansible_execute_log"),
]
