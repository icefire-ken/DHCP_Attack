#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import psutil


def get_nic_info():
    """
    获取网卡信息
    """
    nic_list = []
    for nic, info in psutil.net_if_addrs().items():
        temp_dict = {'网卡': nic, 'MAC': 'None', 'IP': 'None', 'Mask': 'None'}
        for addr in info:
            if addr.family == 2:
                temp_dict['IP'] = addr.address
                temp_dict['Mask'] = addr.netmask
            elif addr.family == -1:
                temp_dict['MAC'] = addr.address
        nic_list.append(temp_dict)

    for i in range(len(nic_list)):
        print(f'\n网卡[{i}]：{nic_list[i]["网卡"]}')
        print(f'\t\tMAC：{nic_list[i]["MAC"]}', end='\t')
        print(f'IP：{nic_list[i]["IP"]}', end='\t')
        print(f'Mask：{nic_list[i]["Mask"]}')


def get_ip_range(subnet_ip, mask):
    """
    计算IP地址范围
    """
    # 将IP地址和掩码转换为二进制字符串
    subnet_ip_bin = "".join([bin(int(x) + 256)[3:] for x in subnet_ip.split(".")])
    mask_bin = "".join([bin(int(x))[2:].zfill(8) for x in mask.split(".")])

    # 计算主机位上的0的个数
    host_bits = mask_bin.count("0")

    # 计算主机数
    host_count = 2 ** host_bits - 2

    # 计算起始和结束IP地址
    ip_start = int(subnet_ip_bin, 2) + 1
    ip_end = ip_start + host_count - 1

    # 将起始和结束IP地址转换为十进制，返回
    return ".".join([str(int(x, )) for x in bin(ip_start)[2:].zfill(32)]), \
        ".".join([str(int(x, 2)) for x in bin(ip_end)[2:].zfill(32)])


if __name__ == '__main__':
    # get_nic_info()
    a = get_ip_range('192.168.1.1', '255.255.255.0')
    print(a)
