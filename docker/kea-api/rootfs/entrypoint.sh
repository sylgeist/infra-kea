#!/usr/bin/env bash

set -e
printenv | egrep "VAULT_SECRET_ID|CA_FILE_PATH|SECRET_PATH|VAULT_ROLE_ID|CERT_FILE|KEY_FILE|REGION" > /etc/environment

# /tls-get.sh
crontab /etc/crontab
/generate-kea-conf.py > /etc/kea/kea.conf

/usr/bin/supervisord -c /etc/supervisor/supervisord.conf
