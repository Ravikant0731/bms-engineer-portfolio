#!/bin/bash
t() {
  desc=$1; expect=$2; ns=$3; cmd=$4
  if ip netns exec "$ns" bash -c "$cmd" >/dev/null 2>&1; then got=ALLOW; else got=BLOCK; fi
  [ "$got" = "$expect" ] && res=PASS || res=FAIL
  printf "%-46s expect=%-5s got=%-5s %s\n" "$desc" "$expect" "$got" "$res"
}
t "BMS server -> AHU ping"                ALLOW bms  "ping -c1 -W1 10.10.20.11"
t "BMS server -> Chiller Modbus TCP 502"  ALLOW bms  "timeout 2 bash -c '</dev/tcp/10.10.20.12/502'"
t "IT PC -> BMS dashboard TCP 443"        ALLOW itpc "timeout 2 bash -c '</dev/tcp/10.10.10.10/443'"
t "Mgmt PC -> AHU port 22 (simulated)"    ALLOW mgmt "timeout 2 bash -c '</dev/tcp/10.10.20.11/22'"
t "IT PC -> AHU ping"                     BLOCK itpc "ping -c1 -W1 10.10.20.11"
t "IT PC -> Chiller Modbus TCP 502"       BLOCK itpc "timeout 2 bash -c '</dev/tcp/10.10.20.12/502'"
t "IT PC -> BMS server ping"              BLOCK itpc "ping -c1 -W1 10.10.10.10"
t "AHU -> BMS server ping"                BLOCK ahu  "ping -c1 -W1 10.10.10.10"
