#!/usr/bin/env python3

import os
import json

db = os.environ.get("KEA_DB", "not-a-db")
db_host = os.environ.get("KEA_DB_HOST", "not-a-host")
db_user = os.environ.get("KEA_DB_USER", "not-a-user")
db_pass = os.environ.get("KEA_DB_USER_PASSWORD", "not-a-password")


def configuration():
    return {
        "Dhcp4": {
            "server-tag": "kea-updater",
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
            "interfaces-config": {"interfaces": ["lo"]},
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
