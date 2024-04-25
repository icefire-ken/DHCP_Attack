#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from scapy.all import *


def construct_dhcp_discovery():
    discovery = Ether(dst='ff:ff:ff:ff:ff:ff') / \
            IP(src='0.0.0.0', dst='255.255.255.255') / \
            UDP(sport=68, dport=67) / \
            BOOTP(op=1, chaddr='ff:ff:ff:ff:ff:ff') / \
            DHCP(options=[('message-type', 'discover'), 'end'])

    return discovery


if __name__ == '__main__':
    dhcp_discovery = construct_dhcp_discovery()
    dhcp_discovery.show()
