import pygame as p
from pathlib import Path

class AudioManager:

    def __init__(self):
     self.music_volume = 0.7
     self.sfx_volume = 0.8

    # Asset directories
     self.game_dir = Path(__file__).resolve().parents[1]
     self.music_dir = self.game_dir / "Music"
     self.sfx_dir = self.game_dir / "SFX"

    # Music key -> directory and filename (without extension)
     self.music_tracks = {
        "menu": (self.music_dir, "MENU_MUSIC"),
        "crimson_drive": (self.music_dir, "MUSIC"),
    }

    # Level ID -> music key
     self.level_music = {
        "level1": "crimson_drive",
    }

    # SFX key -> directory and filename (without extension)
     self.sfx_files = {
        "jump": (self.sfx_dir, "sound1"),
    }

    # Cache loaded sounds so they can be reused
     self.sfx_cache = {}

    # Track the currently playing music
     self.current_music_path = None
    @staticmethod
    def _resolve_audio_file(directory, file_stem):
     if not directory.is_dir():
        raise FileNotFoundError(
            f"Audio directory not found: {directory}"
        )

     for file_path in directory.iterdir():
        if (
            file_path.is_file()
            and file_path.stem.casefold() == file_stem.casefold()
        ):
            return file_path

     raise FileNotFoundError(
        f"Audio file '{file_stem}' not found in {directory}"
    )
    
    def play_music(self, track_or_path):
     requested = str(track_or_path)

    # Convert a level ID into its assigned music key.
     music_key = self.level_music.get(
        requested.casefold(),
        requested
    )

    # Resolve registered music keys.
     if music_key in self.music_tracks:
        directory, file_stem = self.music_tracks[music_key]
        path = self._resolve_audio_file(directory, file_stem)
     else:
        # Backward compatibility: allow existing file-path calls.
        path = Path(requested)

        if not path.is_file():
            raise KeyError(
                f"Unknown music key or invalid audio path: {requested}"
            )

     path = path.resolve()
     resolved_path = str(path)

    # Don't restart a track that is already playing.
     if (
        self.current_music_path == resolved_path
        and p.mixer.music.get_busy()
    ):
        return

     p.mixer.music.load(resolved_path)
     p.mixer.music.set_volume(self.music_volume)
     p.mixer.music.play(-1)

     self.current_music_path = resolved_path


    def stop_music(self):

        p.mixer.music.stop()

    def set_music_volume(
        self,
        value
    ):

        self.music_volume = max(
            0.0,
            min(1.0, value)
        )

        p.mixer.music.set_volume(
            self.music_volume
        )

    def set_sfx_volume(
        self,
        value
    ):

        self.sfx_volume = max(
            0.0,
            min(1.0, value)
        )

    def play_sfx(
        self,
        sound
    ):

        sound.set_volume(
            self.sfx_volume
        )

        sound.play()


audio_manager = AudioManager()