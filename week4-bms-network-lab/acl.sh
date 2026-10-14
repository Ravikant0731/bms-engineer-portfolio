#!/bin/bash
set -e
R="ip netns exec rtr"
$R iptables -F FORWARD
$R iptables -P FORWARD DROP
$R iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
# BMS server -> controllers
$R iptables -A FORWARD -s 10.10.10.10 -d 10.10.20.0/24 -p udp --dport 47808 -j ACCEPT
$R iptables -A FORWARD -s 10.10.10.10 -d 10.10.20.0/24 -p tcp --dport 502 -j ACCEPT
$R iptables -A FORWARD -s 10.10.10.10 -d 10.10.20.0/24 -p icmp -j ACCEPT
# Controllers -> BMS server (alarms/COV)
$R iptables -A FORWARD -s 10.10.20.0/24 -d 10.10.10.10 -p udp --dport 47808 -j ACCEPT
# IT users -> dashboard only
$R iptables -A FORWARD -s 10.10.30.0/24 -d 10.10.10.10 -p tcp --dport 443 -j ACCEPT
# Management VLAN
$R iptables -A FORWARD -s 10.10.99.0/24 -d 10.10.10.0/24 -p tcp --dport 22 -j ACCEPT
$R iptables -A FORWARD -s 10.10.99.0/24 -d 10.10.20.0/24 -p tcp --dport 22 -j ACCEPT
$R iptables -A FORWARD -s 10.10.99.0/24 -p icmp -j ACCEPT
# Explicit final drop (so the counter shows blocked packets)
$R iptables -A FORWARD -j DROP
echo "ACL applied."
