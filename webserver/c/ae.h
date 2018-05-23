#ifndef __AE_H__
#define __AE_H__

#include <stdlib.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/types.h>

#define AE_ERR -1
#define AE_OK 0

#define AE_READABLE 1
#define AE_WRITABLE 2
#define AE_EXCEPTION 4

struct aeEventLoop;

typedef void aeFileProc(struct aeEventLoop *eventLoop, int fd, void *clientData, int mask);
typedef int aeTimeProc(struct aeEventLoop *eventLoop, long long id, void *clientData);
typedef void aeEventFinalizerProc(struct aeEventLoop *aeEventLoop, void *clientData);

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

aeEventLoop* aeCreateEventLoop(void);

long long aeCreateTimeEvent(aeEventLoop *eventLoop, long long milliseconds,
    aeTimeProc *proc, void *clientData, aeEventFinalizerProc *finalizerProc);
int aeCreateFileEvent(aeEventLoop *eventLoop, int fd, int mask,
    aeFileProc *proc, void *clientData, aeEventFinalizerProc *finalizerProc);

void aeDeleteFileEvent(aeEventLoop *eventLoop, int fd, int mask);

int aeProcessEvents(aeEventLoop *eventLoop, int flags);

#endif // __AE_H__