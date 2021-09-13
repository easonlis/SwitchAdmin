#!/usr/local/bin/python3.8
# -*- coding=utf8 -*-
from .JiaohuanjiCaozuo import JiaohuanjiCaozuo
from .HexinCaozuo import HexinCaozuo

# 交换机列表
switches = [
    '192.168.111.1', '192.168.111.2', '192.168.111.3',
    '192.168.111.4', '192.168.111.5', '192.168.111.7',
    '192.168.111.8', '192.168.111.9', '192.168.111.10'
]

# 核心上各聚合端口对应连接的交换机
core_bagges = {
    'BAGG1': '华三VPN', 'BAGG2': '192.168.111.3', 'BAGG3': '192.168.111.2',
    'GE1/0/5': '深信服AC', 'GE1/0/11': '8楼运维钉钉AP', 'GE1/0/12': '8楼大数据钉钉AP',
    'GE1/0/14': '8楼机房旁钉钉AP', 'GE1/0/16': '192.168.111.7', 'GE1/0/18': '8楼后端钉钉AP',
    'GE1/0/19': '8楼华三AP', 'GE1/0/21': '16.6服务器', 'GE1/0/25': '深信服VPN',
    'GE1/0/35': '16.17服务器', 'GE1/0/37': '192.168.111.8', 'GE1/0/39': '192.168.111.10',
    'GE1/0/41': 'Aruba AP', 'GE1/0/47': '16.5服务器', 'GE1/0/48': '16.5服务器'
}

hsw_bagges = {
        'BAGG2': '192.168.111.4', 'BAGG3': '192.168.111.5', 'GE1/0/25': '10楼墨西哥钉钉AP',
        'GE1/0/27': '10楼休闲区钉钉AP', 'GE1/0/28': '10楼前台钉钉AP', 'GE1/0/29': '10楼中东钉钉AP',
        'GE1/0/32': '10楼机房旁钉钉AP', 'GE1/0/48': '192.168.111.9'
        }

sw2_bagges = {
        'GE1/0/2': '8楼前门口钉钉AP', 'GE1/0/3': '8楼休闲区钉钉AP', 'GE1/0/20': '8楼打印机'    
        }

sw4_bagges = { 'GE1/0/3': '10楼前台打印机' }
sw5_bagges = {}
sw9_bagges = { 'GE1/0/3': '10楼研发钉钉AP' }

def get_son_switch(switch_ip, switch_bagges):
    son_switch = JiaohuanjiCaozuo(switch_ip, adm, adm_pwd)
    interface = son_switch.locate(mac)
    if interface in switch_bagges:
        return (f"该设备 {item}, 位于 {switch_bagges.get(interface)}")
    else:
        return (f"该设备 {item}, 位于 {switch_ip}, {interface}")

def locate_item(item, adm, adm_pwd):
    result = []
    core = HexinCaozuo(adm, adm_pwd)
    mac, bagg, core_result = core.cha_weizhi(item)
    result.append(core_result)
    if mac is not None and bagg is not None:
        first_switch_ip = core_bagges.get(bagg)
        if first_switch_ip == '192.168.111.2':
            result.append(get_son_switch(first_switch_ip, sw2_bagges))
        elif first_switch_ip == '192.168.111.3':
            first_switch = JiaohuanjiCaozuo(first_switch_ip, adm, adm_pwd)
            interface = first_switch.locate(mac)
            second_switch_ip = hsw_bagges.get(interface)
            if second_switch_ip == '192.168.111.4':
                result.append(get_son_switch(second_switch_ip, sw4_bagges))
            elif second_switch_ip == '192.168.111.9':
                result.append(get_son_switch(second_switch_ip, sw9_bagges))
            elif second_switch_ip == '192.168.111.5':
                result.append(get_son_switch(second_switch_ip, sw5_bagges))
            elif interface in hsw_bagges:
                result.append((f"该设备 {item}, 位于 {hsw_bagges.get(interface)}"))
            else:
                result.append((f"该设备 {item}, 位于 {first_switch_ip}, {interface}"))
        else:
            result.append((f"该设备 {item}, 位于 {first_switch_ip}"))
    else:
        pass

    return result
