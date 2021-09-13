#!/usr/local/bin/python3.8
# -*- coding=utf8 -*-
"""
# @Author : Eason Lee
# @Created Time : 2020/9/27 16:06
# @Description : 
"""
from netmiko import ConnectHandler
import re


class JiaohuanjiCaozuo(object):
    def __init__(self, swip, adm, adm_pwd):
        self.swip = swip
        self.adm = adm
        self.adm_pwd = adm_pwd
        self.net_connect = self.connect()

    def connect(self, device_type="huawei", port=22):
        login_info = {
            # 如果需要一次显示多行如 dis curr ，切换为 hp_comware 才可以
            # 'device_type': 'hp_comware'
            'device_type': device_type,
            'ip': self.swip,
            'username': self.adm,
            'password': self.adm_pwd,
            'port': port
        }
        net_connect = ConnectHandler(**login_info)
        # sshConfirm = net_connect.find_prompt()
        # print('login' + sshConfirm)
        return net_connect

    def locate(self, mac):
        command = f'dis mac-address | include {mac}'
        oupt = self.net_connect.send_command(command)
        pattern = re.compile(r'BAGG\d{1,2}|GE\d{1}/0/\d{1,2}', re.I)
        inter = pattern.search(oupt).group()
        #command = f'dis interface {inter} brief'
        #oupt = self.net_connect.send_command(command)
        self.net_connect.disconnect()
        return inter

    def change_vlan(self, port, vlan):
        vlans = ['1011', '1016', '1024', '1028']
        if re.match(r'^[1-9]$|^[1-3][0-9]$|^[4][0-6]$', port) and vlan in vlans:
            commands = [
                f'interface GigabitEthernet 1/0/{port}',
                f'port access vlan {vlan}',
                'save force'
            ]
            outp = self.net_connect.send_config_set(commands)
            return (outp +"\n操作成功")
        else:
            return (f"参数错误，端口(1-46)\nvlan端口:{vlans}")
        self.net_connect.disconnect()


    def operate(self, commands):
        self.net_connect.disconnect()
        new_session = self.connect("hp_comware", 22)
        outp = new_session.send_config_set(commands)
        new_session.disconnect()

        return (outp +"\n操作成功")
        # for host in self.switches.keys():
        #     net_connect = self.connect(host)
        #     # huawei = self.login_info(host)
        #     # net_connect = ConnectHandler(**huawei)
        #     # sshConfirm = net_connect.find_prompt()
        #     # print('login ' + sshConfirm)
        #     # commands = [
        #     #     'ftp server enable',
        #     #     'local-user ftp class manage',
        #     #     'password simple Ejh18FRNUoY8OK8h',
        #     #     'service-type ftp',
        #     #     'authorization-attribute user-role network-admin',
        #     #     'save force'
        #     # ]
        #     output = net_connect.send_config_set(commands)
        #     net_connect.disconnect()
        #     print(output)


