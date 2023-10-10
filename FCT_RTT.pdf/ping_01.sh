#!/bin/bash
rm ping_result.dat &>/dev/null

while true; do
  ping -c 1 20.0.0.1 | tail -1 | awk -F' ' '{print $4}' | cut -d'/' -f2 >> ping_result.dat
  sleep 0.01
done
