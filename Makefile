#!/usr/bin/make -f

REGISTRY_HOST = 127.0.0.1
REGISTRY_PORT = 10000

NODES = node-1 node-2

define ig_admin
    icegridadmin --Ice.Config=locator.config -u user -p pass -e "$(1)"
endef


/tmp/icedata/%:
	@mkdir -p $@

#Descargar banda sonora de Portal 2
media: portal2-ost.zip
	mkdir -p distrib/media
	unzip -o $< -d distrib/media
portal2-ost.zip:
	wget http://media.steampowered.com/apps/portal2/soundtrack/Portal2-OST-Complete.zip -O $@

.PHONY: clean media show-state deploy-app start-registry start-grid stop-grid node-1 node-2 client

# Borrar datos temporales
clean: stop-grid
	@-$(RM) *~ 2>/dev/null
	@-$(RM) -r /tmp/icedata 2>/dev/null

	@echo -- tmp files deleted
	

# Mostrar nodos y servers
list-nodes-servers:
	@echo -- NODES --
	@$(call ig_admin, node list)
	@echo 
	@echo -- SERVERS --
	@$(call ig_admin, server list)

#Desplegar la aplicacion
deploy-app:
	@echo -- patching application...
	@icepatch2calc distrib
	@echo -- deploying application...
	@if $(call ig_admin,application describe Spotifice) >/dev/null 2>&1; then \
		$(call ig_admin,application update ./Spotificeapp-py.xml); \
	else \
		$(call ig_admin,application add ./Spotificeapp-py.xml); \
	fi
	@echo -- application deployed successfully

# Arrancar Registry + Nodos
start-registry: /tmp/icedata/registry
	@cp default-templates.xml /tmp/icedata/

	@echo -- starting IceGrid registry
	@icegridregistry --Ice.Config=registry.config &

	@echo -- waiting registry to start...
	@while ! bash -c ':> /dev/tcp/$(REGISTRY_HOST)/$(REGISTRY_PORT)' 2>/dev/null; do sleep 1; done

	@echo -- registry started

# Arrancar Registry + Nodo 1
start-grid: stop-grid start-registry node-1

#Parar Registry + Nodos
stop-grid:
	-@for node in $(NODES); do \
		$(call ig_admin, node shutdown $$node) 2>/dev/null || true; \
	done
	-@killall icegridnode icegridregistry 2>/dev/null || true
	@echo -- grid stopped

#Arrancar nodo 1
node-1: /tmp/icedata/node-1 /tmp/icedata/registry
	@icegridnode --Ice.Config=node-1.config & 
	@echo -- node-1 started

#Arrancar nodo 2
node-2: /tmp/icedata/node-2 /tmp/icedata/registry
	@icegridnode --Ice.Config=node-2.config &
	@echo -- node-2 started

#Arrancar Controller
client:
	@echo -- starting client
	@python3 media_control_v1.py --Ice.Config=locator.config

