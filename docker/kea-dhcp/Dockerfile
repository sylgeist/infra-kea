ARG KEA_VERSION=2.2.0

# Build core Kea app
FROM docker.internal/kea-package:${KEA_VERSION} AS hook-build

COPY hooks/ /hooks/

RUN cd /hooks && make

# Build Shipyard update script
FROM ubuntu:22.04 AS shipyard-update-build

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y \
      clang-14 \
      make \
      pkg-config \
      protobuf-compiler-grpc \
      libgrpc-dev \
      libgrpc++-dev

COPY /shipyard-update /shipyard-update/

RUN cd /shipyard-update && make

# Assemble completed Kea container with Stork agent
FROM ubuntu:22.04

ARG STORK_VERSION=1.8.0.221205192523

ENV KEA_DB=kea_db
ENV KEA_DB_HOST=127.0.0.1
ENV KEA_DB_USER=kea-rw
ENV KEA_DB_USER_PASSWORD=password
ENV DOMAIN_SUFFIX=not-a-domain-suffix.
ENV DDNS_SERVER_IP=127.0.0.1
ENV DDNS_TSIG_KEY=not-a-secret
ENV STORK_AGENT_SERVER_URL=http://localhost
ENV STORK_AGENT_HOST=not-an-agent-name
ENV VAULT_ROLE_ID=not-an-app-role
ENV VAULT_SECRET_ID=not-a-secret-id
ENV CERT_FILE=cert-file-location
ENV KEY_FILE=cert-key-location
ENV CA_FILE_PATH=ca-location
ENV REGION=not-a-region

COPY --from=hook-build /keafiles.tar /

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
    curl -o isc-stork-agent.deb https://dl.cloudsmith.io/public/isc/stork/deb/any-distro/pool/any-version/main/i/is/isc-stork-agent_${STORK_VERSION}/isc-stork-agent_${STORK_VERSION}_amd64.deb && \
    dpkg -i isc-stork-agent.deb && \
    rm isc-stork-agent.deb && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    cd / && tar -xf keafiles.tar && rm keafiles.tar && \
    ldconfig

COPY rootfs/ /
COPY --from=hook-build /hooks/*.so /lib/kea/hooks/
COPY --from=shipyard-update-build /shipyard-update/shipyard_bmc_update /usr/sbin/

RUN /bin/bash -c "if [[ ! -d /run/kea ]]; then mkdir -p /run/kea; fi"
RUN update-ca-certificates

ENTRYPOINT ["/entrypoint.sh"]
