#!/bin/sh

rm /tmp/output.txt
out=""
good=""
ip=""
for ip in "10.0.0.1" "192.168.60.125" "10.0.4.2" "127.0.0.1"; do
  if ping -c 1 -W 1 "$ip" >/dev/null 2>&1; then
    echo "$ip is reachable"
    out="$out GOOD-$ip"
  else
    echo "$ip is unreachable"
    out="$out ERR-$ip"
    good="N"
  fi
done
if [ -z "$good" ]; then
  touch /tmp/output.txt
else
  echo $out > /tmp/output.txt
fi

