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

### 1. Iniciar IceGrid

```bash
make start-grid
```

### 2. Abrir la interfaz gráfica de IceGrid

```bash
icegridgui
```

### 3. Conectar con el Registry

En la interfaz de IceGrid:

1. Seleccionar **"Log into an IceGrid Registry"**
2. Elegir **"New Connection"**
3. Seleccionar **"Direct Connection"**
4. Elegir **"Connect to a Master Registry"**
5. Aceptar el endpoint descubierto
6. Introducir credenciales: `user@pass`

### 4. Importar XML de la aplicación

En el menú de IceGrid:

1. **File → Open → Application from file**
2. Abrir **Spotificeapp-py.xml**

### 5. Guardar en el registry

En IceGrid: **Save to registry** (los servidores pueden reiniciarse)

### 6. Calcular parches

En el directorio del proyecto:

```bash
icepatch2calc ./
```

### 7. Iniciar los servidores

En la vista de **Live Deployment**:

1. **Tools → Application → Patch Distribution**
2. Click derecho en `node-server` → **"Start All Servers"**
3. Click derecho en `node-render` → **"Start All Servers"**

### 8. Ejecutar el control de medios

En el directorio del proyecto:

```bash
python3 media_control_v1.py --Ice.Config=locator.config
```


