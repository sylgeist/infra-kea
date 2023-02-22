#!/usr/bin/env python3

import json, os, random, re, shlex, subprocess, sys
from dns import resolver

ddns_secret = os.environ.get("DDNS_TSIG_KEY", "notatsig")
domain_name = os.environ.get("DOMAIN_SUFFIX", "domain.notdefined")
region = os.environ.get("REGION", "not-a-region")

if "s2r" in region:
  ddns_host = "dynamicdns01"
  try:
    res = resolver.query(ddns_host + "." + domain_name, 'A')
    ddns_server_ip = str(res[0])
  except:
    ddns_server_ip = "127.0.0.1"
else:
  ddns_host = "prod-dynamicdns01"
  try:
    res = resolver.query(ddns_host + "." + domain_name, 'CNAME')
    ddns_server_ext_hostname = str(res[0])
    ddns_server_int_hostname = re.sub('-ext\.', '-int.', ddns_server_ext_hostname)
    res = resolver.query(ddns_server_int_hostname, 'A')
    ddns_server_ip = str(res[0])
  except:
    ddns_server_ip = "127.0.0.1"


def configuration():
    return {
            "DhcpDdns": {
                    "dns-server-timeout": 100,
                    "forward-ddns": {
                        "ddns-domains": [
                            {
                                "dns-servers": [{"ip-address": ddns_server_ip}],
                                "key-name": "ddns_key.",
                                "name": f"{domain_name}.",
                            }
                        ]
                    },
                    "ip-address": "127.0.0.1",
                    "ncr-format": "JSON",
                    "ncr-protocol": "UDP",
                    "port": 53001,
                    "tsig-keys": [
                        {"algorithm": "HMAC-MD5", "name": "ddns_key.", "secret": ddns_secret}
                    ],
            "loggers": [ {
                "name": "kea-dhcp-ddns",
                "output_options": [
                  {
                    "flush": True,
                    "maxsize": 204800,
                    "maxver": 3,
                    "output": "/var/log/kea-dhcp-ddns.log"
                  }
                ],
                "severity": "WARN"
              }
             ]
            },
    }

print(json.dumps(configuration(), indent=2, sort_keys=False))

