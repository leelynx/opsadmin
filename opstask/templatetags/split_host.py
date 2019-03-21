# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter(name='str_to_list')
def str_to_list(string):
    """"string to list"""
    var_list = string.encode('utf-8').split(',')
    return var_list

@register.filter(name='ip_to_list')
def ip_to_list(vars):
    if vars:
        return vars.encode('utf-8').split(',')
    else:
        return "not host"
