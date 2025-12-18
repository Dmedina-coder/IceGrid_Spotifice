#!/usr/bin/make -f

define ig_admin
	icegridadmin --Ice.Config=locator.config -u user -p pass -e "$(1)"
endef

up: down
	reset
	docker-compose up --build -d --remove-orphans

down:
	docker-compose down

build_nodes: make-dir
	docker-compose up --build node-server
	docker-compose up --build node-render

logs:
	docker-compose logs -f

rm-app:
	-$(call ig_admin, application remove Spotifice)

add-app: up Spotificeapp-py.xml
	$(call ig_admin, application add Spotificeapp-py.xml)

client:
	python3 ./media_control_v1.py --Ice.Config=locator.config

client-wko:
	python3 ./media_control_v1.py --Ice.Config=locator.config

make-dir:
	mkdir -p ./icedata/node-server
	mkdir -p ./icedata/node-render

clean: down
	-$(RM) *~
