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

int initServer(const char* host, int port) {
    int on = 1;
    struct sockaddr_in sa;

    memset(&sa, 0, sizeof(sa));
    sa.sin_family = AF_INET;
    sa.sin_port = htons(port);
    sa.sin_addr.s_addr = htonl(INADDR_ANY);
    if (host) {
        if(inet_aton(host, &sa.sin_addr) == -1) {
            svrLog(2, "errno = %d", errno); return AE_ERR;
        }
    }

    int sfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sfd == -1) {
        svrLog(2, "errno = %d", errno); return AE_ERR;
    }

    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

    if (bind(sfd, (struct sockaddr*)&sa, sizeof(sa)) == -1) {
        close(sfd);
        svrLog(2, "errno = %d", errno); return AE_ERR;
    }

    if (listen(sfd, QUEUE_SIZE) == -1) {
        close(sfd);
        svrLog(2, "errno = %d", errno); return AE_ERR;
    }

    svrLog(1, "Listening on %d", port);
    
    return sfd;
}

aeEventLoop* aeCreateEventLoop(void) {
    aeEventLoop *eventLoop = (aeEventLoop*)malloc(sizeof(aeEventLoop));
    if (eventLoop == NULL) {
        svrLog(3, "OOM aeCreateEventLoop()");
        return NULL;
    }
    eventLoop->fileEventHead = NULL;
    eventLoop->timeEventHead = NULL;
    eventLoop->timeEventNextId = 0;
    eventLoop->stop = 0;
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
    fe->fileProc = proc;
    fe->finalizerProc = finalizerProc;
    fe->clientData = clientData;
    fe->next = eventLoop->fileEventHead;
    eventLoop->fileEventHead = fe;

    return AE_OK;
}

int aeProcessEvents(aeEventLoop *eventLoop, int flags){
    fd_set rfds, wfds, efds;

    FD_ZERO(&rfds);
    FD_ZERO(&wfds);
    FD_ZERO(&efds);

    int retval;
    int numfd = 3;
    int maxfd = numfd + 1;

    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 0;

    retval = select(maxfd + 1, &rfds, &wfds, &efds, &tv);
    if (retval > 0) {

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

int serverCron(struct aeEventLoop *eventLoop, long long id, void *clientData){
    svrLog(0, "%d connections.", 0);
    return 0;
}

void startServer(int serversocket) {
    if (serversocket == AE_ERR) return;
    // int fd;
    // struct sockaddr_in sa;
    // unsigned int saLen;

    aeEventLoop *eventLoop = aeCreateEventLoop();
    aeCreateTimeEvent(eventLoop, 1000, serverCron, NULL, NULL);
    // aeCreateFileEvent(eventLoop, )
    while(eventLoop->stop == 0) {
        // saLen = sizeof(sa);
        aeProcessEvents(eventLoop, 0);
    }
    close(serversocket);
}