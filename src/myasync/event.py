from myasync.loop import Coroutine


class Event:
    def __init__(self) -> None:
        self._status = False

    def set(self) -> None:
        self._status = True

    def clear(self) -> None:
        self._status = False

    def wait(self) -> Coroutine[None]:
        while not self._status:
            yield None
