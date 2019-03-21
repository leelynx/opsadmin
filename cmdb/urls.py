from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^server/list', views.cmdb_server_list, name='cmdb_server_list'),
    url(r'^server/add', views.cmdb_server_add, name='cmdb_server_add'),
    url(r'^server/edit', views.cmdb_server_edit, name='cmdb_server_edit'),
    url(r'^server/detail', views.cmdb_server_detail, name='cmdb_server_detail'),
    url(r'^server/del',  views.cmdb_server_del, name='cmdb_server_del'),
    url(r'^project/list', views.cmdb_project_list, name='cmdb_project_list'),
    url(r'^project/add', views.cmdb_project_add, name='cmdb_project_add'),
    url(r'^project/del', views.cmdb_project_del, name='cmdb_project_del'),
    url(r'^project/edit', views.cmdb_project_edit, name='cmdb_project_edit'),
    url(r'^app/list', views.cmdb_app_list, name='cmdb_app_list'),
    url(r'^app/add', views.cmdb_app_add, name='cmdb_app_add'),
    url(r'^app/del', views.cmdb_app_del, name='cmdb_app_del'),
    url(r'^app/edit', views.cmdb_app_edit, name='cmdb_app_edit'),
    url(r'^app/detail', views.cmdb_app_detail, name='cmdb_app_detail'),
    url(r'^ansible/list', views.cmdb_ansible_list, name='cmdb_ansible_list'),
    url(r'^ansible/add', views.cmdb_ansible_add, name='cmdb_ansible_add'),
    url(r'^ansible/del', views.cmdb_ansible_del, name='cmdb_ansible_del'),
    url(r'^ansible/edit', views.cmdb_ansible_edit, name='cmdb_ansible_edit'),
]