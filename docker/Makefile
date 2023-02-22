#####################################
# Convenience Makefile for building #
# and testing images locally        #
#####################################
GIT_COMMIT := $(shell git rev-parse --short HEAD)
CONTAINERS := ipxe-tftp kea-build kea-dhcp kea-api kea-stork kea-db
REGISTRY := localhost
TEAM := infra-eng

build:
	$(foreach container, $(CONTAINERS), \
		docker build $(container) \
		--build-arg GIT_COMMIT="${GIT_COMMIT}" \
		--tag "${REGISTRY}/${TEAM}/$(container):${GIT_COMMIT}" \
		--tag "${REGISTRY}/${TEAM}/$(container):latest"; \
	)

push:
	$(foreach container, $(CONTAINERS), \
		docker push "${REGISTRY}/${TEAM}/$(container):${GIT_COMMIT}"; \
		docker push "${REGISTRY}/${TEAM}/$(container):latest"; \
	)
