# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from opsconfig.models import ServerLoadBalancer, BackendServer
from opsconfig.slb.forms import ServerLoadBalancerForm, BackendServerForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from api.views import role_required
from api.etcdconfig import EtcdConfig
import json
import logging
import traceback


@login_required(login_url='/login')
@permission_required('opsconfig.has_read_slb',login_url='/forbidden/')
def slb_list(request):
    """
    查看Nginx负载均衡
    """
    path1, path2, path3 = u'配置管理中心', u'Nginx负载均衡', u'实例管理'
    try:
        slbs = ServerLoadBalancer.objects.all()
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())
    return render(request,'slb/slb_list.html',locals())

@login_required(login_url='/login')
@permission_required('opsconfig.has_add_slb',login_url='/forbidden/')
def slb_add(request):
    """
    添加Nginx负载均衡
    """
    path1, path2, path3 = u'配置管理中心', u'Nginx负载均衡', u'添加实例'
    slb_form = ServerLoadBalancerForm()
    if request.method == 'POST':
        slb_host = request.POST.get('slb_host', '')
        slb_name = request.POST.get('slb_name', '')
        if ServerLoadBalancer.objects.filter(slb_name=slb_name):
            error = u'负载均衡 %s 已存在' % slb_name
        else:
            form = ServerLoadBalancerForm(request.POST)
            if form.is_valid():
                slb_form_save = form.save(commit=False)
                slb_form_save.save()
                form.save_m2m()
                msg = u'负载均衡 %s 添加成功' % slb_host
            else:
                error = u'负载均衡 %s 添加失败' % slb_host
    return render(request,'slb/slb_add.html',locals())

@login_required(login_url='/login')
@permission_required('opsconfig.has_chanage_slb',login_url='/forbidden/')
def slb_edit(request):
    """
    修改Nginx负载均衡信息
    """
    path1, path2, path3 = u'配置管理中心', u'Nginx负载均衡', u'修改实例'
    slb_id = request.GET.get('id', '')
    slb = ServerLoadBalancer.objects.get(id=slb_id)
    slb_form = ServerLoadBalancerForm(instance=slb)
    try:
        if request.method == 'POST':
            slb_post = ServerLoadBalancerForm(request.POST, instance=slb)
            ip = request.POST.get('slb_host', '')
            if slb_post.is_valid():
                slb_form_save = slb_post.save(commit=False)
                slb_form_save.save()
                slb_post.save_m2m()                
                msg = u'负载均衡 %s 修改成功' % ip
            else:
                error = u'负载均衡 %s 修改失败' % ip
    except Exception,e:
        error = e 
    return render(request,'slb/slb_edit.html',locals())

@login_required(login_url='/login')
@permission_required('opsconfig.has_delete_slb',login_url='/forbidden/')
def slb_del(request):
    """
    删除Nginx负载均衡实例
    """
    slb_id = request.GET.get('id', '')
    slb_id_list = slb_id.split(',')
    for id_num in slb_id_list:
        if id_num:
            ServerLoadBalancer.objects.filter(id=id_num).delete()    
    return HttpResponseRedirect(reverse('slb_list'))


@login_required(login_url='/login')
@permission_required('opsconfig.has_add_backendserver',login_url='/forbidden/')
def backend_server_add(request):
    """
    添加Nginx负载均衡后端服务器
    """
    path1, path2, path3 = u'配置管理中心', u'Nginx负载均衡', u'添加后端服务器'
    try:
        bks_form = BackendServerForm()
        if request.method == 'POST':
            server_ip = request.POST.get('server_ip', '')
            upstream_dict = {}
            #if BackendServer.objects.filter(server_ip=server_ip):
            #    error = u'后端服务器 %s 已存在' % server_ip
            # else:
            form = BackendServerForm(request.POST)
            if form.is_valid():
                bks_form_save = form.save(commit=False)
                bks_form_save.save()
                form.save_m2m()
                upstream_dict['host'] = "{0}:{1}".format(server_ip, request.POST.get('server_port', ''))
                upstream_dict['weight'] = request.POST.get('weight', '')
                upstream_dict['fails'] = request.POST.get('max_fails', '')
                upstream_dict['timeout'] = request.POST.get('fail_timeout', '')
                key = request.POST.get('update_key', '')
                upstream_dict = json.dumps(upstream_dict, ensure_ascii=False, encoding='utf-8')
                update_host = EtcdConfig(key, upstream_dict)
                update_host.set_value()
                msg = u'后端服务器 %s 添加成功' % server_ip
            else:
                error = u'后端服务器 %s 添加失败' % server_ip
    except:
        error = '%s' % traceback.format_exc()   
    return render(request,'slb/backend_server_add.html',locals())

@login_required(login_url='/login')
@permission_required('opsconfig.has_chanage_backendserver',login_url='/forbidden/')
def backend_server_edit(request):
    """
    修改Nginx负载均衡后端服务器信息
    """
    path1, path2, path3 = u'配置管理中心', u'Nginx负载均衡', u'修改后端服务器'
    try:
        global backend_server
        if request.method == 'GET':
            backend_server_id = request.GET.get('id', '')
            backend_server = BackendServer.objects.get(id=backend_server_id)
            backend_server_form = BackendServerForm(instance=backend_server)
            return render(request,'slb/backend_server_edit.html',locals())
        if request.method == 'POST':
            backend_server_post = BackendServerForm(request.POST, instance=backend_server)
            ip = request.POST.get('server_ip', '')
            if backend_server_post.is_valid():
                backend_server_save = backend_server_post.save(commit=False)
                backend_server_save.save()
                backend_server_post.save_m2m()                
                msg = u'后端服务器 %s 修改成功' % ip
                return HttpResponse(msg)
            else:
                error = u'后端服务器 %s 修改失败' % ip
                return HttpResponse(error)
    except Exception,e:
        return HttpResponse(e)


@login_required(login_url='/login')
@permission_required('opsconfig.has_chanage_backendserver',login_url='/forbidden/')
def backend_server_update(request):
    """
    修改Nginx负载均衡后端服务器权重
    """
    try:
        upstream_dict = {}
        if request.method == 'POST':
            backend_server_id = request.POST.get('pk', '')
            weight = request.POST.get('value', '')
            BackendServer.objects.filter(id=backend_server_id).update(weight=weight)
            if int(weight) == 0:
                key_list = BackendServer.objects.filter(id=backend_server_id).values('update_key')
                for key_dict in key_list:  
                    delete_host = EtcdConfig(key_dict['update_key'], '')
                    delete_host.delete_value()
            else:
                upstream_list = BackendServer.objects.filter(id=backend_server_id)
                for upstream in upstream_list:
                    upstream_dict['host'] = "{0}:{1}".format(upstream.server_ip, upstream.server_port)
                    upstream_dict['weight'] = upstream.weight
                    upstream_dict['fails'] = upstream.max_fails
                    upstream_dict['timeout'] = upstream.fail_timeout
                    key = upstream.update_key
                    upstream_dict = json.dumps(upstream_dict, ensure_ascii=False, encoding='utf-8')
                    update_host = EtcdConfig(key, upstream_dict)
                    update_host.set_value()
        return HttpResponse(json.dumps({'msg':'success'}))      
    except:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())
        return HttpResponse(json.dumps({'msg':'failed'}))

@login_required(login_url='/login')
@permission_required('opsconfig.has_delete_backendserver',login_url='/forbidden/')
def backend_server_del(request):
    """
    摘除Nginx负载均衡后端服务器
    """
    try:
        backend_server_id = request.GET.get('id', '')
        backend_server_id_list = backend_server_id.split(',')
        for id_num in backend_server_id_list:
            if id_num:
                bkserver = BackendServer.objects.filter(id=id_num).values('update_key')
                for key in bkserver:
                    delete_host = EtcdConfig(key['update_key'], '')
                    delete_host.delete_value()
                BackendServer.objects.get(id=id_num).delete()   
        return HttpResponseRedirect(reverse('backend_server_list'))
    except:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())        

@login_required(login_url='/login')
@permission_required('opsconfig.has_read_backendserver',login_url='/forbidden/')
def backend_server_list(request):
    """
    查看Nginx负载均衡后端服务器
    """
    path1, path2, path3 = u'配置管理中心', u'Nginx负载均衡', u'后端服务器'
    slb_id = request.GET.get('id', '')
    slb_list = ServerLoadBalancer.objects.get(id=slb_id)
    try:
        bks = slb_list.slb.all().order_by('id')
    except Exception as error:
        logg = logging.getLogger('opsadmin')
        logg.error('%s' % traceback.format_exc())
    return render(request,'slb/backend_server_list.html',locals())
