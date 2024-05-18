import socket

from myasync.loop import Coroutine, Await, IOType


def send(conn: socket.socket, data: bytes) -> Coroutine[None]:
    yield Await(conn, IOType.OUTPUT)
    conn.send(data)


def recv(conn: socket.socket, size: int) -> Coroutine[bytes]:
    yield Await(conn, IOType.INPUT)
    return conn.recv(size)
