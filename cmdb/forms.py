from django import forms

from cmdb.models import ServerInfo
from cmdb.models import PlatformType
from cmdb.models import AppInfo


class ServerInfoForm(forms.ModelForm):

    class Meta:
        model = ServerInfo

        fields = [
            "private_ip","hostname", "resource_area", "username", "password", "rsa_key", "host_port", "platform", "ab_group"
        ]


class AppInfoForm(forms.ModelForm):
    class Meta:
        model = AppInfo
        fields = [
            "app_ip", "app_name", "app_type", "frameworks", "main_path", "service_path", "root_path", "run_port", "svn_path", "backup_path", "work_path", "app_alias","app_status"
    ]

class PlatformTypeForm(forms.ModelForm):
    class Meta:
        model = PlatformType
        fields = [
            "platform_name", "short_name", "comment"
        ]