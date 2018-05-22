#include "tcpserver.h"

void svrLog(int level, const char* fmt, ...) {
    va_list ap;
    FILE *fp = stdout;
    
    va_start(ap, fmt);
    if (level >= 0) {
        // char *c = ".-*";
        char buf[64];
        time_t now;
        now = time(NULL);

        strftime(buf, 64, "%Y-%m-%d %H:%M:%S", gmtime(&now));
        // fprintf(fp, "%s, %c ", buf, c[level]);
        fprintf(fp, "[%s] ", buf);
        vfprintf(fp, fmt, ap);
        fprintf(fp, "\n");
        fflush(fp);
    }
    va_end(ap);
}

aeEventLoop* aeCreateEventLoop(void) {
    aeEventLoop *eventLoop = (aeEventLoop*)malloc(sizeof(aeEventLoop));
    if (eventLoop == NULL) {
        svrLog(2, "OOM aeCreateEventLoop()");
        return NULL;
    }
    eventLoop->fileEventHead = NULL;
    eventLoop->timeEventHead = NULL;
    eventLoop->timeEventNextId = 0;
    eventLoop->stop = 0;
    eventLoop->s = NULL;
    return eventLoop;
}

long long aeCreateTimeEvent(aeEventLoop *eventLoop, long long milliseconds,
    aeTimeProc *proc, void *clientData, aeEventFinalizerProc *finalizerProc) {
    long long id = eventLoop->timeEventNextId++;
    aeTimeEvent *te = (aeTimeEvent *)malloc(sizeof(aeTimeEvent));
    if (te == NULL) {
        svrLog(3, "OOM aeTimeEvent()");
        return AE_ERR;
    }
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
    if (fe == NULL) {
        svrLog(3, "OOM aeCreateFileEvent()");
        return AE_ERR;
    }
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

    // svrLog(0, "numfd=%d, maxfd=%d", numfd, maxfd);
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

void freeClient(struct aeEventLoop *eventLoop, int fd) {
    aeDeleteFileEvent(eventLoop, fd, AE_READABLE);
    aeDeleteFileEvent(eventLoop, fd, AE_WRITABLE);
    eventLoop->s->nClinetConnections--;
    close(fd);
}

void sendReplyToClient(struct aeEventLoop *eventLoop, int fd, void *clientData, int mask){
    char *reply = "OK\r\n";
    write(fd, reply, strlen(reply));
    aeDeleteFileEvent(eventLoop, fd, AE_WRITABLE);
}

void addReply(struct aeEventLoop *eventLoop, int fd) {
    aeCreateFileEvent(eventLoop, fd, AE_WRITABLE, sendReplyToClient, NULL, NULL);
}

void readQueryFromClient(struct aeEventLoop *eventLoop, int fd, void *clientData, int mask) {
    int IOBUF_LEN = 1024;
    char buf[IOBUF_LEN];
    int nread;

    nread = read(fd, buf, IOBUF_LEN);
    if(nread == -1) {
        svrLog(2, "%s", strerror(errno));
        freeClient(eventLoop, fd);
        return;
    } else if(nread == 0) {
        svrLog(1, "Client closed connection");
        freeClient(eventLoop, fd);
        return;
    }
    if(nread) {
        svrLog(1, "%s", buf);
        addReply(eventLoop, fd);
    } else {
        return;
    }
}

void acceptHandler(struct aeEventLoop *eventLoop, int fd, void *clientData, int mask) {
    int cfd, cport;
    char cip[128];
    struct sockaddr_in sa;
    unsigned int saLen;
    while(1) {
        cfd = accept(fd, (struct sockaddr *)&sa, &saLen);
        if (cfd == -1) {
            svrLog(0, "%s", strerror(errno));
            return;
        }
        break;
    }
    
    strcpy(cip, inet_ntoa(sa.sin_addr));
    cport = ntohs(sa.sin_port);
    svrLog(0, "Accepting client connection: %s:%d", cip, cport);
    eventLoop->s->nClinetConnections++;
    aeCreateFileEvent(eventLoop, cfd, AE_READABLE, readQueryFromClient, NULL, NULL);
}

int serverCron(struct aeEventLoop *eventLoop, long long id, void *clientData){
    svrLog(0, "%d connections", eventLoop->s->nClinetConnections);
    return 0;
}

void initServer(server *s, const char* host, int port) {
    if (s == NULL) return;
    int on = 1;
    struct sockaddr_in sa;

    memset(&sa, 0, sizeof(sa));
    sa.sin_family = AF_INET;
    sa.sin_port = htons(port);
    sa.sin_addr.s_addr = htonl(INADDR_ANY);
    if (host) {
        if(inet_aton(host, &sa.sin_addr) == -1) {
            svrLog(2, "errno = %d", errno); return;
        }
    }

    int sfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sfd == -1) {
        svrLog(2, "errno = %d", errno); return;
    }

    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

    if (bind(sfd, (struct sockaddr*)&sa, sizeof(sa)) == -1) {
        close(sfd);
        svrLog(2, "errno = %d", errno); return;
    }

    if (listen(sfd, QUEUE_SIZE) == -1) {
        close(sfd);
        svrLog(2, "errno = %d", errno); return;
    }

    s->fd = sfd;
    s->el = aeCreateEventLoop();
    s->el->s = s;
    aeCreateTimeEvent(s->el, 1000, serverCron, NULL, NULL);
    aeCreateFileEvent(s->el, s->fd, AE_READABLE, acceptHandler, NULL, NULL);
    svrLog(1, "Listening on %d", port);
}

void startServer(server *s) {
    if (s == NULL) return;

    while(s->el->stop == 0) {
        // saLen = sizeof(sa);
        aeProcessEvents(s->el, 0);
    }
}