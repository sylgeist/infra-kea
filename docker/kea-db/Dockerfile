FROM postgres:14-bullseye

ENV POSTGRES_PASSWORD=pgpassword

ENV KEA_DB=kea_cb
ENV KEA_DB_USER=kea-rw
ENV KEA_DB_USER_PASSWORD=config-password

ENV KEA_STORK_DB=stork_db
ENV KEA_STORK_DB_USER=stork-user
ENV KEA_STORK_DB_USER_PASSWORD=stork-password

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y \
      ca-certificates \
      iputils-ping \
      net-tools && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY rootfs/ /

RUN update-ca-certificates

