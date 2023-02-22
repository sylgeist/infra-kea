#!/usr/bin/env python3

import json
import os
import sys
import random
import requests
import socket
import datetime
from typing import List
from netaddr import IPAddress, IPNetwork, IPRange, IPSet
import generator_configs

kea_region = os.environ.get("REGION", "not-a-region")
kea_api = "http://127.0.0.1:8000"

subnet_results = []  # type: List[str]
subnets = {}  # type: Dict[str]
reservations = {} # type: Dict
subnetstats = {'added': 0, 'failed': 0}
resstats = {'added': 0, 'failed': 0, 'dupes': 0}

req = requests.Session()
headers = requests.utils.default_headers()
req.headers.update({"User-Agent": "digitalocean/platform/netboot/kea-config (python3)"})


if 's2r' in kea_region:
    regions = generator_configs.staging_regions
else:
    regions = generator_configs.prod_regions


def get_router(network: IPNetwork) -> str:
    if network.prefixlen == 31:
        return str(network.ip)
    else:
        return str(network.ip + 1)


# Returns a list of IPRanges for the DHCP pools for the given subnet
def get_pools(network: IPNetwork, role: str) -> IPRange:
    last_octet = int(str(network.ip).split(".")[-1])
    # Stage2 L2 check
    if network.prefixlen == 20:
        # Pools consist of last octet 200-250 in four /24 subnets
        # with a third octet of 0-3, for 216 total DHCP addresses
        pools = [IPRange(s.ip + 200, s.ip + 250) for s in list(network.subnet(24))[0:4]]
    elif network.prefixlen == 31:
        pools = [IPRange(network.ip + 1, network.ip + 1)]
    elif network.prefixlen == 25:
        if role == "oob-access":
            pools = [IPRange(network.ip + 21, network.ip + 63)]
        else:
            if last_octet == 0:
                pools = [IPRange(network.ip + 60, network.ip + 126)]
            else:  # last_octet = 128
                pools = [IPRange(network.ip + 12, network.ip + 71)]
    elif network.prefixlen == 26:
        if last_octet == 0:
            pools = [IPRange(network.ip + 40, network.ip + 60)]
        elif last_octet == 64:
            pools = [IPRange(network.ip + 36, network.ip + 56)]
        elif last_octet == 128:
            pools = [IPRange(network.ip + 22, network.ip + 32)]
        else:  # last_octet = 192
            pools = [IPRange(network.ip + 38, network.ip + 58)]
    elif network.prefixlen == 16:
        # Pools consist of last octet 4-250 in four /24 subnets
        # with a third octet of 249-252, for 1012 total DHCP addresses
        pools = [
            IPRange(s.ip + 4, s.ip + 250) for s in list(network.subnet(24))[249:253]
        ]
    else:
        return "Invalid subnet mask"

    return pools


def shipyard_graphql(query: str, region: str):
    shipyard_fqdn = "shipyard"
    try:
        response = requests.post(f"https://{shipyard_fqdn}/graphql", json={"query": query}, timeout=15)
        response.raise_for_status()
        return response.json()["data"]["search"]
    except Exception as error:
        print(f"Shipyard GraphQL query failed: {error}")
        sys.exit(1)


# Returns all region reservations as a dict with the IP as key and MAC as value
def region_reservations(region: str):
    reservations = {}
    if region == "nbg1":
        res_region = "nyc1"
    elif region == "nyc3-uat":
        res_region = "pp1"
    elif "s2r" in region:
        res_region = "nyc3"
    else:
        res_region = region

    query = (
        f'{{ search(term:"Site:{res_region}")'
        " { networkInterfaces { name mac } addresses { interfaceName address } } }"
    )

    shipyard_results = shipyard_graphql(query, res_region)

    for machine in shipyard_results:
        mac = machine["networkInterfaces"][0]["mac"]

        for addr in machine["addresses"]:
            if addr["interfaceName"] in ("eth0", "br0", "bond0"):
                address = addr["address"]

        reservations[address] = mac

    return reservations


# Returns a MAC address from Netbox if found, otherwise randomly generated
def netbox_iface_mac(id):
    netbox_uri = "https://netbox/graphql/"
    defined_mac_address = ""
    query = f"query {{interface(id:{id}) {{mac_address}} }}"

    try:
        r = req.get(netbox_uri, verify="/usr/local/share/ca-certificates/CA.pem", json={"query": query}, headers=headers, timeout=15)
        netbox_response = r.json()
        defined_mac_address = netbox_response["data"]["interface"]["mac_address"]
    except Exception as error:
        return None

    return defined_mac_address


def random_mac():
    rand_mac = "02"
    for i in range(5):
        rand_mac = rand_mac + (":%02x" % (random.randint(0, 255)))

    return rand_mac


# Returns dict of reserved IP addresses from Netbox and randomly generated MAC, given a subnet
def netbox_ipaddrs(subnet) -> {}:
    netbox_uri = "https://netbox/graphql/"
    netbox_results = list()
    netbox_ips = {}
    query = f"query {{ip_address_list(parent:\"{subnet}\") {{address assigned_object_id}} }}"
    try:
        r = req.get(netbox_uri, verify="/usr/local/share/ca-certificates/CA.pem", json={"query": query}, headers=headers)
        netbox_response = r.json()
        netbox_results = netbox_response["data"]["ip_address_list"]
    except Exception as error:
        print(f"Netbox GraphQL query failed: {error}")
        sys.exit(1)

    for ip_and_cidr in netbox_results:
        ipaddr = IPNetwork(ip_and_cidr['address']).ip
        cidr = IPNetwork(ip_and_cidr['address']).prefixlen
        if 'assigned_object_id' in ip_and_cidr:
            iface_id = ip_and_cidr['assigned_object_id']
        else:
            iface_id = None
        ip = str(ipaddr)

        # don't create reservations for bgp-controllers
        if str(cidr) != "31":
            # ignore duplicate addresses
            if ip not in netbox_ips:
                defined_mac = netbox_iface_mac(iface_id)
                if defined_mac != None:
                    mac = defined_mac
                else:
                    mac = random_mac()

                netbox_ips[ip] = mac

    return netbox_ips


def netbox_subnets(role, cidr):
    netbox_uri = "https://netbox/graphql/"
    netbox_results = list()
    if "s2r" in region:
        # In netbox the site for all staging regions is nyc3
        if role == "oob-access" and "s2r8" in region:
            query = f"query {{ prefix_list(role:\"{role}\" mask_length:\"{cidr}\" site:\"nyc3\" q:\"stage\") {{id prefix}} }}"

        elif role == "oob-access.pp1" and "s2r8" in region:
            query = f"query {{ prefix_list(role:\"oob-access\" mask_length:\"{cidr}\" site:\"pp1\") {{id prefix}} }}"

        elif role == "oob-access.pp1" and "s2r6" in region:
            query = f"query {{ prefix_list(role:\"oob-access\" mask_length:\"{cidr}\" site:\"pp1\") {{id prefix}} }}"

        elif role == "underlay.pp1" and "s2r6" in region:
            query = f"query {{ prefix_list(role:\"underlay\" mask_length:\"{cidr}\" site:\"pp1\") {{id prefix}} }}"

        elif role == "underlay" and "s2r6" in region:
            query = f"query {{ prefix_list(role:\"underlay\" mask_length:\"{cidr}\" site:\"pp1\") {{id prefix}} }}"

        elif role == "storage":
            query = f"query {{ prefix_list(role:\"staging\" mask_length:\"{cidr}\" site:\"nyc3\" q:\"s2r{region[-1]} object\") {{id prefix}} }}"

        elif role == "staging-L3VPN":
            query = f"query {{ prefix_list(role:\"staging\" mask_length:\"{cidr}\" site:\"nyc3\" q:\"S2R{region[-1]}-MGMT-L3VPN\") {{id prefix}} }}"

        elif cidr == 31:
            query = f"query {{ prefix_list(role:\"{role}\" mask_length:\"{cidr}\" site:\"nyc3\") {{id prefix}} }}"

        elif cidr != 20:
            query = f"query {{ prefix_list(role:\"{role}\" mask_length:\"{cidr}\" site:\"nyc3\" q:\"Region{region[-1]} L3 (mgmt)\") {{id prefix}} }}"

        else:
            query = f"query {{ prefix_list(role:\"{role}\" mask_length:\"{cidr}\" site:\"nyc3\" q:\"stage2 region {region[-1]} mgmt\") {{id prefix}} }}"

    elif "nbg1" in region:
        query = f"query {{ prefix_list(role:\"{role}\" mask_length:\"{cidr}\" site:\"nyc1\") {{id prefix}} }}"

    elif "nyc3-uat" in region:
        query = f"query {{ prefix_list(role:\"{role}\" mask_length:\"{cidr}\" site:\"pp1\") {{id prefix}} }}"
    else:
        query = f"query {{ prefix_list(role:\"{role}\" mask_length:\"{cidr}\" site:\"{region}\") {{id prefix}} }}"

    try:
        r = req.get(netbox_uri, verify="/usr/local/share/ca-certificates/CA.pem", json={"query": query}, headers=headers)
        netbox_response = r.json()
        return netbox_response['data']['prefix_list']
    except Exception as error:
        print(f"Netbox GraphQL query failed: {error}")
        sys.exit(1)


def get_relay(network: IPNetwork) -> str:
        if network.prefixlen == 31:
            return str(network.ip)
        else:
            return str(network.ip + 2)


# Returns reservations for a particular subnet, given a list of DHCP pools and a list of reservations
def subnet_reservations(pools, res_ips, reservations):
    reserved_ips = IPSet(res_ips.keys())

    for pool in pools:
        for ip in pool:
            if ip in reserved_ips:
                reservations[str(ip)] = res_ips[str(ip)]


def generate_subnetconfig(id: str, subnet: IPNetwork, role: str, pools: IPRange, region: str):
    subnetdef = []
    router = get_router(subnet)
    relay = get_relay(subnet)
    if "oob-access" in role:
        subnetdef = {
            "id": int(id),
            "shared-network-name": None,
            "option-data": [
              {"code": 3, "data": router, "name": "routers"},
            ],
            "pools": [{"pool": str(p).replace("-", " - ")} for p in pools],
            "subnet": str(subnet),
            "relay": {"ip-address": relay},
            "user-context": {"role": "oob-access"},
            "ddns-generated-prefix": "bmc",
            "valid-lifetime": 86400,
        }
    else:
        subnetdef = {
            "id": int(id),
            "shared-network-name": None,
            "option-data": [
              {"code": 3, "data": router, "name": "routers"},
            ],
            "pools": [{"pool": str(p).replace("-", " - ")} for p in pools],
            "subnet": str(subnet),
            "relay": {"ip-address": relay},
            "user-context": {"role": role}
        }
    return {
        "service": ["dhcp4"],
        "command": "remote-subnet4-set",
        "arguments": {
            "subnets": [ subnetdef ],
        "server-tags": [ region ]
        }
    }


# Returns reservations for a particular subnet, given a list of DHCP pools and a list of reservations
def subnet_reservations(pools, res_ips, reservations):
    reserved_ips = IPSet(res_ips.keys())

    for pool in pools:
        for ip in pool:
            if ip in reserved_ips:
                reservations[str(ip)] = res_ips[str(ip)]


def generate_resconfig(ip, mac):
    return {
        "service": ["dhcp4"],
        "command": "reservation-add",
        "arguments": {
            "reservation": {
                "subnet-id": 0,
                "hw-address": mac,
                "ip-address": ip
            }
        }
    }


for region in regions:
    if region == "s2r6":
        subnet_types = [
            {"role": "oob-access", "cidr": 25},
            {"role": "oob-access.pp1", "cidr": 25},
            {"role": "underlay.pp1", "cidr": 25},
            {"role": "staging", "cidr": 20},
            {"role": "staging", "cidr": 25},
            {"role": "staging", "cidr": 26},
            {"role": "storage", "cidr": 26},
            {"role": "staging-L3VPN", "cidr": 25},
            {"role": "bgp-controller", "cidr": 31},
        ]
    elif region == "s2r8":
        subnet_types = [
            {"role": "oob-access", "cidr": 25},
            {"role": "oob-access.pp1", "cidr": 25},
            {"role": "staging", "cidr": 20},
            {"role": "staging", "cidr": 25},
            {"role": "staging", "cidr": 26},
            {"role": "storage", "cidr": 26},
            {"role": "staging-L3VPN", "cidr": 25},
            {"role": "bgp-controller", "cidr": 31},
        ]
    elif "s2r" in region:
        subnet_types = [
            {"role": "staging", "cidr": 20},
            {"role": "staging", "cidr": 25},
            {"role": "staging", "cidr": 26},
            {"role": "storage", "cidr": 26},
            {"role": "staging-L3VPN", "cidr": 25},
            {"role": "bgp-controller", "cidr": 31},
        ]
    else:
        subnet_types = [
            {"role": "oob-access", "cidr": 25},
            {"role": "underlay", "cidr": 25},
            {"role": "storage", "cidr": 25},
            {"role": "underlay", "cidr": 26},
            {"role": "hv-management", "cidr": 16},
            {"role": "bgp-controller", "cidr": 31},
        ]

    # Reservations should be in a dict of IP's as keys, mac's as values
    rr = region_reservations(region)
    for type in subnet_types:
        subnet_results = netbox_subnets(type["role"], type["cidr"])

        for s in subnet_results:
            pools = get_pools(IPNetwork(s["prefix"]), type["role"])
            netbox_reservations = netbox_ipaddrs(str(s))
            subnet_reservations(pools, rr, reservations)
            subnet_reservations(pools, netbox_reservations, reservations)
            subnets[s["id"]] = generate_subnetconfig(s["id"], IPNetwork(s["prefix"]), type["role"], pools, region)


# Process and upload subnets to the DB
for subnet in subnets.values():
  response = requests.post(kea_api, json=subnet, timeout=10)
  response.raise_for_status()
  if response.json()[0]['result'] == 0:
    subnetstats['added'] += 1
  else:
    subnetstats['failed'] += 1


# Process and upload reservations to the DB
for ip, mac in reservations.items():
    payload = generate_resconfig(ip, mac)
    response = requests.post(kea_api, json=payload, timeout=10)
    response.raise_for_status()
    if response.json()[0]['result'] == 0:
        resstats['added'] += 1
    elif response.json()[0]['result'] == 1:
        if response.json()[0]['text'] == 'Database duplicate entry error':
            resstats['dupes'] += 1
    else:
        resstats['failed'] += 1

ct = datetime.datetime.now()
print(ct, ' Subnets:      ', subnetstats)
print(ct, ' Reservations: ', resstats)
