#include "ae.h"

#include <arpa/inet.h>
#include <errno.h>
#include <string.h>
#include <stdarg.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>

#define QUEUE_SIZE 64

#define SERVER_DEBUG 0
#define SERVER_INFO 1
#define SERVER_ERROR 2

// Global variable
static int nconn = 0;
static int defaultLevel = SERVER_INFO;

typedef struct cServer {
    int fd;
    char host[128];
    int port;
    aeEventLoop *el;
} cServer;

typedef struct cClient {
    int fd;
    char host[128];
    char *querybuf;
    int port;
} cClient;


void serverLog(int level, const char* fmt, ...) {
    va_list ap;
    FILE *fp = stdout;
    
    va_start(ap, fmt);
    if (level >= defaultLevel) {
        char *c[] = { "DEBUG", "INFO", "ERR" };
        char buf[64];
        time_t now;
        now = time(NULL);

        strftime(buf, 64, "%Y-%m-%d %H:%M:%S", gmtime(&now));
        // fprintf(fp, "%s, %c ", buf, c[level]);
        fprintf(fp, "[%s] %s ", buf, c[level]);
        vfprintf(fp, fmt, ap);
        fprintf(fp, "\n");
        fflush(fp);
    }
    va_end(ap);
}

void freeClient(struct aeEventLoop *eventLoop, cClient* c) {
    aeDeleteFileEvent(eventLoop, c->fd, AE_READABLE);
    aeDeleteFileEvent(eventLoop, c->fd, AE_WRITABLE);
    // eventLoop->s->nConnections--;
    nconn--;
    if (c->querybuf) 
        free(c->querybuf);
    close(c->fd);
    free(c);
}

void sendReplyToClient(struct aeEventLoop *eventLoop, int fd, void *clientData, int mask){
    cClient *c = clientData;
    if (c->querybuf) {
        if (strcmp(c->querybuf, "quit") == 0) {
            serverLog(SERVER_INFO, "Client closed connection");
            freeClient(eventLoop, c);
            return;
        }
    }
    // char *reply = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: Closed\r\n\r\n<html><head><title>cServer</title></head><body><h1>Hello cServer</h1></body></html>\r\n";
    char *reply = "OK";
    int nwrite = 0;
    nwrite = write(fd, reply, strlen(reply));
    if (nwrite == -1) {
        serverLog(SERVER_ERROR, "%s", strerror(errno));
        freeClient(eventLoop, c);
        return;
    } else {
        // freeClient(eventLoop, c);
        aeDeleteFileEvent(eventLoop, fd, AE_WRITABLE);
    }
}

void addReply(struct aeEventLoop *eventLoop, cClient* c) {
    aeCreateFileEvent(eventLoop, c->fd, AE_WRITABLE, sendReplyToClient, c, NULL);
}

void readQueryFromClient(struct aeEventLoop *eventLoop, int fd, void *clientData, int mask) {
    cClient *c = clientData;
    int IOBUF_LEN = 1024;
    char buf[IOBUF_LEN];
    int nread;

    nread = read(fd, buf, IOBUF_LEN);
    if (nread == -1) {
        serverLog(SERVER_ERROR, "%s", strerror(errno));
        freeClient(eventLoop, c);
        return;
    } else if (nread == 0) {
        serverLog(SERVER_INFO, "Client closed connection");
        freeClient(eventLoop, c);
        return;
    }
    if (nread) {
        serverLog(SERVER_INFO, "[%s:%d] %s", c->host, c->port, buf);
        if (c->querybuf) 
            free(c->querybuf);
        c->querybuf = (char*)calloc(nread, sizeof(char));
        strncpy(c->querybuf, buf, nread);
        addReply(eventLoop, c);
    } else {
        return;
    }
}

void acceptHandler(struct aeEventLoop *eventLoop, int fd, void *clientData, int mask) {
    cClient *c = NULL;
    int cfd;
    struct sockaddr_in sa;
    unsigned int saLen = sizeof(sa);
    while(1) {
        cfd = accept(fd, (struct sockaddr *)&sa, &saLen);
        if (cfd == -1) {
            serverLog(SERVER_ERROR, "%s", strerror(errno));
            return;
        }
        break;
    }
    c = (cClient*)calloc(1, sizeof(cClient));
    c->querybuf = NULL;
    if (c == NULL) { close(cfd);return;}
    c->fd = cfd;
    strcpy(c->host, inet_ntoa(sa.sin_addr));
    c->port = ntohs(sa.sin_port);
    serverLog(SERVER_INFO, "Accepting client connection: %s:%d", c->host, c->port);
    // eventLoop->s->nConnections++;
    nconn++;
    aeCreateFileEvent(eventLoop, cfd, AE_READABLE, readQueryFromClient, c, NULL);
}

int serverCron(struct aeEventLoop *eventLoop, long long id, void *clientData){
    serverLog(SERVER_DEBUG, "%d connections", nconn);
    return 0;
}

void initServer(cServer *s, const char* host, int port) {
    if (s == NULL) return;
    int on = 1;
    struct sockaddr_in sa;

    memset(&sa, 0, sizeof(sa));
    sa.sin_family = AF_INET;
    sa.sin_port = htons(port);
    sa.sin_addr.s_addr = htonl(INADDR_ANY);
    if (host) {
        if(inet_aton(host, &sa.sin_addr) == -1) {
            serverLog(SERVER_ERROR, "%s", strerror(errno)); return;
        }
    }

    int sfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sfd == -1) {
        serverLog(SERVER_ERROR, "%s", strerror(errno)); return;
    }

    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

    if (bind(sfd, (struct sockaddr*)&sa, sizeof(sa)) == -1) {
        close(sfd);
        serverLog(SERVER_ERROR, "%s", strerror(errno)); return;
    }

    if (listen(sfd, QUEUE_SIZE) == -1) {
        close(sfd);
        serverLog(SERVER_ERROR, "%s", strerror(errno)); return;
    }

    s->fd = sfd;
    strcpy(s->host, host);
    s->port = port;
    s->el = aeCreateEventLoop();
    // s->el->s = s;
    // s->nConnections = 0;
    aeCreateTimeEvent(s->el, 1000, serverCron, NULL, NULL);
    aeCreateFileEvent(s->el, s->fd, AE_READABLE, acceptHandler, NULL, NULL);
    serverLog(SERVER_INFO, "Listening on %s:%d", s->host, s->port);
}

int main(int argc, char* argv[]) {
    if(argc < 2) exit(-1);

    cServer s;
    initServer(&s, argv[1], atoi(argv[2]));
    
    while(s.el->stop == 0)
        aeProcessEvents(s.el, 0);
    exit(0);
}