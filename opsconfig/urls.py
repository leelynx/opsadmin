from django.conf.urls import url

from opsconfig.slb import view
urlpatterns = [
    url(r'^slb/list/$', view.slb_list, name='slb_list'),
    url(r'^slb/add/$', view.slb_add, name='slb_add'),
    url(r'^slb/edit/$', view.slb_edit, name='slb_edit'),
    url(r'^slb/del/$', view.slb_del, name='slb_del'),
    url(r'^slb/backend/list/$', view.backend_server_list, name='backend_server_list'),
    url(r'^slb/backend/add/$', view.backend_server_add, name='backend_server_add'),
    url(r'^slb/backend/edit/$', view.backend_server_edit, name='backend_server_edit'),
    url(r'^slb/backend/update/$', view.backend_server_update, name='backend_server_update'),
    url(r'^slb/backend/del/$', view.backend_server_del, name='backend_server_del'),
]