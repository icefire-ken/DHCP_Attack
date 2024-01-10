#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import ipaddress

if __name__ == '__main__':
    ip = input("请输入IP地址：")
    mask = input("请输入子网掩码：")
    num = int(input("请输入所需地址数量："))

    subnet = ipaddress.ip_interface(ip + '/' + mask).network

    if num > subnet.num_addresses:
        print("所需地址数量大于子网可用地址数量，请重新输入。")
    else:
        host_list = list(subnet.hosts())
        print(f"IP地址范围：{host_list[0]} ~ {host_list[num - 1]}")

