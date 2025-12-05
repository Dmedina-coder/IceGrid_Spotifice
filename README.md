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
1º

$ make start-grid

2º

$ icegridgui

3º

icegrid -->
    "Log int an IceGrid Registry"
    "New Connection"
    "Direct Connection"
    "Connect to a Master Registry"
    Aceptar Endpoint descubierto
    Credenciales "user@pass"

4º

icegrid -->
    "File">
    "New">
    "Application with Default Template from Registry"

5º

icegrid>New App
    "Spotifice">IcePatch2 Proxy>"${application}.IcePatch2/server"
    "Nodes">btn_der>"New Node">Name>"node-Sopotifice"
    "node-Spotifice">btn_der"New Server from Template">
        Template>"IcePatch2"
        directory>{directorio del proyecto}
    "node-Spotifice">btn_der>"New Server"
        Server ID>"media-server1"
        Path to Executable>"./media_server.py"
        Working Directory>"${application.distrib}
    "node-Spotifice">btn_der>"New Server"
        Server ID>"media-render1"
        Path to Executable>"./media_render.py"
        Working Directory>"${application.distrib}

6º    

icegrid>Spotifice>Nodes>node_Spotifice>media-server1
    btn_der>"New Adapter"
        AdapterName>"MediaServerAdapter"
icegrid>Spotifice>Nodes>node_Spotifice>media-render1
    btn_der>"New Adapter"
        AdapterName>"MediaRenderAdapter"

7º

icegrid>Save to registry (server may restart)

8º

En el directorio del proyecto
    $ icepatch2calc ./

9º

icegrid>Live Deployment
    Tools>Application>Patch Distribution
    node_Spotifice>btn_der>Start All Servers

10º

En el directorio del proyecto
    $ python3 media_control_v1.py --Ice.Config=locator.config


