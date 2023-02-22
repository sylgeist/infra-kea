# This is the primary/secondary lookup table for DNS. If/when dns servers change this needs to be updated
name_server = {
    "ams2": ["10.0.0.32", "10.0.0.222"],
    "ams3": ["10.0.0.48", "10.0.0.239"],
    "blr1": ["10.0.0.93", "10.0.0.172"],
    "fra1": ["10.0.0.16", "10.0.0.166"],
    "lon1": ["10.0.0.15", "10.0.0.75"],
    "nbg1": ["10.0.0.27", "10.0.0.168"],
    "nyc2": ["10.0.0.32", "10.0.0.222"],
    "nyc3": ["10.0.0.35", "10.0.0.46"],
    "sfo1": ["10.0.0.32", "10.0.0.222"],
    "sfo2": ["10.0.0.24", "10.0.0.170"],
    "sfo3": ["10.0.0.226", "10.0.0.226"],
    "sgp1": ["10.0.0.25", "10.0.0.175"],
    "syd1": ["10.0.0.35", "10.0.0.225"],
    "tor1": ["10.0.0.205", "10.0.0.166"],
    "stage1": ["10.0.0.11", "10.0.0.10"],
    "stage2": ["10.0.0.10", "10.0.0.11"],
    "stage3": ["10.0.0.10", "10.0.0.85"],
    "stage4": ["10.0.0.10", "10.0.0.106"],
    "stage5": ["10.0.0.10"],
    "stage6": ["10.0.0.10", "10.0.0.228"],
    "stage7": ["10.0.0.10"],
    "stage8": ["10.0.0.40"],
    "lab1": ["10.0.0.5"],
}

# This is the lookup table for "next-server" dhcp entries, as we deploy in new regions
# we will need to add in the address for each region
next_servers = {
    "ams2": "10.0.0.11",
    "ams3": "10.0.0.39",
    "blr1": "10.0.0.207",
    "fra1": "10.0.0.243",
    "lon1": "10.0.0.170",
    "nbg1": "10.0.0.38",
    "nyc2": "10.0.0.11",
    "nyc3": "10.0.0.49",
    "sfo1": "10.0.0.11",
    "sfo2": "10.0.0.40",
    "sfo3": "10.0.0.243",
    "sgp1": "10.0.0.22",
    "syd1": "10.0.0.217",
    "tor1": "10.0.0.220",
    "stage1": "10.0.0.4",
    "stage2": "10.0.0.2",
    "stage3": "10.0.0.2",
    "stage4": "10.0.0.2",
    "stage5": "10.0.0.2",
    "stage6": "10.0.0.2",
    "stage7": "10.0.0.2",
    "stage8": "10.0.0.2",
    "lab1": "",
}

staging_regions = (
    'stage1',
    'stage2',
    'stage3',
    'stage4',
    'stage5',
    'stage6',
    'stage7',
    'stage8'
  )

prod_regions = (
    'ams2',
    'ams3',
    'blr1',
    'fra1',
    'lon1',
    'nbg1',
    'nyc2',
    'nyc3',
    'sfo1',
    'sfo2',
    'sfo3',
    'sgp1',
    'syd1',
    'tor1'
  )
