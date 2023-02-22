FROM ubuntu:22.04

ARG PG_EXPORTER=0.11.1

ENV DATA_SOURCE_URI=not-a-uri
ENV DATA_SOURCE_USER=postgres
ENV DATA_SOURCE_PASS=not-a-password
ENV PG_EXPORTER_AUTO_DISCOVER_DATABASES=true

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y \
      iputils-ping \
      net-tools \
      wget \
      ca-certificates && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    wget -O pg_exporter.tar.gz https://github.com/prometheus-community/postgres_exporter/releases/download/v${PG_EXPORTER}/postgres_exporter-${PG_EXPORTER}.linux-amd64.tar.gz && \
    tar xzf pg_exporter.tar.gz --strip-components 1 postgres_exporter-${PG_EXPORTER}.linux-amd64/postgres_exporter && rm pg_exporter.tar.gz

COPY rootfs/ /

RUN update-ca-certificates

ENTRYPOINT ["/postgres_exporter"]
