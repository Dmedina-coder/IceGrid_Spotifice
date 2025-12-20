#!/usr/bin/make -f

PORT ?= 10000
SUBNET ?= 10.0.2.0/24

REGISTRY_CFG = registry.config
NODES = node-server node-render node-server2 node-render2

SERVERS = media-server media-render media-server2 media-render2

define ig_admin
    icegridadmin --Ice.Config=locator.config -u user -p pass -e "$(1)"
endef

/tmp/icedata/%:
	mkdir -p $@

media: portal2-ost.zip
	mkdir -p media
	unzip -o $< -d media

portal2-ost.zip:
    wget http://media.steampowered.com/apps/portal2/soundtrack/Portal2-OST-Complete.zip -O $@

borrar-datos: 
	-find . -type f -name "*.bz2" -delete
	-find . -type f -name "*.sum" -delete
	-$(RM) *.sum

.PHONY: clean deploy-app start-servers start-nodes start-all start-grid start-registry start-node-server start-node-render stop-grid show-nodes client media borrar-datos update-locator

update-configs:
	@echo -- scanning $(SUBNET) for tcp/$(PORT)
	@LOCATOR_IP=$$(nmap -p $(PORT) --open $(SUBNET) 2>/dev/null | grep -oP '(?<=Nmap scan report for )[0-9.]+' | head -1); \
	if [ -z "$$LOCATOR_IP" ]; then echo "No host with tcp/$(PORT) open in $(SUBNET)"; exit 1; fi; \
	for cfg in locator.config node-server2.config node-render2.config; do \
		sed -i -E 's/(Ice.Default.Locator=.*-h )[^ ]+/\1'$$LOCATOR_IP'/' $$cfg; \
		echo "-- locator set to $$LOCATOR_IP in $$cfg"; \
	done

clean: stop-grid
	-$(RM) *~
	-$(RM) -r /tmp/icedata
	-killall icegridnode

stop-grid:
	@for node in $(NODES); do \
		$(call ig_admin, node shutdown $$node); \
	done
	-killall icegridnode icegridregistry
	@echo -- grid stopped

show-nodes:
	$(call ig_admin, node list)

deploy-app:
	$(call ig_admin,application add ./Spotificeapp-py.xml)

deploy-app-update:
	$(call ig_admin,application update ./Spotificeapp-py.xml)
	- icepatch2calc distrib

start-servers:
	@for server in $(SERVERS); do \
		$(call ig_admin, server start $$server); \
	done

start-nodes: start-node-server start-node-render start-node-server2 start-node-render2

start-local-nodes: start-node-server start-node-render

start-remote-nodes: update-configs start-node-server2 start-node-render2 

start-all: start-registry start-nodes deploy-app start-servers

start-nodes-only: start-nodes deploy-app start-servers

start-registry: /tmp/icedata/registry
	cp default-templates.xml /tmp/icedata/

	@echo -- starting IceGrid registry
	icegridregistry --Ice.Config=$(REGISTRY_CFG) &

	@echo -- waiting registry to start...
	@while ! ss -ltnH 2>/dev/null | grep -q ':$(PORT)'; do sleep 1; done

	@echo -- ok

start-node-server: /tmp/icedata/node-server /tmp/icedata/registry
	icegridnode --Ice.Config=node-server.config & \

start-node-render: /tmp/icedata/node-render /tmp/icedata/registry
	icegridnode --Ice.Config=node-render.config & \

start-node-server2: /tmp/icedata/node-server2 /tmp/icedata/registry
	icegridnode --Ice.Config=node-server2.config & \

start-node-render2: /tmp/icedata/node-render2 /tmp/icedata/registry
	icegridnode --Ice.Config=node-render2.config & \

client:
	python3 media_control_v1.py --Ice.Config=locator.config
