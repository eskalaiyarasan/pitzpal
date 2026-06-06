class base_proxy:
    def __init__(self, parent_instance):
        self.parent = parent_instance

    def __getattr__(self, attr):
        return getattr(self.parent, attr)

    def __setattr__(self, attr, value):
        # If the wrapper itself has overridden this attribute, set it on the wrapper
        if attr in self.__dict__:
            self.__dict__[attr] = value
        else:
            # Otherwise, pass the value down to the inner object!
            setattr(self._delegate, attr, value)


class base_utils:
    def __init__(self, game_in):
        self.game = game_in
        self.max_index = self.game.Config.PitsPerSide * self.game.Config.Nside

    def save_to_store(self, side, seeds):
        value = self.game.Board.Store[side][str(side)]
        self.game.Board.Store[side] = {str(side): value + seeds}

    def move_to_store(self, index, side=None):
        if index >= 0 and index < self.max_index:
            if side is None:
                side = self.game.Board.Pits[index].Side
            value = self.game.Board.Pits[index].Value
            self.save_to_store(side, value)
            self.game.Board.Pits[index].Value = 0

    def get_pit_value(self, index):
        if index >= 0 and index < self.max_index:
            return self.game.Board.Pits[index].Value
        return -1

    def set_pit_value(self, index, value):
        if value < 0:
            value = 0
        if index >= 0 and index < self.max_index:
            self.game.Board.Pits[index].Value = value

    def raise_pit_value(self, index, value):
        if index >= 0 and index < self.max_index:
            old_value = self.game.Board.Pits[index].Value
            self.game.Board.Pits[index].Value = old_value + value

    def raise_pit_share(self, index, side):
        value = self.game.Board.Pits[index].Share[side][str(side)]
        self.game.Board.Pits[index].Share[side] = {str(side): value + 1}
