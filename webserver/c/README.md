# cServer - an echo server
It's a strip down version of redis's IO multiplexing. It's achieved by select() and fd_set.

- ae.c: IO multiplexing
- cServer.c: main

There're two events: **aeFileEvent** and **aeTimeEvent**. Both are implemented using singly linked list. Each holds a file descriptor which can be both read and write.

```c
typedef struct aeFileEvent {
    int fd;
    int mask;
    aeFileProc *fileProc;
    aeEventFinalizerProc *finalizerProc;
    void *clientData;
    struct aeFileEvent *next;
} aeFileEvent;

typedef struct aeTimeEvent {
    long long id;
    long when_sec;
    long when_ms;
    aeTimeProc *timeProc;
    aeEventFinalizerProc *finalizerProc;
    void *clientData;
    struct aeTimeEvent *next;
} aeTimeEvent;

typedef struct aeEventLoop {
    long long timeEventNextId;
    aeFileEvent *fileEventHead;
    aeTimeEvent *timeEventHead;
    int stop;
} aeEventLoop;

int retval = select(maxfd + 1, &rfds, &wfds, &efds, &tv);
```