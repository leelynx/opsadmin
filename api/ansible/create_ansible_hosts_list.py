#!/usr/bin/env  python
# -*- coding: utf-8 -*-


import ConfigParser
from ConfigParser import DEFAULTSECT
import base64

class KconfigParser(ConfigParser.RawConfigParser):
    def write(self, fp):
        """解决ConfigParser的冒号被自动保存为等号而引起的后续解析问题"""
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            for (key, value) in self._defaults.items():
                fp.write("%s %s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")
        for section in self._sections:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write("%s %s\n" %
                         (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")

class Generate_ansible_hosts(object):
    def __init__(self, host_file):
        self.config = KconfigParser(allow_no_value=True)
        self.host_file = host_file

    def create_all_servers(self, host_dic):
        for i in host_dic:
            group = i['group']
            self.config.add_section(group)
            for j in i['items']:
                name = j['hostname']
                ssh_port = j['host_port']
                ssh_host = j['private_ip']
                ssh_user = j['username']
                ssh_pass = base64.b64decode(j['password'])
                build = "ansible_ssh_port={0} ansible_ssh_host={1} ansible_ssh_user={2} ansible_ssh_pass='{3}'".format(
                        ssh_port, ssh_host, ssh_user, ssh_pass)
                self.config.set(group, name, build)
        with open(self.host_file, 'wb') as configfile:
            self.config.write(configfile)
        return True


"""例子"""
if __name__ == '__main__':
    generate_hosts = Generate_ansible_hosts('/tmp/hosts')
    data = [
        {
        "group": "test-group1",
        "items": [
            {
            "name": "test1",
            "ssh_host": "127.0.0.1",
            "ssh_port": 22,
            "ssh_user": "deploy"
            },
            {
            "name": "test2",
            "ssh_host": "127.0.0.1",
            "ssh_port": 22,
            "ssh_user": "deploy"
            }
        ]
        },
        {
        "group": "test-group2",
        "items": [
            {
            "name": "test3",
            "ssh_host": "127.0.0.1",
            "ssh_port": 22,
            "ssh_user": "deploy"
            }
        ]
        }
    ]
    generate_hosts.create_all_servers(data)
