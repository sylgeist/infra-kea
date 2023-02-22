FROM ubuntu:20.04 AS first

ARG GIT_COMMIT=unknown
ENV GIT_COMMIT ${GIT_COMMIT}

COPY rootfs/ /

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y \
      build-essential \
      curl \
      dnsutils \
      genisoimage \
      git \
      liblzma-dev \
      patch \
      gcc-aarch64-linux-gnu && \
    git clone https://git.ipxe.org/ipxe.git && \
    cd ipxe && \
    git checkout -b build 831f17f66f9d0082509343de2cf57f9478d877e0 && \
    patch -p1 </ipxe_UEFI_sanboot.patch && \
    cd src && \
    sed -i \
      -e "s|undef\tDOWNLOAD_PROTO_HTTPS|define\tDOWNLOAD_PROTO_HTTPS|g" \
      -e "s|^//#define NTP_CMD|#define NTP_CMD|g" \
      -e "s|^//#define CERT_CMD|#define CERT_CMD|g" \
      -e "s|^//#define NSLOOKUP_CMD|#define NSLOOKUP_CMD|g" \
      -e "s|define\tNET_PROTO_LACP|undef\tNET_PROTO_LACP|g" \
      config/general.h && \
    sed -i "s|define OCSP_CHECK|undef OCSP_CHECK|" config/crypto.h && \
    sed -i "s|__GIT_COMMIT__|$GIT_COMMIT|g" /chain.ipxe && \
    make -j $(nproc) \
      bin-x86_64-efi/ipxe.efi \
      bin-x86_64-efi/snponly.efi \
      bin-x86_64-pcbios/ipxe.pxe \
      bin/ipxe.usb \
      EMBED=/chain.ipxe \
      CERT=/DigiCert_CA_Chain.pem \
      TRUST=/DigiCert_CA_Chain.pem \ 
      DEBUG=tls,x509,ntp && \
    make -j $(nproc) \
      CROSS=aarch64-linux-gnu- \
      bin-arm64-efi/snponly.efi \
      EMBED=/chain.ipxe \
      CERT=/DigiCert_CA_Chain.pem \
      TRUST=/DigiCert_CA_Chain.pem \
      DEBUG=tls,x509,ntp

FROM ubuntu:20.04

RUN apt-get update && \ 
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y \
      curl \
      iputils-ping \
      netcat \
      net-tools \
      tftpd-hpa && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Keeping these existing ipxe build artifacts without arch suffixes in order to
# avoid a breaking change. Once all downstream consumers of these ipxe files
# have been converted to using arch specific filenames, remove these
COPY --from=first /ipxe/src/bin-x86_64-efi/ipxe.efi /var/lib/tftpboot/ipxe.efi
COPY --from=first /ipxe/src/bin-x86_64-efi/snponly.efi /var/lib/tftpboot/snponly.efi
COPY --from=first /ipxe/src/bin-x86_64-pcbios/ipxe.pxe /var/lib/tftpboot/ipxe.pxe
COPY --from=first /ipxe/src/bin/ipxe.usb /var/lib/tftpboot/ipxe.usb
COPY --from=first /ipxe/src/bin-x86_64-efi/ipxe.efi /var/lib/tftpboot/ipxe-x86_64.efi
COPY --from=first /ipxe/src/bin-x86_64-efi/snponly.efi /var/lib/tftpboot/snponly-x86_64.efi
COPY --from=first /ipxe/src/bin-x86_64-pcbios/ipxe.pxe /var/lib/tftpboot/ipxe-x86_64.pxe
COPY --from=first /ipxe/src/bin-arm64-efi/snponly.efi /var/lib/tftpboot/snponly-arm64.efi
COPY --from=first /entrypoint.sh /

WORKDIR /

ENTRYPOINT [ "/usr/sbin/in.tftpd", "--foreground", "--user", "tftp", "--address", ":69", "--secure", "/var/lib/tftpboot", "-vvv" ]
