#!/usr/bin/env bash
set -eo pipefail

OUTFILE="$(mktemp)"
SHOULD_LOGOUT='false'

function finish() {
  rm -f "${OUTFILE}"
  if [[ "${SHOULD_LOGOUT}" == 'true' ]]; then
    echo 'Logging out ...'
    curl --request POST --header "X-Vault-Token: ${VAULT_TOKEN}" \
      https://vault-api:8200/v1/auth/token/revoke-self
  fi
}
trap finish EXIT

function showHelp() {
  echo "Downloads a TLS certificate chain and private key stored in turtle-vault."
  echo "Usage: tls-get.sh [OPTIONS]"
  echo "  -h / --help          Show this message and exit"
  echo "  --token value        Vault token (env: VAULT_TOKEN)"
  echo "  --role-id value      Vault approle role_id (env: VAULT_ROLE_ID)"
  echo "  --secret-id value    Vault approle secret_id (env: VAULT_SECRET_ID)"
  echo "  --secret-path value  Path to secret that stores the TLS cert and key (env: SECRET_PATH)"
  echo "  --cert-param value   Secret parameter for TLS cert (default: cert) (env: CERT_PARAM)"
  echo "  --key-param value    Secret parameter for TLS key (default: key) (env: KEY_PARAM)"
  echo "  --cert-file value    TLS cert file to create (env: CERT_FILE)"
  echo "  --key-file value     TLS key file to create (env: KEY_FILE)"
  echo "  --ca value           Path to ca root cert file (env: CA_FILE_PATH)"
  echo "                       Required if ca is not trusted by your system."
  exit 1
}

while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
  -h | --help)
    showHelp
    ;;
  --token)
    VAULT_TOKEN="$2"
    shift # past argument
    shift # past value
    ;;
  --role-id)
    VAULT_ROLE_ID="$2"
    shift # past argument
    shift # past value
    ;;
  --secret-id)
    VAULT_SECRET_ID="$2"
    shift # past argument
    shift # past value
    ;;
  --secret-path)
    SECRET_PATH="$2"
    shift # past argument
    shift # past value
    ;;
  --cert-param)
    CERT_PARAM="$2"
    shift # past argument
    shift # past value
    ;;
  --key-param)
    KEY_PARAM="$2"
    shift # past argument
    shift # past value
    ;;
  --cert-file)
    CERT_FILE="$2"
    shift # past argument
    shift # past value
    ;;
  --key-file)
    KEY_FILE="$2"
    shift # past argument
    shift # past value
    ;;
  --ca)
    CA_FILE_PATH="$2"
    shift # past argument
    shift # past value
    ;;
  *)
    echo "ERROR: Unknown option: $1"
    showHelp
    ;;
  esac
done

if [[ -z "${SECRET_PATH}" ]]; then
  echo "ERROR: SECRET_PATH is required"
  exit 1
fi

if [[ -z "${CERT_FILE}" ]]; then
  echo "ERROR: CERT_FILE is required"
  exit 1
fi

if [[ -z "${KEY_FILE}" ]]; then
  echo "ERROR: KEY_FILE is required"
  exit 1
fi

if [[ -z "${CERT_PARAM}" ]]; then
  CERT_PARAM='cert'
fi

if [[ -z "${KEY_PARAM}" ]]; then
  KEY_PARAM='key'
fi

CACERT=""
if [[ -n "${CA_FILE_PATH}" ]]; then
  CACERT="--cacert ${CA_FILE_PATH}"
fi

if [[ -n "${VAULT_ROLE_ID}" ]]; then
  if [[ -n "${VAULT_SECRET_ID}" ]]; then
    echo "Authenticating with approle ..."
    curl --silent --show-error --fail --request POST --output "${OUTFILE}" ${CACERT} \
      --data "{\"role_id\":\"${VAULT_ROLE_ID}\",\"secret_id\":\"${VAULT_SECRET_ID}\"}" \
      https://vault-api:8200/v1/auth/approle/login
    VAULT_TOKEN="$(jq -r '.auth.client_token' "${OUTFILE}")"
    SHOULD_LOGOUT="$(jq -r '.auth.renewable' "${OUTFILE}")"
  fi
fi

if [[ -z "${VAULT_TOKEN}" ]]; then
  echo "ERROR: VAULT_TOKEN is required"
  exit 1
fi

echo "Reading from ${SECRET_PATH} ..."
curl --silent --show-error --fail --output "${OUTFILE}" ${CACERT} \
  --header "X-Vault-Token: ${VAULT_TOKEN}" \
  "https://vault-api:8200/v1/${SECRET_PATH}"

if [[ "${SECRET_PATH}" == secret-versioned/* ]]; then
  echo "Writing certificate chain to ${CERT_FILE} ..."
  jq -r ".data.data.${CERT_PARAM}" "${OUTFILE}" >"${CERT_FILE}"
  echo "Writing private key to ${KEY_FILE} ..."
  jq -r ".data.data.${KEY_PARAM}" "${OUTFILE}" >"${KEY_FILE}"
else
  echo "Writing certificate chain to ${CERT_FILE} ..."
  jq -r ".data.${CERT_PARAM}" "${OUTFILE}" >"${CERT_FILE}"
  echo "Writing private key to ${KEY_FILE} ..."
  jq -r ".data.${KEY_PARAM}" "${OUTFILE}" >"${KEY_FILE}"
fi
