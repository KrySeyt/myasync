__all__ = (
    "gather",
    "create_task",
    "sleep",
    "run",
    "Lock",
    "Coroutine",
    "EventLoop",
    "AbstractTask",
    "Task",
    "TaskProxy",
    "IOType",
    "Await",
    "Event",
    "send",
    "recv",
)

import multiprocessing
import threading
import time
from typing import TypeVar, Callable, cast

from myasync.events import Event
from myasync.locks import Lock
from myasync.loop import (
    AbstractTask,
    Await,
    Coroutine,
    EventLoop,
    IOType,
)
from myasync.selectors import SelectSelector
from myasync.sockets import (
    recv,
    send,
)
from myasync.tasks import (
    Task,
    TaskProxy,
)


T = TypeVar("T")

loop = EventLoop(SelectSelector())


def sleep(seconds: float = 0) -> Coroutine[None]:
    start_time = time.time()

    while start_time + seconds > time.time():
        yield None


def create_task(coro: Coroutine[T]) -> TaskProxy[T]:
    coro_task = Task(coro)
    loop.attach_task(coro_task)
    return TaskProxy(coro_task)


def gather(*awaitables: Coroutine[T] | AbstractTask[T]) -> TaskProxy[None]:
    tasks = []
    for awaitable in awaitables:
        task = awaitable if isinstance(awaitable, AbstractTask) else create_task(awaitable)
        tasks.append(task)

    def gather_coro() -> Coroutine[None]:
        for task in tasks:
            yield from task

        return None

    return create_task(gather_coro())


def run(coro_or_task: Coroutine[T] | AbstractTask[T]) -> None:
    task = Task(coro_or_task) if not isinstance(coro_or_task, AbstractTask) else coro_or_task
    loop.attach_task(task)
    loop.run()


def run_in_thread(callable_: Callable[[], T]) -> Coroutine[T]:
    event = threading.Event()
    result = None

    def thread_task() -> None:
        nonlocal result
        result = callable_()
        event.set()

    thread = threading.Thread(target=thread_task)
    thread.start()

    while not event.is_set():
        yield None

    result = cast(T, result)

    return result


def run_in_executor(callable_: Callable[[], T]) -> Coroutine[T]:
    event = multiprocessing.Event()
    result = None

    def process_task(event) -> None:
        nonlocal result
        result = callable_()
        event.set()

    process = multiprocessing.Process(target=process_task, args=(event,))
    process.start()

    while not event.is_set():
        yield None

    return result
