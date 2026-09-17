import pygame as p


class AudioManager:

    def __init__(self):

        self.music_volume = 0.7
        self.sfx_volume = 0.8

    def play_music(
        self,
        path
    ):

        p.mixer.music.load(
            path
        )

        p.mixer.music.set_volume(
            self.music_volume
        )

        p.mixer.music.play(
            -1
        )

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