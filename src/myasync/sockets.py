import socket

import myasync


def send(conn: socket.socket, data: bytes) -> myasync.Coroutine[None]:
    yield myasync.Await(conn, myasync.IOType.OUTPUT)
    conn.send(data)


def recv(conn: socket.socket, size: int) -> myasync.Coroutine[bytes]:
    yield myasync.Await(conn, myasync.IOType.INPUT)
    return conn.recv(size)
