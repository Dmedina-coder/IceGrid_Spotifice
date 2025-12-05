#!/usr/bin/env python3

import sys
import re
from time import sleep
from datetime import datetime

import Ice

Ice.loadSlice('-I{} spotifice_v1.ice'.format(Ice.getSliceDir()))
import Spotifice  # type: ignore # noqa: E402


def get_proxy(ic, property, cls):
    proxy = ic.propertyToProxy(property)

    for _ in range(5):
        try:
            proxy.ice_ping()
            break
        except Ice.ConnectionRefusedException:
            sleep(0.5)

    object = cls.checkedCast(proxy)
    if object is None:
        raise RuntimeError(f'Invalid proxy for {property}')

    return object


def main(ic):
    server = get_proxy(ic, 'MediaServer.Proxy', Spotifice.MediaServerPrx)
    render = get_proxy(ic, 'MediaRender.Proxy', Spotifice.MediaRenderPrx)

    render.bind_media_server(server)

    tracks = server.get_all_tracks()
    listas = server.get_all_playlists()

    comando = "-1"

    print("BIENVENIDO AL CONTROLADOR DE SPOTIFICE, ESCRIBE HELP PARA VER LA LISTA DE COMANDOS")

    while comando != "EXIT":
        comando = input(">> ").strip().upper()

        if comando == "HELP":
            get_help()
        elif comando == "GET_CANCIONES":
            tracks = get_tracks(server)
        elif comando == "GET_LISTAS":
            get_listas(server)
        elif comando.startswith("SET_LIST"):
            set_list(comando, listas, render)
        elif comando == "RESUME" or comando == "PLAY":
            resume(render)
        elif comando.startswith("PLAY"):
            play(comando, tracks, render)
        elif comando == "STOP":
            stop(render)
        elif comando == "PAUSE":
            pause(render)
        elif comando.startswith("GET_TRACK"):
            get_info(comando, tracks)
        elif comando.startswith("GET_LIST"):
            get_info_lista(comando, listas, server)
        elif comando == "NEXT":
            next(render)
        elif comando == "PREV":
            previous(render)
        elif comando.startswith("REPEAT"):
            repeat(comando, render)
        elif comando == "EXIT":
            print("Cerrando el controlador...")
        else:
            print("Comando inválido: escribe HELP para ver la lista de comandos")
    

def get_help():
    print("Lista de comandos:")
    print("HELP: devuelve todos los comandos que acepta el controlador")
    print("GET_CANCIONES: devuelve todas las canciones alamecenadas en el servidor")
    print("GET_LISTAS: devuelve todas las listas de reproducción alamecenadas en el servidor")
    print("GET_TRACK N: devuelve la información de la canción N de la lista")
    print("GET_LIST N: devuelve la información de la lista N")
    print("SET_LIST N: establecela lista N en el reproductor")
    print("PLAY N: reproduce la canción N de la lista")
    print("RESUME: continua con la canción cargada")
    print("STOP: para la reproducción atual, al reanudar comienza la canción de 0")
    print("PAUSE: pausa la reproducción atual, al reanudar continuara donde se quedo")
    print("NEXT: reproduce la siguiente canción de la lista")
    print("PREV: reproduce la canción anterior de la lista")
    print("REPEAT bool: establece si la canción se repite o no (TRUE/FALSE)")
    print("EXIT: cierra el controlador")

def get_tracks(server):
    print("Cargando todas las canciones...")
    tracks = server.get_all_tracks()
    i = 0
    for t in tracks:
        print(f"{i} - {t.title}")
        i += 1

    if not tracks:
        print("No tracks found.")
        return

    return tracks

def get_listas(server):
    print("Cargando todas las listas de reproducción...")
    listas = server.get_all_playlists()
    i = 0
    for t in listas:
        print(f"{i} - {t.id}")
        print(f"  - {t.name}")
        print(f"  - {t.description}")
        print(f"  - {t.owner}")
        date = timestamp_to_date(t.created_at)
        print(f"  - {date}")
        print(f"  - {t.id}")
        print(f"  - Tracks:")
        for track_id in t.track_ids:
            print(f"\t  - {track_id}")
        print("_______________________________________________________________________________________")
        i += 1

    if not listas:
        print("No listas found.")
        return

    return listas

def play(mensaje, tracks, render):
    try:
        idx = extract_index_from_message(mensaje)
    except ValueError:
        print("Comando inválido: escribe HELP para ver la lista de comandos")
        return

    if idx < 0 or idx >= len(tracks):
        print("Canción inválida: escribe HELP para ver la lista de comandos")
        return

    render.stop()
    render.load_track(tracks[idx].id)
    render.play()

def pause(render):
    render.pause()

def resume(render):
    render.play()

def stop(render):
    render.stop()

def next(render):
    render.next()

def previous(render):
    render.previous()

def repeat(mensaje, render):
    render.set_repeat(True if "TRUE" in mensaje else False)

def get_info(mensaje, tracks):
    try:
        idx = extract_index_from_message(mensaje)
    except ValueError:
        print("Comando inválido: escribe HELP para ver la lista de comandos")
        return

    if idx < 0 or idx >= len(tracks):
        print("Canción inválida: escribe HELP para ver la lista de comandos")
        return

    print(f"Requesting info for track {tracks[{idx}].id}")

def set_list(mensaje, listas, render):
    try:
        idx = extract_index_from_message(mensaje)
    except ValueError:
        print("Comando inválido: escribe HELP para ver la lista de comandos")
        return

    if idx < 0 or idx >= len(listas):
        print("Lista inválida: escribe HELP para ver la lista de comandos")
        return

    info = listas[idx]

    render.stop()
    render.load_playlist(info.id)
    print(f"Lista {info.name} cargada en el reproductor.")

def sign_in(server, render):
    print("Intorduce tu usuario")
    input_user = input(">> ").strip()
    print("Intorduce tu contraseña")
    input_pass = input(">> ").strip()

    stream_manager = server.authenticate(render, "user", "secret")

    render.bind_media_server(server, stream_manager)
    render.stop()

    print(f"Usuario {input_user} autenticado correctamente.")

def get_info_lista(mensaje, listas, server):
    try:
        idx = extract_index_from_message(mensaje)
    except ValueError:
        print("Comando inválido: escribe HELP para ver la lista de comandos")
        return

    if idx < 0 or idx >= len(listas):
        print("Canción inválida: escribe HELP para ver la lista de comandos")
        return

    info = listas[idx]

    server.get_playlist(info.id)

    print(f"  - {info.id}")
    print(f"  - {info.name}")
    print(f"  - {info.description}")
    print(f"  - {info.owner}")
    date = timestamp_to_date(info.created_at)
    print(f"  - {date}")
    print(f"  - {info.id}")
    print(f"  - Tracks:")
    for track_id in info.track_ids:
        print(f"\t  - {track_id}")

def extract_index_from_message(msg):
    msg = msg.strip()
    m = re.search(r'(\d+)(?!.*\d)', msg)  # último número en el texto
    if not m:
        raise ValueError()

    n = int(m.group(1))

    return n

def timestamp_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%d-%m-%Y')

if __name__ == '__main__':

    with Ice.initialize(sys.argv) as communicator:
        main(communicator)
