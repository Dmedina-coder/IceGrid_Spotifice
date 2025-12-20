# Spotifice

This repository contains the starter code for the **Spotifice** application.
Spotifice is a distributed multimedia streaming system built with **ZeroC Ice** and **Python**.

## Requirements

To run this application, you need:

- **Python ≥ 3.10**
- **ZeroC Ice 3.7**
- All Python dependencies listed in the `DEPENDS` file
- A recent GNU/Linux distribution such as **Debian 12 (Bookworm)** or **Ubuntu 23.04** or newer

## Contents

This repository has been cloned as part of an GitHub Classroom assignment. See lab statement in the Moodle course for details.

## Download media files

The `Makefile` will download example music files:

```bash
spotifice$ make
```

## Usage

You can start the application (using `tmux`):

```bash
spotifice$ ./run.sh
```

That executes `media_server`, `media_render` and `media_control` with the proper configuration.


## Authors

Developed by the *Distributed Systems* course teachers at **UCLM-ESI**.

## Ejecución

### 1. Iniciar Registry

```bash
make start-registry
```

### 2. Crear nodos locales y remotos

En la maquina local

```bash
make start-local-nodes
```
En la maquina distribuida

```bash
make start-remote-nodes
```

### 3. Desplegar la aplicación

```bash
make deploy-app
```

### 4. Arrancamos los servidores locales y remotos

```bash
make start-servers
```

### 5. Ejecutar el control de medios

En el directorio del proyecto:

```bash
make client
```

### 6. La gestion de los nodos la podemos gestionar desde

```bash
icegridgui
```