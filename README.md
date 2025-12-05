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

### 4. Crear una nueva aplicación

En el menú de IceGrid:

**File → New → Application with Default Template from Registry**

### 5. Configurar la aplicación

#### Configuración básica:
- **Nombre de aplicación:** `Spotifice`
- **IcePatch2 Proxy:** `${application}.IcePatch2/server`

#### Crear nodo:
1. Click derecho en **"Nodes"** → **"New Node"**
2. **Name:** `node-Spotifice`

#### Añadir servidor IcePatch2:
1. Click derecho en `node-Spotifice` → **"New Server from Template"**
   - **Template:** `IcePatch2`
   - **Directory:** `{directorio del proyecto}`

#### Añadir servidor de medios:
1. Click derecho en `node-Spotifice` → **"New Server"**
   - **Server ID:** `media-server1`
   - **Path to Executable:** `./media_server.py`
   - **Working Directory:** `${application.distrib}`

#### Añadir servidor de renderizado:
1. Click derecho en `node-Spotifice` → **"New Server"**
   - **Server ID:** `media-render1`
   - **Path to Executable:** `./media_render.py`
   - **Working Directory:** `${application.distrib}`

### 6. Configurar adaptadores

#### Para media-server1:
Navegar a: **Spotifice → Nodes → node_Spotifice → media-server1**
- Click derecho → **"New Adapter"**
- **Adapter Name:** `MediaServerAdapter`

#### Para media-render1:
Navegar a: **Spotifice → Nodes → node_Spotifice → media-render1**
- Click derecho → **"New Adapter"**
- **Adapter Name:** `MediaRenderAdapter`

### 7. Guardar en el registry

En IceGrid: **Save to registry** (los servidores pueden reiniciarse)

### 8. Calcular parches

En el directorio del proyecto:

```bash
icepatch2calc ./
```

### 9. Iniciar los servidores

En la vista de **Live Deployment**:

1. **Tools → Application → Patch Distribution**
2. Click derecho en `node_Spotifice` → **"Start All Servers"**

### 10. Ejecutar el control de medios

En el directorio del proyecto:

```bash
python3 media_control_v1.py --Ice.Config=locator.config
```


