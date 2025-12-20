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

#Descargar banda sonora de Portal 2
media: portal2-ost.zip
	mkdir -p distrib/media
	unzip -o $< -d distrib/media
portal2-ost.zip:
	wget http://media.steampowered.com/apps/portal2/soundtrack/Portal2-OST-Complete.zip -O $@

.PHONY: clean deploy-app start-servers start-nodes start-all start-grid start-registry start-node-server start-node-render stop-grid show-nodes client media borrar-datos update-locator

#Borrar datos temporales
clean: stop-grid
	-$(RM) *~
	-$(RM) -r /tmp/icedata
	-killall icegridnode

#Mostrar nodos
show-nodes:
	$(call ig_admin, node list)

#Desplegar la aplicacion
deploy-app:
	$(call ig_admin,application add ./Spotificeapp-py.xml)

#Actualizar la aplicacion
deploy-app-update:
	$(call ig_admin,application update ./Spotificeapp-py.xml)
	- icepatch2calc distrib

#Eliminar la aplicacion
remove-app:
	$(call ig_admin,application remove Spotificeapp)

#Arrancar todos los servers del Grid
start-servers:
	@for server in $(SERVERS); do \
		$(call ig_admin, server start $$server); \
	done

# Ejecutar en la maquina local
start-local-nodes: start-node-server start-node-render

# Ejecutar en la maquina remota
start-remote-nodes: start-node-server2 start-node-render2 

# Arrancar Registry + Nodos
start-registry: /tmp/icedata/registry
	cp default-templates.xml /tmp/icedata/

	@echo -- starting IceGrid registry
	icegridregistry --Ice.Config=$(REGISTRY_CFG) &

	@echo -- waiting registry to start...
	@while ! ss -ltnH 2>/dev/null | grep -q ':$(PORT)'; do sleep 1; done

	@echo -- ok

#Parar Registry + Nodos
stop-grid:
	@for node in $(NODES); do \
		$(call ig_admin, node shutdown $$node); \
	done
	-killall icegridnode icegridregistry
	@echo -- grid stopped

#Arrancar nodo local server
start-node-server: /tmp/icedata/node-server /tmp/icedata/registry
	icegridnode --Ice.Config=node-server.config & \

#Arrancar nodo local render
start-node-render: /tmp/icedata/node-render /tmp/icedata/registry
	icegridnode --Ice.Config=node-render.config & \

#Arrancar nodo remoto server
start-node-server2: /tmp/icedata/node-server2 /tmp/icedata/registry
	icegridnode --Ice.Config=node-server2.config & \

#Arrancar nodo remoto render
start-node-render2: /tmp/icedata/node-render2 /tmp/icedata/registry
	icegridnode --Ice.Config=node-render2.config & \

#Actualizar la IP del Registry en los ficheros de configuracion de los nodos remotos
update-configs:
	@echo -- scanning $(SUBNET) for tcp/$(PORT)
	@LOCATOR_IP=$$(nmap -p $(PORT) --open $(SUBNET) 2>/dev/null | grep -oP '(?<=Nmap scan report for )[0-9.]+' | head -1); \
	if [ -z "$$LOCATOR_IP" ]; then echo "No host with tcp/$(PORT) open in $(SUBNET)"; exit 1; fi; \
	for cfg in locator.config node-server2.config node-render2.config; do \
		sed -i -E 's/(Ice.Default.Locator=.*-h )[^ ]+/\1'$$LOCATOR_IP'/' $$cfg; \
		echo "-- locator set to $$LOCATOR_IP in $$cfg"; \
	done

#Arrancar Controller
client:
	python3 media_control_v1.py --Ice.Config=locator.config
