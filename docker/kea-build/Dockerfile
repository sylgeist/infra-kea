# Build core Kea app
FROM ubuntu:22.04 AS kea-build

ARG KEA_VERSION=2.2.0
ARG KEA_SUBSCRIPTION=XXXXXXXXX

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y \
      autoconf \
      build-essential \
      curl \
      libboost-dev \
      libboost-system-dev \
      liblog4cplus-dev \
      libssl-dev \
      libtool \
      postgresql-server-dev-14 \
      python3 \
      unzip && \
    mkdir /kea-build && \
    cd /kea-build && \
    curl -o kea.tar.gz ftp://ftp.isc.org/isc/kea/${KEA_VERSION}/kea-${KEA_VERSION}.tar.gz && \
    curl -o kea-subscription.tar.gz https://dl.cloudsmith.io/${KEA_SUBSCRIPTION}/isc/kea-2-2-prv/raw/versions/${KEA_VERSION}/kea-subscription-${KEA_VERSION}.tar.gz && \
    tar xf kea.tar.gz && \
    rm kea.tar.gz && \
    cd kea-${KEA_VERSION} && \
    tar xf ../kea-subscription.tar.gz && \
    rm ../kea-subscription.tar.gz && \
    autoreconf -if && \
    ./configure --with-pgsql --enable-generate-messages --enable-perfdhcp --prefix=/ --enable-shell --with-site-packages=/usr/lib/python3/dist-packages && \
    make -j $(nproc) && \
    make install

RUN rm /lib/libkea*.a && rm /lib/libkea*.la && \
    rm /lib/kea/hooks/libdhcp*.a && rm /lib/kea/hooks/libdhcp*.la && \
    cd / && tar -cf keafiles.tar /lib/libkea*.so.* /lib/kea /sbin/kea* /share/kea /usr/lib/python3/dist-packages/kea
