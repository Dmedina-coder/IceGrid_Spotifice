#!/usr/bin/env python3

import logging
import sys
import json
from datetime import datetime
from pathlib import Path

import Ice
from Ice import identityToString as id2str

Ice.loadSlice('-I{} spotifice_v1.ice'.format(Ice.getSliceDir()))
import Spotifice  # type: ignore # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MediaServer")


class StreamedFile:
    def __init__(self, track_info, media_dir):
        self.track = track_info
        filepath = media_dir / track_info.filename

        try:
            self.file = open(filepath, 'rb')
        except Exception as e:
            raise Spotifice.IOError(track_info.filename, f"Error opening media file: {e}")

    def read(self, size):
        return self.file.read(size)

    def close(self):
        try:
            if self.file:
                self.file.close()
        except Exception as e:
            logger.error(f"Error closing file for track '{self.track.id}': {e}")

    def __repr__(self):
        return f"<StreamState '{self.track.id}'>"


class MediaServerI(Spotifice.MediaServer):
    def __init__(self, media_dir, playlists_dir):
        self.media_dir = Path(media_dir)
        self.tracks = {}
        self.active_streams = {}  # media_render_id -> StreamedFile
        self.load_media()


        self.playlists_dir = Path(playlists_dir)
        self.playlists = {}
        self.load_playlist()

    def ensure_track_exists(self, track_id):
        if track_id not in self.tracks:
            raise Spotifice.TrackError(track_id, "Track not found")

    def load_media(self):
        for filepath in sorted(Path(self.media_dir).iterdir()):
            if not filepath.is_file() or filepath.suffix.lower() != ".mp3":
                continue

            self.tracks[filepath.name] = self.track_info(filepath)

        logger.info(f"Load media:  {len(self.tracks)} tracks")

    def load_playlist(self):
        for filepath in sorted(Path(self.playlists_dir).iterdir()):
            if not filepath.is_file() or filepath.suffix.lower() != ".playlist":
                continue

            self.playlists[filepath.name] = self.playlist_info(filepath, tracks=self.tracks)

        logger.info(f"Load playlist:  {len(self.playlists)} lists")

    @staticmethod
    def track_info(filepath):
        return  Spotifice.TrackInfo(
            id=filepath.name,
            title=filepath.stem,
            filename=filepath.name)

    @staticmethod
    def playlist_info(filepath, tracks):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo playlist {filepath.name}: {e}")
            return None

        pid = data.get('id', filepath.stem)
        name = data.get('name', pid)
        description = data.get('description', '')
        owner = data.get('owner', '')

        # Convertir created_at a un long (timestamp en segundos)
        created_at_str = data.get('created_at', '').replace('-', '')
        created_at = int(datetime.strptime(created_at_str, "%d%m%Y").timestamp())

        canciones = data.get('track_ids', [])

        for t in canciones:
            if t not in tracks:
                canciones.remove(t)
                logger.warning(f"Track '{t}' in playlist '{pid}' not found in media library.")

        return Spotifice.Playlist(
                id=pid,
                name=name,
                description=description,
                owner=owner,
                created_at=created_at,
                track_ids=canciones
            )      

    # ---- MusicLibrary ----
    def get_all_tracks(self, current=None):
        return list(self.tracks.values())

    def get_track_info(self, track_id, current=None):
        self.ensure_track_exists(track_id)
        return self.tracks[track_id]

    # ---- PlaylistManager ----
    def get_all_playlists(self, current=None):

        return list(self.playlists.values())

    def get_playlist(self, playlist_id, current=None):
        lista = next((p for p in self.playlists.values() if p.id == playlist_id), None)
        if not lista:
            raise Spotifice.PlaylistError(playlist_id, "Playlist not found")
        return lista
    

    # ---- StreamManager ----
    def open_stream(self, track_id, render_id, current=None):
        str_render_id = id2str(render_id)
        self.ensure_track_exists(track_id)

        if not render_id.name:
            raise Spotifice.BadIdentity(str_render_id, "Invalid render identity")

        self.active_streams[str_render_id] = StreamedFile(
            self.tracks[track_id], self.media_dir)

        logger.info("Open stream for track '{}' on render '{}'".format(
            track_id, str_render_id))

    def close_stream(self, render_id, current=None):
        str_render_id = id2str(render_id)
        if stream_state := self.active_streams.pop(str_render_id, None):
            stream_state.close()
            logger.info(f"Closed stream for render '{str_render_id}'")

    def get_audio_chunk(self, render_id, chunk_size, current=None):
        str_render_id = id2str(render_id)
        try:
            streamed_file = self.active_streams[str_render_id]
        except KeyError:
            raise Spotifice.StreamError(str_render_id, "No open stream for render")

        try:
            data = streamed_file.read(chunk_size)
            if not data:
                logger.info(f"Track exhausted: '{streamed_file.track.id}'")
                self.close_stream(render_id, current)
            return data

        except Exception as e:
            raise Spotifice.IOError(
                streamed_file.track.filename, f"Error reading file: {e}")


def main(ic):
    properties = ic.getProperties()

    media_dir = properties.getPropertyWithDefault(
        'MediaServer.Content', 'media')

    playlists_dir = properties.getPropertyWithDefault(
        'MediaServer.Playlists', 'playlists')
    
    servant = MediaServerI(Path(media_dir), Path(playlists_dir))

    adapter = ic.createObjectAdapter("MediaServerAdapter")
    proxy = adapter.add(servant, ic.stringToIdentity("mediaServer1"))
    logger.info(f"MediaServer: {proxy}")

    adapter.activate()
    ic.waitForShutdown()

    logger.info("Shutdown")


if __name__ == "__main__":
    try:
        # IceGrid maneja los argumentos automáticamente
        with Ice.initialize(sys.argv) as communicator:
            main(communicator)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user.")
