#!/usr/bin/env python3

import logging
import sys
from contextlib import contextmanager

import Ice
from Ice import identityToString as id2str

from gst_player import GstPlayer

Ice.loadSlice('-I{} spotifice_v1.ice'.format(Ice.getSliceDir()))
import Spotifice  # type: ignore # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MediaRender")


class MediaRenderI(Spotifice.MediaRender):
    def __init__(self, player):
        self.player = player
        self.server: Spotifice.MediaServerPrx = None
        self.current_track = None
        self.current_playlist = {}
        self.playlist_index = 0

        self.current_context = None

        self.status = Spotifice.PlaybackStatus()
        self.status.state = Spotifice.PlaybackState.STOPPED
        self.status.repeat = False
        self.status.current_track_id = ""

    def ensure_player_stopped(self):
        if self.player.is_playing():
            raise Spotifice.PlayerError(reason="Already playing")

    def ensure_server_bound(self):
        if not self.server:
            raise Spotifice.BadReference(reason="No MediaServer bound")

    # --- RenderConnectivity ---

    def bind_media_server(self, media_server, current=None):
        try:
            proxy = media_server.ice_timeout(500)
            proxy.ice_ping()
        except Ice.ConnectionRefusedException as e:
            raise Spotifice.BadReference(reason=f"MediaServer not reachable: {e}")

        self.server = media_server
        logger.info(f"Bound to MediaServer '{id2str(media_server.ice_getIdentity())}'")

    def unbind_media_server(self, current=None):
        self.stop(current)
        self.server = None
        logger.info("Unbound MediaServer")

    # --- ContentManager ---

    def load_track(self, track_id, current=None):
        self.ensure_server_bound()

        try:
            with self.keep_playing_state(current):
                self.current_track = self.server.get_track_info(track_id)
                self.status.current_track_id = self.current_track.title

            logger.info(f"Current track set to: {self.current_track.title}")

        except Spotifice.TrackError as e:
            logger.error(f"Error setting track: {e.reason}")
            raise

    def load_playlist(self, list_id, current=None):
        self.ensure_server_bound()

        try:
            playlist = self.server.get_playlist(list_id)
            self.current_playlist = playlist.track_ids
            logger.info(f"Current playlist set to: {playlist.name}")
            self.load_track(self.current_playlist[0], current)
            self.playlist_index = 0

        except Spotifice.PlaylistError as e:
            logger.error(f"Error setting playlist: {e.reason}")
            raise

    def get_current_track(self, current=None):
        return self.current_track

    def current_track_finished(self, current=None):
        if self.current_playlist:
            self.next(self.current_context)
        elif self.status.repeat:
            self.play(self.current_context)
        else:
            self.status.state = Spotifice.PlaybackState.STOPPED

    # --- PlaybackController ---

    def get_status(self, current=None):
        return self.status

    @contextmanager
    def keep_playing_state(self, current):
        playing = self.player.is_playing()
        if playing:
            self.stop(current)
        try:
            yield
        finally:
            if playing:
                self.play(current)

    def play(self, current=None):
        def get_chunk_hook(chunk_size):
            try:
                return self.server.get_audio_chunk(current.id, chunk_size)
            except Spotifice.IOError as e:
                logger.error(e)
            except Ice.Exception as e:
                logger.critical(e)

        assert current, "remote invocation required"

        self.current_context = current

        if self.status.state == Spotifice.PlaybackState.PAUSED:
            self.player.resume()
            self.status.state = Spotifice.PlaybackState.PLAYING
            logger.info("Resumed playback")
            return

        self.ensure_player_stopped()
        self.ensure_server_bound()

        if not self.current_track:
            raise Spotifice.TrackError(reason="No track loaded")

        try:
            self.server.open_stream(self.current_track.id, current.id)
        except Spotifice.BadIdentity as e:
            logger.error(f"Error starting stream: {e.reason}")
            raise Spotifice.StreamError(reason="Strean setup failed")

        self.player.configure(get_chunk_hook, track_exhausted_hook=self.current_track_finished)

        if not self.player.confirm_play_starts():
            raise Spotifice.PlayerError(reason="Failed to confirm playback")
        else:
            logger.info("Playing")
            self.status.state = Spotifice.PlaybackState.PLAYING


    def pause(self, current=None):
        self.player.pause()
        self.status.state = Spotifice.PlaybackState.PAUSED
        logger.info("Paused")

    def stop(self, current=None):
        if self.server and current:
            self.server.close_stream(current.id)

        if not self.player.stop():
            raise Spotifice.PlayerError(reason="Failed to confirm stop")

        self.status.state = Spotifice.PlaybackState.STOPPED
        logger.info("Stopped")

    def next(self, current=None):
        self.ensure_server_bound()

        if not self.current_playlist:
            logger.info("No playlist loaded")
            return

        playing = self.status.state        

        self.playlist_index += 1
        if self.playlist_index >= len(self.current_playlist):
            if self.status.repeat:
                self.playlist_index = 0
            else:
                self.playlist_index = len(self.current_playlist) - 1
                logger.info("End of playlist reached")
                return

        self.stop(current)

        next_track_id = self.current_playlist[self.playlist_index]
        self.load_track(next_track_id, current)

        if self.current_track:
            if playing == Spotifice.PlaybackState.PLAYING:
                self.play(current)

    def previous(self, current=None):
        self.ensure_server_bound()

        if not self.current_playlist:
            logger.info("No playlist loaded")
            return

        playing = self.status.state

        self.playlist_index -= 1
        if self.playlist_index < 0:
            self.playlist_index = 0
            logger.info("Start of playlist reached")
            return

        self.stop(current)

        prev_track_id = self.current_playlist[self.playlist_index]
        self.load_track(prev_track_id, current)

        if self.current_track:
            if playing == Spotifice.PlaybackState.PLAYING:
                self.play(current)


    def set_repeat(self, estado = False, current=None):
        self.status.repeat = estado
        logger.info(f"Set repeat to {self.status.repeat}")

def main(ic, player):
    servant = MediaRenderI(player)

    adapter = ic.createObjectAdapter("MediaRenderAdapter")
    # Usar categoría para poder identificar el servicio
    identity = Ice.Identity()
    identity.name = "render"
    identity.category = "mediaRender"
    proxy = adapter.add(servant, identity)
    logger.info(f"MediaRender (category/UUID): {proxy}")

    adapter.activate()
    ic.waitForShutdown()

    logger.info("Shutdown")

if __name__ == "__main__":
    player = GstPlayer()
    player.start()
    try:
        # IceGrid maneja los argumentos automáticamente
        with Ice.initialize(sys.argv) as communicator:
            main(communicator, player)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user.")
    finally:
        player.shutdown()
