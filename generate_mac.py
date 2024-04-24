#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import random


def generate_random_mac():
    """
    生成随机MAC地址
    """
    return '-'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)])


if __name__ == '__main__':
    random_mac_list = []  # 准备一个存放随机MAC地址的列表
    for _ in range(10):  # 准备生成10个
        random_mac = generate_random_mac()  # 生成随机MAC地址
        while random_mac in random_mac_list:  # 如果随机MAC地址已经存在，则重新生成
            random_mac = generate_random_mac()  # 重新生成随机MAC地址
            print(f"重新生成随机MAC地址: {random_mac}")
        random_mac_list.append(random_mac)  # 将随机MAC地址添加到列表中

    print(random_mac_list)
