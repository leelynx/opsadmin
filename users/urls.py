from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^group/add/$', views.user_group_add, name='user_group_add'),
    url(r'^group/list/$', views.user_group_list, name='user_group_list'),
    url(r'^group/del/$', views.user_group_del, name='user_group_del'),
    url(r'^group/edit/$', views.user_group_edit, name='user_group_edit'),
    url(r'^user/add/$', views.user_add, name='user_add'),
    url(r'^user/list/$', views.user_list, name='user_list'),
    url(r'^user/del/$', views.user_del, name='user_del'),
    url(r'^user/edit/$', views.user_edit, name='user_edit'),
    url(r'^perm/add/$', views.perm_rule_add, name='perm_rule_add'),
    url(r'^perm/list/$', views.perm_rule_list, name='perm_rule_list'),
    url(r'^perm/del/$', views.perm_rule_del, name='perm_rule_del'),
    url(r'^perm/edit/$', views.perm_rule_edit, name='perm_rule_edit'),
]