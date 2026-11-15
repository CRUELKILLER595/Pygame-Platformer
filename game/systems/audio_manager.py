import sys
from pathlib import Path

import pygame as p


class AudioManager:

    def __init__(self):

        self.music_volume = 0.7
        self.sfx_volume = 0.8

        # Audio directories.
        self.game_dir = Path(__file__).resolve().parents[1]

        self.music_dir = self.game_dir / "Music"
        self.sfx_dir = self.game_dir / "SFX"

        # Registered music tracks.
        self.music_tracks = {
            "menu": (self.music_dir, "MENU_MUSIC"),
            "crimson_drive": (self.music_dir, "MUSIC"),
        }

        # Level ID -> music key.
        self.level_music = {
            "level1": "crimson_drive",
        }

        # Registered sound effects.
        self.sfx_files = {
            "jump": (self.sfx_dir, "sound1"),
        }

        # Cached sound effects.
        self.sfx_cache = {}

        # Current music state.
        self.current_music_path = None
        self.music_paused = False

    # ==========================================
    # MIXER INITIALIZATION
    # ==========================================

    @staticmethod
    def _ensure_mixer():

        if p.mixer.get_init() is not None:
            return True

        try:
            p.mixer.init()
            return True

        except p.error as error:

            print(
                "Audio mixer initialization failed:",
                error
            )

            return False

    # ==========================================
    # AUDIO FILE RESOLUTION
    # ==========================================

    @staticmethod
    def _resolve_audio_file(directory, file_stem):

        if not directory.is_dir():

            raise FileNotFoundError(
                f"Audio directory not found: {directory}"
            )

        matching_files = {
            path.suffix.lower(): path
            for path in directory.iterdir()
            if (
                path.is_file()
                and path.stem.casefold() == file_stem.casefold()
            )
        }

        if sys.platform == "emscripten":

            extension_order = (
                ".ogg",
                ".wav",
                ".mp3",
            )

        else:

            extension_order = (
                ".wav",
                ".ogg",
                ".mp3",
            )

        for extension in extension_order:

            if extension in matching_files:
                return matching_files[extension]

        raise FileNotFoundError(
            f"Audio file '{file_stem}' not found in {directory}"
        )

    @staticmethod
    def _resolve_explicit_path(requested):

        path = Path(requested)

        if sys.platform == "emscripten":

            ogg_path = path.with_suffix(".ogg")

            if ogg_path.is_file():
                path = ogg_path

        if not path.is_file():

            raise FileNotFoundError(
                f"Audio file not found: {path}"
            )

        return path.resolve()

    # ==========================================
    # PLAY MUSIC
    # ==========================================

    def play_music(self, track_or_path):

        if not self._ensure_mixer():
            return False

        requested = str(track_or_path)

        music_key = self.level_music.get(
            requested.casefold(),
            requested,
        )

        try:

            if music_key in self.music_tracks:

                directory, file_stem = self.music_tracks[music_key]

                path = self._resolve_audio_file(
                    directory,
                    file_stem,
                )

            else:

                path = self._resolve_explicit_path(
                    requested
                )

            resolved_path = str(path.resolve())

            # Same track already playing or paused.
            if self.current_music_path == resolved_path:

                if self.music_paused:

                    self.resume_music()

                    return True

                if p.mixer.music.get_busy():
                    return True

            # Replace the previous track.
            p.mixer.music.stop()

            p.mixer.music.load(resolved_path)

            p.mixer.music.set_volume(
                self.music_volume
            )

            p.mixer.music.play(-1)

            self.current_music_path = resolved_path
            self.music_paused = False

            print(
                "NOW PLAYING:",
                path.name
            )

            return True

        except (
            p.error,
            FileNotFoundError,
            KeyError,
        ) as error:

            print(
                "Could not play music:",
                error
            )

            return False

    # ==========================================
    # PAUSE MUSIC
    # ==========================================

    def pause_music(self):

        if self.current_music_path is None:
            return

        if p.mixer.get_init() is None:
            return

        if self.music_paused:
            return

        p.mixer.music.pause()

        self.music_paused = True

        print(
            "MUSIC PAUSED:",
            Path(self.current_music_path).name
        )

    # ==========================================
    # RESUME MUSIC
    # ==========================================

    def resume_music(self):

        if self.current_music_path is None:
            return

        if p.mixer.get_init() is None:
            return

        if not self.music_paused:
            return

        p.mixer.music.unpause()

        self.music_paused = False

        print(
            "MUSIC RESUMED:",
            Path(self.current_music_path).name
        )

    # ==========================================
    # STOP MUSIC
    # ==========================================

    def stop_music(self):

        if p.mixer.get_init() is not None:
            p.mixer.music.stop()

        self.current_music_path = None
        self.music_paused = False

    # ==========================================
    # VOLUME
    # ==========================================

    def set_music_volume(self, value):

        self.music_volume = max(
            0.0,
            min(1.0, float(value)),
        )

        if p.mixer.get_init() is not None:

            p.mixer.music.set_volume(
                self.music_volume
            )

    def set_sfx_volume(self, value):

        self.sfx_volume = max(
            0.0,
            min(1.0, float(value)),
        )

    # ==========================================
    # SOUND EFFECTS
    # ==========================================

    def play_sfx(self, sound_key):

        if not self._ensure_mixer():
            return False

        try:

            if sound_key not in self.sfx_files:

                raise KeyError(
                    f"Unknown sound: {sound_key}"
                )

            if sound_key not in self.sfx_cache:

                directory, file_stem = self.sfx_files[sound_key]

                sound_path = self._resolve_audio_file(
                    directory,
                    file_stem,
                )

                self.sfx_cache[sound_key] = p.mixer.Sound(
                    str(sound_path)
                )

            sound = self.sfx_cache[sound_key]

            sound.set_volume(
                self.sfx_volume
            )

            sound.play()

            return True

        except (
            p.error,
            FileNotFoundError,
            KeyError,
        ) as error:

            print(
                "Could not play sound:",
                error
            )

            return False


# Shared audio manager.
audio_manager = AudioManager()