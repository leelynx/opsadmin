from django import forms
from opsconfig.models import ServerLoadBalancer, BackendServer


class ServerLoadBalancerForm(forms.ModelForm):

    class Meta:
        model = ServerLoadBalancer

        fields = [
            "slb_name","slb_area", "slb_host", "slb_port", "comment"
        ]


class BackendServerForm(forms.ModelForm):
    class Meta:
        model = BackendServer
        fields = [
            "server_name", "server_area", "slb_name", "server_ip", "server_port", "weight", "max_fails", "fail_timeout", "update_key", "comment"
            ]      