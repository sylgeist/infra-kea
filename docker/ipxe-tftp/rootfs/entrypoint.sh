#!/usr/bin/env bash

# Copy ipxe files to the tftp directory
[ -d /tftpd ] && /bin/cp /var/lib/tftpboot/*.{efi,pxe,usb} /tftpd/

# With HTTP booting we need to copy the efi files to /www as well 
[ -d /www ] && /bin/cp /var/lib/tftpboot/*.efi /www/
