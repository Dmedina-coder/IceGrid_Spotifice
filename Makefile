#!/usr/bin/make -f

NODES     := $(basename $(sort $(wildcard node*.config)))
NODE_DIRS := $(addprefix /tmp/icedata/, $(NODES))

define ig_admin
    icegridadmin --Ice.Config=locator.config -u user -p pass -e "$(1)"
endef

/tmp/icedata/%:
	mkdir -p $@

start-grid: /tmp/icedata/registry $(NODE_DIRS)
	cp default-templates.xml /tmp/icedata/
	icegridnode --Ice.Config=node-Spotifice.config &

	@echo -- waiting registry to start...
	@while ! ss -ltnH 2>/dev/null | grep -q ':4061'; do sleep 1; done

	@for node in $(filter-out node-Spotifice, $(NODES)); do \
    	icegridnode --Ice.Config=$$node.config & \
    	echo -- $$node started; \
	done

	@echo -- ok

stop-grid:
	$(call ig_admin, node shutdown node-Spotifice)
	@while ss -ltnH | grep -q ":4061"; do sleep 1; done
	-killall icegridnode
	@echo -- ok

show-nodes:
	$(call ig_admin, node list)

media: portal2-ost.zip
	mkdir -p media
	unzip -o $< -d media

portal2-ost.zip:
    wget http://media.steampowered.com/apps/portal2/soundtrack/Portal2-OST-Complete.zip -O $@

borrar-datos: 
	-$(RM) -r ./*.bz2

.PHONY: clean

clean: stop-grid
	-$(RM) *~
	-$(RM) -r /tmp/icedata
	-killall icegridnode

