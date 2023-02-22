FROM ubuntu:22.04

ARG STORK_VERSION=1.8.0.221205192529

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y \
      cron \
      curl \
      iputils-ping \
      jq \
      net-tools \
      rsyslog \
      supervisor && \
    curl -o isc-stork-server.deb https://dl.cloudsmith.io/public/isc/stork/deb/any-distro/pool/any-version/main/i/is/isc-stork-server_${STORK_VERSION}/isc-stork-server_${STORK_VERSION}_amd64.deb && \
    dpkg -i isc-stork-server.deb && \
    rm isc-stork-server.deb && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY rootfs/ /

RUN update-ca-certificates

ENV VAULT_ROLE_ID=not-an-app-role
ENV VAULT_SECRET_ID=not-a-secret-id

ENV STORK_DATABASE_HOST=kea-db
ENV STORK_DATABASE_PORT=5432
ENV STORK_DATABASE_NAME=stork
ENV STORK_DATABASE_USER_NAME=stork
ENV STORK_DATABASE_PASSWORD=not-a-password
ENV STORK_REST_HOST=0.0.0.0
ENV STORK_REST_STATIC_FILES_DIR=/usr/share/stork/www
ENV STORK_REST_TLS_CERTIFICATE=cert-location
ENV STORK_REST_TLS_PRIVATE_KEY=key-location

ENV CA_FILE_PATH=ca-location
ENV TLS_CERT_FILE_PATH=gencert-cert-location
ENV TLS_KEY_FILE_PATH=gencert-key-location
ENV TLS_PARAM_FILE_PATH=gencert-params-location

ENTRYPOINT ["/entrypoint.sh"]
