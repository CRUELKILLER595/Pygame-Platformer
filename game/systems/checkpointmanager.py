class CheckpointManager:

    def __init__(
        self,
        start_position=None
    ):

        self.start_position = start_position
        self.active_checkpoint = None

    def set_start_position(
        self,
        position
    ):

        self.start_position = position

    def activate_checkpoint(
        self,
        checkpoint
    ):

        self.active_checkpoint = checkpoint
        checkpoint.activate()

    def get_respawn_position(
        self,
        player
    ):

        if self.active_checkpoint is None:

            if self.start_position is None:

                return player.rect.topleft

            x, y = self.start_position

        else:

            x = self.active_checkpoint.rect.centerx
            y = self.active_checkpoint.rect.bottom

        return (
            x - player.rect.width // 2,
            y - player.rect.height
        )

    def reset(self):

        self.active_checkpoint = None