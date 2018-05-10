Samples from https://ruslanspivak.com/lsbaws-part1/

## C
Implementations in C code is also available.
```
make
./svr locahost 8080
```

There're two models being used:
1. fork-exec (close fd)
2. pthread (avoid race condition for fd)
3. IO Multiplexing (developping)

IO Multiplexing is considerably more complex than 1 and 2.