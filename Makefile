#!/usr/bin/make -f

REGISTRY_CFG = registry.config
NODES = node-server node-render
NODE_DIRS = $(addprefix /tmp/icedata/, $(NODES) registry)

define ig_admin
    icegridadmin --Ice.Config=locator.config -u user -p pass -e "$(1)"
endef

/tmp/icedata/%:
	mkdir -p $@

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

stop-grid:
	-killall icegridnode icegridregistry
	@for node in $(NODES); do \
		$(call ig_admin, node shutdown $$node); \
	done
	@echo -- grid stopped

show-nodes:
	$(call ig_admin, node list)

media: portal2-ost.zip
	mkdir -p media
	unzip -o $< -d media

portal2-ost.zip:
    wget http://media.steampowered.com/apps/portal2/soundtrack/Portal2-OST-Complete.zip -O $@

borrar-datos: 
	-find . -type f -name "*.bz2" -delete
	-$(RM) *.sum

.PHONY: clean

clean: stop-grid
	-$(RM) *~
	-$(RM) -r /tmp/icedata
	-killall icegridnode

