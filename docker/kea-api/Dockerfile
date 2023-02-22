ARG KEA_VERSION=2.2.0

FROM docker.internal/kea-package:${KEA_VERSION} AS kea-package

# Assemble completed Kea container with Stork agent
FROM ubuntu:22.04

ENV KEA_DB=kea_db
ENV KEA_DB_HOST=127.0.0.1
ENV KEA_DB_USER=kea-rw
ENV KEA_DB_USER_PASSWORD=password
ENV VAULT_ROLE_ID=not-an-app-role
ENV VAULT_SECRET_ID=not-a-secret-id
ENV CERT_FILE=cert-file-location
ENV KEY_FILE=cert-key-location
ENV CA_FILE_PATH=ca-location
ENV REGION=not-a-region

COPY --from=kea-package /keafiles.tar /

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y \
      cron \
      curl \
      iputils-ping \
      libboost-system-dev \
      liblog4cplus-dev \
      jq \
      libgrpc++1 \
      libssl-dev \
      libprotobuf23 \
      netcat \
      net-tools \
      num-utils \
      postgresql-client-14 \
      python3 \
      python3-dnspython \
      python3-netaddr \
      python3-requests \
      rsyslog \
      supervisor \
      unzip \
      zlib1g && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    cd / && tar -xf keafiles.tar && rm keafiles.tar && \
    ldconfig

COPY rootfs/ /

RUN /bin/bash -c "if [[ ! -d /run/kea ]]; then mkdir -p /run/kea; fi"
RUN update-ca-certificates

ENTRYPOINT ["/entrypoint.sh"]
