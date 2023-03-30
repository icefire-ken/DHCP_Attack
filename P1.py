#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import psutil

if __name__ == '__main__':
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
