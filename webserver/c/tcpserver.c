#include "tcpserver.h"

static void PRINTERR(int code) {
    switch(code) {
        default:
            fprintf(stderr, "code=%d\n", errno);
    }
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
            PRINTERR(errno); return AE_ERR;
        }
    }

    int sfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sfd == -1) {
        PRINTERR(errno); return AE_ERR;
    }

    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));

    if (bind(sfd, (struct sockaddr*)&sa, sizeof(sa)) == -1) {
        close(sfd);
        PRINTERR(errno); return AE_ERR;
    }

    if (listen(sfd, QUEUE_SIZE) == -1) {
        close(sfd);
        PRINTERR(errno); return AE_ERR;
    }

    fprintf(stderr, "Listening on %d\n", port);
    
    return sfd;
}

void startServer(int serversocket) {
    if (serversocket == AE_ERR) return;
    // int fd;
    struct sockaddr_in sa;
    unsigned int saLen;

    for(;;) {
        saLen = sizeof(sa);
        int* fd = malloc(sizeof(int)); // avoid race condition
        *fd = accept(serversocket, (struct sockaddr *)&sa, &saLen);
        if (*fd == -1) {
            PRINTERR(errno); return;
        }
        /* fork-exec model */
        // int pid = fork();
        // if (pid == 0) {
        //     close(serversocket);
        //     handle_one_request(fd, (struct sockaddr *)&sa);
        //     return;
        // } else {
        //     fprintf(stderr, "fork() pid=%d, fd=%d\n", pid, fd);
        //     close(fd);
        // }
        /* pthread */
        fprintf(stderr, "client address = [%s:%d] fd=%d\n", inet_ntoa(sa.sin_addr), sa.sin_port, *fd);
        pthread_t tid;
        pthread_create(&tid, NULL, handle_request, fd);
    }
    close(serversocket);
}

void handle_one_request(int fd, const struct sockaddr* sa) {
    int size = 1024;
    char buf[size];
    memset(buf, 0, size);
    read(fd, buf, size);
    fprintf(stderr, "%s\n", buf);

    // char* response = "HTTP/1.1 200 OK\r\n\r\n<h1>+OK</h1>\r\n";
    char* response = "+OK";

    write(fd, response, strlen(response));

    close(fd);
}

void* handle_request(void* arg) {
    int fd = *(int *)arg;
    pthread_detach(pthread_self()); // marks itself for deletion.
    free(arg);
    handle_one_request(fd, NULL);
    return NULL;
}