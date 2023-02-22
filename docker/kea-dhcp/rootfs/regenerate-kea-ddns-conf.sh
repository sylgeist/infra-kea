#!/usr/bin/env bash
#
# This script runs generate-kea-conf.py and validates the configuration
# before moving it into place and reloading it.
#
# This script may be used to start Kea for the first time or to refresh
# the configuration for an already-running Kea service
#

set -e

readonly CUR=/etc/kea/kea-ddns.conf
readonly OLD=/etc/kea/kea-ddns.conf.old
readonly NEW=/etc/kea/kea-ddns.conf.new

# generate new conf
/generate-kea-ddns-conf.py > $NEW

# syntax check new conf
kea-dhcp-ddns -t $NEW
if [ $? -ne 0 ]
then
  echo "Kea DDNS regeneration failed" | /usr/bin/logger -p local0.info -t kea-ddns
  exit
fi

# if it exists, move current conf -> old
if [ -f $CUR ]; then
  cp -v $CUR $OLD
fi

# move new conf -> current
cp -v $NEW $CUR
echo

keactrl reload -s dhcp_ddns

# show status to put our minds at ease
keactrl status
echo
