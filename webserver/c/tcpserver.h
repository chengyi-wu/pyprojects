#ifndef __TCP_SERVER_H
#define __TCP_SERVER_H

#include <stdlib.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <pthread.h>
// #include <wchar.h>
#include <stdarg.h>

#define QUEUE_SIZE 64
#define AE_ERR -1
#define AE_OK 0

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

int aeProcessEvents(aeEventLoop *eventLoop, int flags);

int serverCron(struct aeEventLoop *eventLoop, long long id, void *clientData);

int initServer(const char* host, int port);

void startServer(int serversocket);

void svrLog(int level, const char* fmt, ...);

#endif // __TCP_SERVER_H