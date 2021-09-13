#!/usr/local/bin/python3.8
# -*- coding=utf8 -*-
"""
# @Author : Eason Lee
# @Created Time : 2020/9/25 17:05
# @Description : 
"""
import re
from netmiko import ConnectHandler

PATTERN_MAC = re.compile(r"^(?:[0-9A-F]{4}[-]){2}(?:[0-9A-F]{4})$", re.I)  # aaaa-bbbb-cccc匹配
PATTERN_IP = re.compile(r"^(?:192|172)\.(?:16|18|168)\.(?:22|23|30|40|52|112|114|138|141|212|214)\."
                        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", re.I)# 内网IP匹配
PATTERN_IP_MAC = re.compile(r"(?:[0-9A-F]{4}[-]){2}(?:[0-9A-F]{4})|(?:192|172)\.(?:16|18|168)\."
                            r"(?:22|23|30|40|52|112|114|138|141|212|214)\."
                            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", re.I)


class HexinCaozuo(object):
    def __init__(self, adm, adm_pwd, ip='192.168.111.1', port=22):
        self.adm = adm
        self.adm_pwd = adm_pwd
        self.ip = ip
        self.port = port
        self.net_connect = self.connect()

    def connect(self, device_type="huawei"):
        login_info = {
            # 如果需要一次显示多行如 dis curr ，需要切换为 hp_comware 才可以
            # 'device_type': 'hp_comware'
            'device_type': device_type,
            'username': self.adm,
            'password': self.adm_pwd,
            'ip': self.ip,
            'port': self.port
        }
        net_connect = ConnectHandler(**login_info)
        # sshConfirm = net_connect.find_prompt()
        # print('login' + sshConfirm)
        return net_connect

    # 绑定IP-MAC地址
    def bind(self, vlan, mac, ip):
        rlt = []
        # 先检查该 MAC 是否已有绑定记录
        command = "dis current-configuration | include static-bind.*{}".format(mac)
        oupt = self.net_connect.send_command(command)
        results = PATTERN_IP_MAC.findall(oupt)
        if len(results) == 0:
            rlt.append(f"{mac} 未有绑定记录")
        else:
            rlt.append(f"{mac} 原有绑定信息如下：\n{oupt}")
        # 再检查该 IP 是否已有绑定记录，如果有则直接退出
        # static-bind ip-address 172.16.22.39 mask 255.255.254.0 hardware-address dca4-ca17-5447
        # static-bind ip-address 172.16.22.120 mask 255.255.254.0 hardware-address 1063-c8af-19d7
        # "static-bind.*{} mask" 用于在交换机中严格匹配对应的 IP 记录
        command = 'dis current-configuration | include "static-bind.*{} mask"'.format(ip)
        oupt = self.net_connect.send_command(command)
        results = PATTERN_IP_MAC.findall(oupt)
        if len(results) != 0:
            rlt.append(f"{ip} 已有绑定记录，请考虑绑定其他 IP：\n{oupt}")
        else:
            # 需要注意无线网段1016、1018的掩码是23
            mask = 23 if vlan in ['1016', '1018'] else 24
            commands = [
                f'dhcp server ip-pool {vlan}',
                f'static-bind ip-address {ip} {mask} hardware-address {mac}',
                f'forbidden-ip {ip}',
                'save force'
            ]
            oupt = self.net_connect.send_config_set(commands)
            rlt.append(oupt + "\n绑定完成")
        self.net_connect.disconnect()

        return rlt


    # 解除绑定IP-MAC
    def no_bind(self, vlan, ip):
        rlt = []
        # 先根据ip查看是否有绑定记录
        command = "dis current-configuration | include static-bind.*{}".format(ip)
        oupt = self.net_connect.send_command(command)
        results = PATTERN_IP_MAC.findall(oupt)
        # 如果有绑定记录则进入解绑
        if len(results) != 0:
            rlt.append(f"{ip} 原有绑定信息如下:\n{oupt}")
            commands = [
                f'dhcp server ip-pool {vlan}',
                f'no static-bind ip-address {ip}',
                f'no forbidden-ip {ip}',
                'save force'
            ]
            oupt = self.net_connect.send_config_set(commands)
            rlt.append(oupt + "\n解绑完成")
        else:
            rlt.append(f"{ip} 无绑定记录")

        self.net_connect.disconnect()
        return rlt

    # 导出IP-MAC绑定记录
    # 如果需要一次显示多行如 dis curr ，切换为 hp_comware 才可以
    # 'device_type': 'hp_comware'
    def daochu_ipmac(self):
        command = 'dis current-configuration | include static-bind'
        net_connect = self.connect("hp_comware")
        outp = net_connect.send_command(command)
        results = PATTERN_IP_MAC.findall(outp)
        print("MAC 记录如下：")
        for i in range(0 ,len(results), 2):
            print(results[i] , results[i+1])
        net_connect.disconnect()

    # 根据 IP 或 MAC 查找定位设备位置
    def cha_weizhi(self, item):
        # 如果是 MAC 格式直接查聚合端口
        if "-" in item:
            command = f'dis arp | include {item}'
        # 如果是 IP 格式先转换为 MAC 再查聚合端口
        if "." in item:
            #192.168.17.17   dcfb-48ba-a009 1016       GE1/0/11                 8     D
            #192.168.17.179  e089-7ea8-de0c 1016       BAGG3                    20    D
            # include "{ip}{space}\w+ 用于在交换机中严格匹配记录
            last_len = len(item.split('.')[-1])
            spaces = ['', '    ', '   ', '  ']
            space = spaces[last_len]
            command = f'dis arp | include "{item}{space}\w+"'

        outp = self.net_connect.send_command(command)
        self.net_connect.disconnect()
        if len(outp) != 0:
            pattern = re.compile(r'(?:[0-9A-F]{4}[-]){2}(?:[0-9A-F]{4})(?:-\w{2})?'
                                     r'|(?:\d{1,3}\.){3}\d{1,3}|BAGG\d{1,2}|GE\d{1}/0/\d{1,2}', re.I)
            results = pattern.findall(outp)
            rlt = (f"在核心上 {item} 的IP是 {results[0]}, MAC是 {results[1]}, 所在端口是 {results[2]}")
            return results[1], results[2], rlt
        else:
            rlt = (f"在核心上{item}没有记录")
            return None, None, rlt

    # 添加翻墙 IP 记录
    def jia_fanq(self):
        while True:
            ip = input('需要翻墙的内网 DHCP IP:')
            if PATTERN_IP.match(ip):
                break
            else:
                print("输入参数错误")
        # 先检查该 IP 是否绑定了 MAC
        # "static-bind.*{} mask" 用于在交换机中严格匹配对应的 IP 记录
        command = 'dis current-configuration | include "static-bind.*{} mask"'.format(ip)
        net_connect = self.connect('hp_comware')
        outp = net_connect.send_command(command)
        if len(outp) == 0:
            print("该 IP 未绑定 MAC, 请先绑定 IP-MAC")
        else:
            # 需要确定绑定记录才进行下一步操作
            print(outp)
            confirm = input("该 IP 绑定记录如上，请核实(y/n):")
            if confirm == 'y':
                commands = [
                    'acl number 2020',
                    'dis this'
                ]
                outp = net_connect.send_config_set(commands)
                # 只获取 rule 编号
                # 并以步长为5进行添加 ACL 记录
                results = re.findall(r" [0-9] | [1-9][0-9]+ ", outp)
                rule_number = int(results.pop()) + 5
                commands = [
                    'acl number 2020',
                    f'rule {rule_number} permit source {ip} 0',
                ]
                outp = net_connect.send_config_set(commands)
                print("该 IP 已添加翻墙记录") if 'exists' in outp else print("添加完成")
            else:
                pass
        net_connect.disconnect()

    # 删除翻墙 IP 记录
    def shan_fanq(self):
        while True:
            ip = input("需要删除翻墙的内网DHCP IP: ")
            if PATTERN_IP.match(ip):
                break
            else:
                print("输入参数错误")

        commands = [
            'acl number 2020',
            f'dis this | include "{ip} 0"'
        ]
        outp = self.net_connect.send_config_set(commands)
        results = re.findall(r" [0-9] | [1-9][0-9]+ ", outp)
        if len(results) == 1:
            rule_number = results[0]
            commands = [
                'acl number 2020',
                f'no rule {rule_number}'
            ]
            outp = self.net_connect.send_config_set(commands)
            print(outp, "\n已删除该翻墙记录")
        elif len(results) == 0:
            print("该 IP 无绑定记录")
        else:
            print("记录出错，请登录交换机处理")

        # self.net_connect.disconnect()

    # 导出翻墙记录
    def daochu_fanq(self):
        command = 'dis acl 2020'
        net_connect = self.connect('hp_comware')
        outp = net_connect.send_command(command)
        print("翻墙记录如下:\n", outp)
        net_connect.disconnect()
     
