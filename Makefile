#!/usr/bin/make -f

REGISTRY_CFG = registry.config
NODES = node-server node-render node-server2 node-render2
NODE_DIRS = $(addprefix /tmp/icedata/, $(NODES) registry)

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

.PHONY: clean deploy-app start-servers start-nodes start-all start-grid start-registry start-node-server start-node-render stop-grid show-nodes client media borrar-datos

clean: stop-grid
	-$(RM) *~
	-$(RM) -r /tmp/icedata
	-killall icegridnode

stop-grid:
	-killall icegridnode icegridregistry
	@for node in $(NODES); do \
		$(call ig_admin, node shutdown $$node); \
	done
	@echo -- grid stopped

show-nodes:
	$(call ig_admin, node list)

deploy-app:
	$(call ig_admin, application update Spotificeapp-py.xml)

start-servers:
	$(call ig_admin, server start $(SERVERS))

start-nodes: start-node-server start-node-render start-node-server2 start-node-render2

start-local-nodes: start-node-server start-node-render

start-remote-nodes: start-node-server2 start-node-render2

start-all: start-registry start-nodes deploy-app start-servers

start-nodes-only: start-nodes deploy-app start-servers

## local ####
start-grid: /tmp/icedata/registry $(NODE_DIRS)
	cp default-templates.xml /tmp/icedata/

	@echo -- starting IceGrid registry
	icegridregistry --Ice.Config=$(REGISTRY_CFG) &

	@echo -- waiting registry to start...
	@while ! ss -ltnH 2>/dev/null | grep -q ':10000'; do sleep 1; done

	@for node in $(NODES); do \
		echo -- starting $$node; \
		icegridnode --Ice.Config=$$node.config & \
	done

	@echo -- ok

## distribuido ##
start-registry: /tmp/icedata/registry
	cp default-templates.xml /tmp/icedata/

	@echo -- starting IceGrid registry
	icegridregistry --Ice.Config=$(REGISTRY_CFG) &

	@echo -- waiting registry to start...
	@while ! ss -ltnH 2>/dev/null | grep -q ':10000'; do sleep 1; done

	@echo -- ok

start-node-server: $(NODE_DIRS)
	icegridnode --Ice.Config=node-server.config & \

start-node-render: $(NODE_DIRS)
	icegridnode --Ice.Config=node-render.config & \

start-node-server2: $(NODE_DIRS)
	icegridnode --Ice.Config=node-server2.config & \

start-node-render2: $(NODE_DIRS)
	icegridnode --Ice.Config=node-render2.config & \

client:
	python3 media_control_v1.py --Ice.Config=locator.config

