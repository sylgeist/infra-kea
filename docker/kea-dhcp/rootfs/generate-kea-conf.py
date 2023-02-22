#!/usr/bin/env python3

import os
import json

db = os.environ.get("KEA_DB", "not-a-db")
db_host = os.environ.get("KEA_DB_HOST", "not-a-host")
db_user = os.environ.get("KEA_DB_USER", "not-a-user")
db_pass = os.environ.get("KEA_DB_USER_PASSWORD", "not-a-password")
region = os.environ.get("REGION", "not-a-region")
shipyard_url = "shipyard-api:443"

def configuration():
    return {
        "Dhcp4": {
            "server-tag": region,
            "config-control": {
                "config-databases": [{
                    "type": "postgresql",
                    "name": db,
                    "user": db_user,
                    "password": db_pass,
                    "host": db_host,
                    "port": 5432,
                    "connect-timeout" : 20,
                    "max-reconnect-tries": 30,
                    "reconnect-wait-time" : 500,
                    "on-fail" : "serve-retry-continue"
                }],
                "config-fetch-wait-time": 3600
            },
            "hooks-libraries": [
                  {
                    "library": "/lib/kea/hooks/libdhcp_pgsql_cb.so"
                  },
                  {
                    "library": "/lib/kea/hooks/libdhcp_cb_cmds.so"
                  },
                  {
                    "library": "/lib/kea/hooks/libdhcp_host_cmds.so"
                  },
                  {
                      "library": "/lib/kea/hooks/libdhcp_stat_cmds.so"
                  },
                  {
                      "library": "/lib/kea/hooks/libdhcp_subnet_cmds.so"
                  },
                  {
                      "library": "/lib/kea/hooks/libdhcp_lease_cmds.so"
                  },
                  {
                      "library": "/lib/kea/hooks/do-kea-runscript.so",
                      "parameters": {
                        "enabled": True,
                        "script": "/usr/sbin/shipyard_bmc_update",
                        "script_debug": False,
                        "shipyard": shipyard_url,
                        "region": region,
                      }
                  }
                ],
            "control-socket": {
                    "socket-type": "unix",
                    "socket-name": "/tmp/kea-dhcp4.sock"
            },
            "multi-threading": {
              "enable-multi-threading": True,
              "thread-pool-size": 8,
              "packet-queue-size": 88,
            },
            "interfaces-config": {"interfaces": ["bond0"]},
            "dhcp-ddns": {
                "enable-updates": True,
                "server-ip": "127.0.0.1",
                "server-port":53001,
                "sender-ip":"",
                "sender-port":0,
                "max-queue-size":1024,
                "ncr-protocol":"UDP",
                "ncr-format":"JSON"
            },
            "lease-database": {
              "type": "postgresql",
              "name": db,
              "user": db_user,
              "password": db_pass,
              "host": db_host,
              "port": 5432,
              "connect-timeout" : 20,
              "max-reconnect-tries": 30,
              "reconnect-wait-time" : 500,
              "on-fail" : "serve-retry-continue"
            },
            "hosts-database": {
              "type": "postgresql",
              "name": db,
              "user": db_user,
              "password": db_pass,
              "host": db_host,
              "port": 5432,
              "connect-timeout" : 20,
              "max-reconnect-tries": 30,
              "reconnect-wait-time" : 500,
              "on-fail" : "serve-retry-continue"
            },
            "host-reservation-identifiers": [ "hw-address" ],
            "loggers": [
                {
                    "name": "kea-dhcp4",
                    "output_options": [
                        {
                            "output": "/var/log/kea-dhcp4.log",
                            "maxver": 3,
                            "maxsize": 204800,
                            "flush": True,
                        }
                    ],
                    "severity": "INFO",
                },
            ],
        },
    }


print(json.dumps(configuration(), indent=2, sort_keys=True))
