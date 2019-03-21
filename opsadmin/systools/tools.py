# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from cmdb.models import AppInfo
from django.http.response import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from opsadmin.settings import MEDIA_ROOT
import json
import os


@login_required(login_url='/login')
def systools_upload_files(request):
    """上传文件"""
    path1, path2 = u'系统管理工具', u'本地文件上传'
    app_info = AppInfo.objects.filter(
            Q(frameworks__contains="play") |
            Q(frameworks__contains="tomcat")).exclude(app_type__contains='private_cloud').values('app_name').distinct()
    if request.method == 'POST' and request.FILES:
        upload_path = request.POST.get('path', '')
        uploadfiles = request.FILES.getlist('file_data', None)
        try:
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            #else:
            #    shutil.rmtree(upload_path)
            #    os.makedirs(upload_path)          
            for uploadfile in uploadfiles:
                file_save = "%s/%s" % (upload_path, uploadfile.name)
                if os.path.exists(file_save):
                    os.remove(file_save) 
                with open(file_save, 'wb+') as f:
                    for chunk in uploadfile.chunks():
                        f.write(chunk)
            return JsonResponse({'mgs': 'sucess'})
        except Exception as error:
            return JsonResponse({"msg": error})

    return render(request,'tools/local_file_upload.html', {'app_info': app_info, 'file_root': MEDIA_ROOT})
