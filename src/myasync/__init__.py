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

import concurrent.futures
import multiprocessing
import threading
import time
from collections.abc import Callable, Generator
from typing import TypeVar, cast

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

Awaitable = Coroutine[T] | AbstractTask[T]


def create_loop() -> EventLoop:
    return EventLoop(SelectSelector())


loop = create_loop()


def sleep(seconds: float = 0) -> Coroutine[None]:
    start_time = time.time()

    while start_time + seconds > time.time():
        yield None


def create_task(coro: Coroutine[T]) -> TaskProxy[T]:
    coro_task = Task(coro)
    loop.attach_task(coro_task)
    return TaskProxy(coro_task)


def gather(*awaitables: Awaitable[T]) -> TaskProxy[None]:
    tasks = []
    for awaitable in awaitables:
        task = awaitable if isinstance(awaitable, AbstractTask) else create_task(awaitable)
        tasks.append(task)

    def gather_coro() -> Coroutine[None]:
        for task in tasks:
            yield from task

        return None

    return create_task(gather_coro())


def run(coro_or_task: Awaitable[T]) -> None:
    task = Task(coro_or_task) if not isinstance(coro_or_task, AbstractTask) else coro_or_task
    loop.attach_task(task)
    loop.run()


def run_callable_in_thread(callable_: Callable[[], T]) -> Coroutine[T]:
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

    thread.join()

    result = cast(T, result)

    return result


def run_awaitable_in_thread(awaitable: Awaitable[T]) -> Coroutine[T]:
    task_ = awaitable if isinstance(awaitable, AbstractTask) else Task(awaitable)
    event = threading.Event()
    thread_loop = create_loop()

    def thread_task() -> None:
        thread_loop.attach_task(task_)
        thread_loop.run()
        event.set()

    thread = threading.Thread(target=thread_task)
    thread.start()

    while not event.is_set():
        yield None

    thread.join()

    return cast(T, task_.result)


def run_in_thread(unit: Callable[[], T] | Awaitable[T]) -> Coroutine[T]:
    if callable(unit):
        return run_callable_in_thread(unit)

    if isinstance(unit, AbstractTask | Generator):
        return run_awaitable_in_thread(unit)

    raise NotImplementedError(unit)
