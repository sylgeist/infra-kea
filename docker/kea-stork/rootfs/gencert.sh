#!/usr/bin/env bash
set -eo pipefail

OUTFILE="$(mktemp)"
SHOULD_LOGOUT='false'
CACERT=""

function finish() {
  rm -f "${OUTFILE}"
  if [[ "${SHOULD_LOGOUT}" == 'true' ]]; then
    echo 'Logging out ...'
    curl --silent --request POST --header "X-Vault-Token: ${VAULT_TOKEN}" ${CACERT} \
      https://vault:8200/v1/auth/token/revoke-self
  fi
}
trap finish EXIT

function showHelp() {
  echo "Generates a TLS certificate chain and private key using turtle-vault."
  echo "Usage: gencert.sh [OPTIONS]"
  echo "  -h / --help          Show this message and exit"
  echo "  --token value        Vault token (env: VAULT_TOKEN)"
  echo "  --role-id value      Vault approle role_id (env: VAULT_ROLE_ID)"
  echo "  --secret-id value    Vault approle secret_id (env: VAULT_SECRET_ID)"
  echo "  --issuer-path value  Vault certificate issuer path (default: pki/security/issue/service) (env: ISSUER_PATH)"
  echo "  --tls-params value   JSON file with internal.digitalocean.com certificate parameters (env: TLS_PARAM_FILE_PATH)"
  echo "                       See https://www.vaultproject.io/api-docs/secret/pki/#generate-certificate for details."
  echo "                       As per chef vault provider: common_name is required; alt_names, ip_sans, and ttl are optional."
  echo "  --mtls-domain value  service.digitalocean.com single domain (env: MTLS_DOMAIN)"
  echo "  --mtls-ttl value     service.digitalocean.com certificate expiry (default: 720h) (env: MTLS_TTL)"
  echo "  --cert-file value    Path to the generated TLS certificate file (env: TLS_CERT_FILE_PATH)"
  echo "  --key-file value     Path to the generated TLS private key. (env: TLS_KEY_FILE_PATH)"
  echo "  --leaf-cert-only     Don't include issuer CA in certificate file (default: no) (env: LEAF_CERT_ONLY)"
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
  --issuer-path)
    ISSUER_PATH="$2"
    shift # past argument
    shift # past value
    ;;
  --tls-params)
    TLS_PARAM_FILE_PATH="$2"
    shift # past argument
    shift # past value
    ;;
  --mtls-domain)
    MTLS_DOMAIN="$2"
    shift # past argument
    shift # past value
    ;;
  --mtls-ttl)
    MTLS_TTL="$2"
    shift # past argument
    shift # past value
    ;;
  --cert-file)
    TLS_CERT_FILE_PATH="$2"
    shift # past argument
    shift # past value
    ;;
  --key-file)
    TLS_KEY_FILE_PATH="$2"
    shift # past argument
    shift # past value
    ;;
  --leaf-cert-only)
    LEAF_CERT_ONLY='yes'
    shift # past argument
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

if [[ -z "${TLS_CERT_FILE_PATH}" ]]; then
  echo "ERROR: TLS_CERT_FILE_PATH is required"
  exit 1
fi

if [[ -z "${TLS_KEY_FILE_PATH}" ]]; then
  echo "ERROR: TLS_KEY_FILE_PATH is required"
  exit 1
fi

if [[ -z "${TLS_PARAM_FILE_PATH}" ]]; then
  if [[ -z "${MTLS_DOMAIN}" ]]; then
    echo "ERROR: TLS_PARAM_FILE_PATH or MTLS_DOMAIN is required"
    exit 1
  fi
fi

if [[ -z "${ISSUER_PATH}" ]]; then
  ISSUER_PATH="pki/security/issue/service"
fi

if [[ -z "${MTLS_TTL}" ]]; then
  MTLS_TTL="720h"
fi

if [[ -z "${LEAF_CERT_ONLY}" ]]; then
  LEAF_CERT_ONLY='no'
fi

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

if [[ -n "${MTLS_DOMAIN}" ]]; then
  echo "Generating certificate and private key for ${MTLS_DOMAIN} ..."
  curl --silent --show-error --fail --request POST --output "${OUTFILE}" ${CACERT} \
    --header "X-Vault-Token: ${VAULT_TOKEN}" --data "{\"common_name\":\"${MTLS_DOMAIN}\", \"ttl\":\"${MTLS_TTL}\"}" \
    "https://vault-api:8200/v1/pki/security/issue/${MTLS_DOMAIN}"
else
  echo "Generating certificate and private key using ${ISSUER_PATH} ..."
  curl --silent --show-error --fail --request POST --output "${OUTFILE}" ${CACERT} \
    --header "X-Vault-Token: ${VAULT_TOKEN}" --data @"${TLS_PARAM_FILE_PATH}" \
    "https://vault-api:8200/v1/${ISSUER_PATH}"
fi

if [[ "${LEAF_CERT_ONLY}" == 'yes' ]]; then
  echo "Writing certificate to ${TLS_CERT_FILE_PATH} ..."
  jq -r '.data.certificate' "${OUTFILE}" >"${TLS_CERT_FILE_PATH}"
else
  echo "Writing certificate chain to ${TLS_CERT_FILE_PATH} ..."
  jq -r '.data.certificate' "${OUTFILE}" >"${TLS_CERT_FILE_PATH}"
  jq -r '.data.issuing_ca' "${OUTFILE}" >>"${TLS_CERT_FILE_PATH}"
fi

echo "Writing private key to ${TLS_KEY_FILE_PATH} ..."
jq -r '.data.private_key' "${OUTFILE}" >"${TLS_KEY_FILE_PATH}"
