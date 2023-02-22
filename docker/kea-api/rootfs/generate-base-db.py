#!/usr/bin/env python3

import os
import json
import requests
import datetime
import generator_configs

kea_region = os.environ.get("REGION", "not-a-region")
kea_api = "http://127.0.0.1:8000"

global_options = []
tag_stats = {'added': 0, 'failed': 0}
option_stats = {'added': 0, 'failed': 0}
param_stats = {'added': 0, 'failed': 0}
class_stats = {'added': 0, 'failed': 0}


if 's2r' in kea_region:
    regions = generator_configs.staging_regions
else:
    regions = generator_configs.prod_regions

server_tags = [
  {
    "service": ["dhcp4"],
    "command": "remote-server4-set",
    "arguments": {
      "servers": [
        {
            "server-tag": "kea_test",
            "description": "Test Tag - Do not assign!"
        }
      ]
    }
  }
]


global_params = [
  {
    "service": ["dhcp4"],
    "command": "remote-global-parameter4-set",
    "arguments": {
      "parameters": {
          "valid-lifetime": 4000,
          "cache-threshold": 0.25,
          "match-client-id": False,
          "ddns-send-updates": True,
          "ddns-generated-prefix": "dhcp",
          "ddns-override-client-update": True,
          "ddns-override-no-update": True,
          "ddns-update-on-renew": True,
          "ddns-use-conflict-resolution": True,
          "ddns-replace-client-name": "when-not-present",
          "hostname-char-replacement": ""
      },
      "server-tags": [ "all" ]
    }
  }
]


client_classes = [
  {
    "service": ["dhcp4"],
    "command": "remote-class4-set",
    "arguments": {
      "client-classes": [
        {
          "boot-file-name": "ipxe.pxe",
          "name": "ipxe_legacy",
          "test": "option[93].hex == 0x0000"
        }
      ],
      "server-tags": [ "all" ]
    }
  },
  {
    "service": ["dhcp4"],
    "command": "remote-class4-set",
    "arguments": {
      "client-classes": [
        {
          "boot-file-name": "snponly-x86_64.efi",
          "name": "ipxe_efi_bc",
          "test": "option[93].hex == 0x0007"
        }
      ],
      "server-tags": [ "all" ]
    }
  },
  {
    "service": ["dhcp4"],
    "command": "remote-class4-set",
    "arguments": {
      "client-classes": [
        {
          "boot-file-name": "snponly-x86_64.efi",
          "name": "ipxe_efi_x64",
          "test": "option[93].hex == 0x0009"
        }
      ],
      "server-tags": [ "all" ]
    }
  },
  {
    "service": ["dhcp4"],
    "command": "remote-class4-set",
    "arguments": {
      "client-classes": [
        {
          "boot-file-name": "snponly-arm64.efi",
          "name": "ipxe_efi_arm64",
          "test": "option[93].hex == 0x000b"
        }
      ],
      "server-tags": [ "all" ]
    }
  }
]


def gen_tag(region):
  return {
    "service": ["dhcp4"],
    "command": "remote-server4-set",
    "arguments": {
      "servers": [
        {
            "server-tag": region,
            "description": "Staging Kea Instance"
        }
      ]
    }
  }


def gen_global(region):
  return {
    "service": ["dhcp4"],
    "command": "remote-global-parameter4-set",
    "arguments": {
      "parameters": {
        "ddns-qualifying-suffix": f"{region}",
        "next-server": generator_configs.next_servers[region]
      },
      "server-tags": [ region ]
    }
  }


def gen_classes(region):
  return {
    "service": ["dhcp4"],
    "command": "remote-class4-set",
    "arguments": {
      "client-classes": [
        {
          "boot-file-name": f"http://netboot.{region}/snponly.efi",
          "name": f"uefi_http_{region}",
          "test": "option[93].hex == 0x0010",
          "option-data": [
            {
              "code": 60,
              "name": "vendor-class-identifier",
              "data": "HTTPClient"
            }
          ]
        }
      ],
      "server-tags": [ region ]
    }
  }


def gen_options(region):
  return [
    {
      "service": ["dhcp4"],
      "command": "remote-option4-global-set",
      "arguments": {
        "options": [
          {
            "code": 6,
            "data": ",".join(generator_configs.name_server[region]),
            "name": "domain-name-servers"
          }
        ],
        "server-tags": [ region ]
      }
    },
    {
      "service": ["dhcp4"],
      "command": "remote-option4-global-set",
      "arguments": {
        "options": [
          {
            "code": 15,
            "data": f"{region}",
            "name": "domain-name"
          }
        ],
        "server-tags": [ region ]
      }
    },
    {
      "service": ["dhcp4"],
      "command": "remote-option4-global-set",
      "arguments": {
        "options": [
          {
            "code": 119,
            "data": f"{region},internal.domain",
            "name": "domain-search"
          }
        ],
        "server-tags": [ region ]
      }
    }
  ]

for region in regions:
  server_tags += [ gen_tag(region) ]
  global_params += [ gen_global(region) ]
  client_classes += [ gen_classes(region) ]
  global_options += gen_options(region)


for server in server_tags:
  response = requests.post(kea_api, json=server, timeout=10)
  response.raise_for_status()
  if response.json()[0]['result'] == 0:
    tag_stats['added'] += 1
  else:
    tag_stats['failed'] += 1

for param in global_params:
  response = requests.post(kea_api, json=param, timeout=10)
  response.raise_for_status()
  if response.json()[0]['result'] == 0:
    param_stats['added'] += 1
  else:
    param_stats['failed'] += 1

for class_item in client_classes:
  response = requests.post(kea_api, json=class_item, timeout=10)
  response.raise_for_status()
  if response.json()[0]['result'] == 0:
    class_stats['added'] += 1
  else:
    class_stats['failed'] += 1

for option in global_options:
  response = requests.post(kea_api, json=option, timeout=10)
  response.raise_for_status()
  if response.json()[0]['result'] == 0:
    option_stats['added'] += 1
  else:
    option_stats['failed'] += 1

ct = datetime.datetime.now()
print(ct, ' Tag Stats:    ', tag_stats)
print(ct, ' Params Stats: ', param_stats)
print(ct, ' Class Stats:  ', class_stats)
print(ct, ' Option Stats: ', option_stats)
