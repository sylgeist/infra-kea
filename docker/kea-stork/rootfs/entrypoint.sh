#!/usr/bin/env bash

set -e
printenv | egrep "VAULT_SECRET_ID|CA_FILE_PATH|VAULT_ROLE_ID|TLS_CERT_FILE_PATH|TLS_KEY_FILE_PATH|TLS_PARAM_FILE_PATH" > /etc/environment

crontab /etc/crontab
/gencert.sh
/usr/bin/supervisord -c /etc/supervisor/supervisord.conf
