# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter(name='list_to_str')
def list_to_str(vars_list):
    """"get list to string"""
    var_list = []
    if len(vars_list) < 3:
        for var in vars_list:
            if hasattr(var, 'platform_name'):
                var_list.append(var.platform_name)
            elif hasattr(var, 'username'):
                var_list.append(var.username)
            elif hasattr(var, 'name'):
                var_list.append(var.name)
            elif hasattr(var, 'private_ip'):
                var_list.append(var.private_ip)
            else:
                var_list.append(var.group)
        return '|'.join(var_list)
    else:
        for var in vars_list[0:3]:
            if hasattr(var, 'platform_name'):
                var_list.append(var.platform_name)
            elif hasattr(var, 'username'):
                var_list.append(var.username)
            elif hasattr(var, 'name'):
                var_list.append(var.name)
            elif hasattr(var, 'private_ip'):
                var_list.append(var.private_ip)
            else:
                var_list.append(var.group) 
        return '%s ...' % '|'.join(var_list)


@register.filter(name='int_to_str')
def int_to_str(value):
    """"int to string"""
    return str(value)

@register.filter(name='ip_to_str')
def ip_to_str(vars_list):
    """"get list to string"""
    var_list = []
    if len(vars_list) < 4:
        for var in vars_list:
            if hasattr(var, 'private_ip'):
                var_list.append(var.private_ip)
        return '|'.join(var_list)
    else:
        for var in vars_list[0:3]:
            if hasattr(var, 'private_ip'):
                var_list.append(var.private_ip) 
        return '%s ...' % '|'.join(var_list)

@register.filter(name='set_to_list')
def set_to_list(vars_list):
    var_list = []
    for var in vars_list:
        if hasattr(var, 'private_ip'):
            var_list.append(var.private_ip.encode('utf-8'))
        else:
            var_list.append(var.group.encode('utf-8')) 
    return var_list

