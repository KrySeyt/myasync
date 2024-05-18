import socket
import time

import myasync
from myasync import (
    Await,
    Coroutine,
    IOType,
    run,
)


def send_request() -> Coroutine[str]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 8000))
    sock.send(b"GET / HTTP/1.1\r\nHost:localhost\r\n\r\n")

    yield Await(sock, IOType.INPUT)

    sock.recv(100)
    sock.close()

    print("Task done")
    return "Done"


def main() -> Coroutine[None]:
    start = time.time()

    yield from myasync.gather(
        send_request(),
        send_request(),
        send_request(),
        send_request(),
    )

    end = time.time()
    print(f"Elapsed time: {end - start}")


if __name__ == "__main__":
    run(main())
