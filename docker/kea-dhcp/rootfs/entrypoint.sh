#!/usr/bin/env bash

set -e
printenv | egrep "VAULT_SECRET_ID|CA_FILE_PATH|SECRET_PATH|VAULT_ROLE_ID|CERT_FILE|KEY_FILE|REGION|DOMAIN_SUFFIX|DDNS_TSIG_KEY" > /etc/environment

crontab /etc/crontab
/tls-get.sh
/generate-kea-conf.py > /etc/kea/kea.conf
/generate-kea-ddns-conf.py > /etc/kea/kea-ddns.conf

/usr/bin/supervisord -c /etc/supervisor/supervisord.conf
