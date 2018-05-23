#include "ae.h"

aeEventLoop* aeCreateEventLoop(void) {
    aeEventLoop *eventLoop = (aeEventLoop*)malloc(sizeof(aeEventLoop));
    if (eventLoop == NULL) return NULL;
    eventLoop->fileEventHead = NULL;
    eventLoop->timeEventHead = NULL;
    eventLoop->timeEventNextId = 0;
    eventLoop->stop = 0;
    // eventLoop->s = NULL;
    return eventLoop;
}

long long aeCreateTimeEvent(aeEventLoop *eventLoop, long long milliseconds,
    aeTimeProc *proc, void *clientData, aeEventFinalizerProc *finalizerProc) {
    long long id = eventLoop->timeEventNextId++;
    aeTimeEvent *te = (aeTimeEvent *)malloc(sizeof(aeTimeEvent));
    if (te == NULL) return AE_ERR;
    te->timeProc = proc;
    te->finalizerProc = finalizerProc;
    te->clientData = clientData;
    te->next = eventLoop->timeEventHead;
    eventLoop->timeEventHead = te;

    return id;
}

int aeCreateFileEvent(aeEventLoop *eventLoop, int fd, int mask,
    aeFileProc *proc, void *clientData, aeEventFinalizerProc *finalizerProc) {
    aeFileEvent *fe = (aeFileEvent *)malloc(sizeof(aeFileEvent));
    if (fe == NULL) return AE_ERR;
    fe->fd = fd;
    fe->mask = mask;
    fe->fileProc = proc;
    fe->finalizerProc = finalizerProc;
    fe->clientData = clientData;
    fe->next = eventLoop->fileEventHead;
    eventLoop->fileEventHead = fe;

    return AE_OK;
}

void aeDeleteFileEvent(aeEventLoop *eventLoop, int fd, int mask) {
    aeFileEvent *fe, *prev = NULL;
    fe = eventLoop->fileEventHead;
    while(fe) {
        if(fe->fd == fd && fe->mask == mask) {
            if (prev == NULL) eventLoop->fileEventHead = fe->next;
            else prev->next = fe->next;
            if (fe->finalizerProc) fe->finalizerProc(eventLoop, fe->clientData);
            free(fe);
            return;
        }
        prev = fe;
        fe = fe->next;
    }
}

int aeProcessEvents(aeEventLoop *eventLoop, int flags){
    int retval;
    int numfd = 0;
    int maxfd = 0;

    aeFileEvent *fe = eventLoop->fileEventHead;

    fd_set rfds, wfds, efds;

    FD_ZERO(&rfds);
    FD_ZERO(&wfds);
    FD_ZERO(&efds);

    while(fe) {
        if(fe->mask & AE_READABLE) FD_SET(fe->fd, &rfds);
        if(fe->mask & AE_WRITABLE) FD_SET(fe->fd, &wfds);
        if(fe->mask & AE_EXCEPTION) FD_SET(fe->fd, &efds);
        if (maxfd < fe->fd) maxfd = fe->fd;
        numfd++;
        fe = fe->next;
    }

    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 0;

    retval = select(maxfd + 1, &rfds, &wfds, &efds, &tv);
    if (retval > 0) {
        fe = eventLoop->fileEventHead;
        while(fe != NULL) {
            int fd = (int) fe->fd;

            if ((fe->mask & AE_READABLE && FD_ISSET(fd, &rfds)) ||
                (fe->mask & AE_WRITABLE && FD_ISSET(fd, &wfds)) ||
                (fe->mask & AE_EXCEPTION && FD_ISSET(fd, &efds)))
            {
                int mask = 0;

                if (fe->mask & AE_READABLE && FD_ISSET(fd, &rfds))
                    mask |= AE_READABLE;
                if (fe->mask & AE_WRITABLE && FD_ISSET(fd, &wfds))
                    mask |= AE_WRITABLE;
                if (fe->mask & AE_EXCEPTION && FD_ISSET(fd, &efds))
                    mask |= AE_EXCEPTION;
                fe->fileProc(eventLoop, fe->fd, fe->clientData, mask);
                fe = eventLoop->fileEventHead;
                FD_CLR(fd, &rfds);
                FD_CLR(fd, &wfds);
                FD_CLR(fd, &efds);
            } else {
                fe = fe->next;
            }
        }
    }

    if (eventLoop->timeEventHead != NULL) {
        aeTimeEvent *te = eventLoop->timeEventHead;
        while (te) {
            te->timeProc(eventLoop, 1000, NULL);
            te = te->next;
        }
    }

    return 0;
}