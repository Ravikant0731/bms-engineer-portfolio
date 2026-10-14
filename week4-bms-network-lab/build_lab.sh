#!/bin/bash
set -e
NS="sw rtr bms ahu chl itpc mgmt"
for ns in $NS; do ip netns del $ns 2>/dev/null || true; done
for ns in $NS; do ip netns add $ns; ip -n $ns link set lo up; done

# Switch: VLAN-aware bridge in its own namespace
ip -n sw link add br0 type bridge vlan_filtering 1
ip -n sw link set br0 up

attach_host() {
  local ns=$1 vid=$2 host=$3
  ip link add p-$ns type veth peer name eth0 netns $ns
  ip link set p-$ns netns sw
  ip -n sw link set p-$ns master br0
  ip -n sw link set p-$ns up
  ip netns exec sw bridge vlan del dev p-$ns vid 1
  ip netns exec sw bridge vlan add dev p-$ns vid $vid pvid untagged
  ip -n $ns addr add 10.10.$vid.$host/24 dev eth0
  ip -n $ns link set eth0 up
  ip -n $ns route add default via 10.10.$vid.1
}

attach_host bms  10 10
attach_host ahu  20 11
attach_host chl  20 12
attach_host itpc 30 10
attach_host mgmt 99 10

# Trunk to router (router-on-a-stick)
ip link add p-rtr type veth peer name trunk netns rtr
ip link set p-rtr netns sw
ip -n sw link set p-rtr master br0
ip -n sw link set p-rtr up
ip netns exec sw bridge vlan del dev p-rtr vid 1
ip -n rtr link set trunk up
for vid in 10 20 30 99; do
  ip netns exec sw bridge vlan add dev p-rtr vid $vid
  ip -n rtr link add link trunk name trunk.$vid type vlan id $vid
  ip -n rtr addr add 10.10.$vid.1/24 dev trunk.$vid
  ip -n rtr link set trunk.$vid up
done
ip netns exec rtr sysctl -qw net.ipv4.ip_forward=1
echo "Lab built."
