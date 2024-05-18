# MyAsync
My simple implementation of asynchronous in Python

# Setup
- Copy repo
```shell
git clone git@github.com:KrySeyt/MyAsync.gitПрпо
```

- Create venv
```shell
python -m venv .venv 
```

- Activate venv
```shell
. ./.venv/bin/activate 
```

- Install `myasync`
```shell
pip install ./MyAsync
```

# Run example
- Install `myasync` with example
```shell
pip install ./MyAsync\[example]
```

- Run example server
```shell
python -m example_server &
```

- Run example client
```shell
python -m example_client 
```

# How to use
- `Await` - socket with expected I/O type. Yield it from `Coroutine`
- If `Coroutine` are not ready and it should be called later just `yield None` from coro. `sleep` and `Lock` works this way
- Await `Coroutine` and `Task` with `yield from`

```python
import time
import socket

from myasync import Coroutine, Await, IOType, gather, run

def send_request() -> Coroutine[str]:
    """
    Example function that requires await socket
    """
    
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

    yield from gather(
        send_request(),
        send_request(),
        send_request(),
        send_request(),
    )

    end = time.time()
    print(end - start)


if __name__ == "__main__":
    run(main())
```
