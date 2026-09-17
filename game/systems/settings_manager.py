class SettingsManager:

    def __init__(self):

        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self.brightness = 1.0

    def set_music_volume(
        self,
        value
    ):

        self.music_volume = max(
            0.0,
            min(1.0, value)
        )

    def set_sfx_volume(
        self,
        value
    ):

        self.sfx_volume = max(
            0.0,
            min(1.0, value)
        )

    def set_brightness(
        self,
        value
    ):

        self.brightness = max(
            0.0,
            min(1.0, value)
        )