from pygame.constants import KEYDOWN, KEYUP, K_LCTRL, K_RCTRL, K_LALT, K_RALT, K_RETURN, K_KP_ENTER, K_KP_PERIOD
from pygame.constants import K_PERIOD, K_LSHIFT, K_RSHIFT
from pygame.event import Event
from time import time


class Input:
    # Key statuses
    NOT_PRESSED = 0
    DOWN = 1
    HOLD = 2
    UP = 3

    # Keys
    K_MENU = 1073741925
    K_HOMEPAGE = 1073742093
    K_EMAIL = 1073742089
    K_MOVE_LEFT = 1073742094
    K_MOVE_RIGHT = 1073742095
    K_PLAY = 1073742085
    K_STOP = 1073742084
    K_VOLUME_UP = 1073741952
    K_VOLUME_DOWN = 1073741953
    K_KP_RETURN = K_KP_ENTER
    K_KP_DOT = K_KP_PERIOD
    K_TILDA = 126
    K_PIPE = 124
    K_DOT = K_PERIOD

    # Generalizing keys
    GK_CTRL = 'CTRL'
    GK_ALT = 'ALT'
    GK_SHIFT = 'SHIFT'
    GK_ENTER = 'ENTER'

    # Hold duration
    FIRST_HOLD_DURATION = 0.5
    HOLD_DURATION = 0.1

    def __init__(self):
        global _active_input
        _active_input = self

        self._keys_data = {}
        self._generalized_keys = {}

        self.generalize_keys(Input.GK_CTRL, K_LCTRL, K_RCTRL)
        self.generalize_keys(Input.GK_ALT, K_LALT, K_RALT)
        self.generalize_keys(Input.GK_SHIFT, K_LSHIFT, K_RSHIFT)
        self.generalize_keys(Input.GK_ENTER, K_RETURN, K_KP_ENTER)

    def __get_time(self, key: int | str) -> float | int:
        if isinstance(key, int):
            return self._keys_data[key][1]

        return max(tuple(self._keys_data[_key][1] for _key in self._generalized_keys[key]))

    def __is_hold_first_time(self, key: int | str):
        if isinstance(key, int):
            return self._keys_data[key][2]

        return bool(sum(tuple(self._keys_data[_key][2] for _key in self._generalized_keys[key])))

    def reset_data(self, key: int):
        """
        Reset data for specified key, but if key is not exists, data for that key will be added automatically
        :param key: just a key
        """
        self._keys_data[key] = [Input.NOT_PRESSED, -1, True]

    def generalize_keys(self, name: str, *keys: int | str):
        """
        The function let add a generalized key, that is, group several keys as one, and then get the most up-to-date
        data among the specified keys by the specified name

        Example: by default, the added generic key `Input.GK_CTRL` when calling the `get_status` function will return
        `Input.HOLD` if `pygame.K_LCTRL` or `pygame.K_RCTRL` have the status `Input.HOLD`, and if `pygame.K_LCTRL` has
        the status `Input.HOLD`, and pygame.K_RCTRL has the status `Input.UP`, then the resulting the status for
        `Input.GK_CTRL` will be `Input.UP`
        :param name: new generic key name
        :param keys: generic keys or just keys
        """
        self._generalized_keys[name] = ()

        for key in keys:
            if isinstance(key, int):
                self._generalized_keys[name] = *self._generalized_keys[name], key
                continue

            self._generalized_keys[name] = *self._generalized_keys[name], self._generalized_keys[key]

    def try_start_observing(self, key: int | str):
        """
        The function allows you to add a key to the internal list of observables (as a result, it includes only simple
        keys, in the case of generalized keys, they are divided into simple ones)
        :param key: generic key or just key
        """
        if isinstance(key, int):
            if key not in self._keys_data:
                self.reset_data(key)

            return

        for _key in self._generalized_keys[key]:
            if _key not in self._keys_data:
                self.reset_data(_key)

    def get_status(self, key: int | str) -> int:
        """
        Get the up-to-date key status
        :return: `Input.NOT_PRESSED` or `Input.DOWN` or `Input.HOLD` or `Input.UP`
        """
        self.try_start_observing(key)

        if isinstance(key, int):
            return self._keys_data[key][0]

        return max(tuple(self._keys_data[_key][0] for _key in self._generalized_keys[key]))

    def is_not_pressed(self, key: int | str):
        """
        Checks if the specified key is not pressed
        :param key: generic key or just key
        """
        return self.get_status(key) == Input.NOT_PRESSED

    def is_down(self, key: int | str):
        """
        Checks if the specified key is down
        :param key: generic key or just key
        """
        return self.get_status(key) == Input.DOWN

    def is_hold(self, key: int | str):
        """
        Checks if the specified key is hold
        :param key: generic key or just key
        """
        return self.get_status(key) == Input.HOLD

    def is_up(self, key: int | str):
        """
        Checks if the specified key is up
        :param key: generic key or just key
        """
        return self.get_status(key) == Input.UP

    def is_applying(self, key: int | str, reset_data=True):
        """
        Checks if the specified key is up or hold for first 0.5s and after that every 0.1s
        :param key: generic key or just key
        :param reset_data: if true, the timer will reset after the time expires
        """
        self.try_start_observing(key)

        current_time = time()
        dt = current_time - self.__get_time(key)
        is_hold_first_time = self.__is_hold_first_time(key)
        hold_duration = Input.FIRST_HOLD_DURATION if is_hold_first_time else Input.HOLD_DURATION

        if self.is_up(key) and dt < hold_duration and is_hold_first_time:
            return True

        if self.is_hold(key) and dt >= hold_duration:
            if isinstance(key, int):
                if reset_data:
                    self._keys_data[key][1:] = [current_time, False]

                return True

            for _key in self._generalized_keys[key]:
                if reset_data:
                    self._keys_data[_key][1:] = [current_time, False]

            return True

        return False

    def any_is_not_pressed(self, *keys: int | str):
        """
        Checks if any of specified keys is not pressed
        :param keys: generic keys or just keys
        """
        for key in keys:
            if self.get_status(key) == Input.NOT_PRESSED:
                return True

        return False

    def any_is_down(self, *keys: int | str):
        """
        Checks if any of specified keys is down
        :param keys: generic keys or just keys
        """
        for key in keys:
            if self.get_status(key) == Input.DOWN:
                return True

        return False

    def any_is_hold(self, *keys: int | str):
        """
        Checks if any of specified keys is hold
        :param keys: generic keys or just keys
        """
        for key in keys:
            if self.get_status(key) == Input.HOLD:
                return True

        return False

    def any_is_up(self, *keys: int | str):
        """
        Checks if any of specified keys is up
        :param keys: generic keys or just keys
        """
        for key in keys:
            if self.get_status(key) == Input.UP:
                return True

        return False

    def any_is_applying(self, *keys: int | str, reset_data=True):
        """
        Checks if any of specified keys is up or hold for first 0.5s and after that every 0.1s
        :param keys: generic keys or just keys
        :param reset_data: if true, the timer will reset after the time expires for key for which this condition was met
        """
        for key in keys:
            if self.is_applying(key, reset_data):
                return True

        return False

    def process_event(self, e: Event):
        if e.type == KEYDOWN and e.key in self._keys_data:
            self._keys_data[e.key][0] = Input.DOWN
        elif e.type == KEYUP and e.key in self._keys_data:
            self._keys_data[e.key][0] = Input.UP

    def flip(self):
        for key in self._keys_data:
            if self._keys_data[key][0] == Input.DOWN:
                self._keys_data[key][:-1] = [Input.HOLD, time()]
            elif self._keys_data[key][0] == Input.UP:
                self.reset_data(key)


_active_input: Input | None = None


def get_input():
    return _active_input


__all__ = 'Input', 'get_input'
