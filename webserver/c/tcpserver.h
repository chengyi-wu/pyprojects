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

#define QUEUE_SIZE 64
#define AENET_ERR -1

int initServer(const char* host, int port);

void startServer(int serversocket);

void handle_one_request(int fd, const struct sockaddr* sa);

void* handle_request(void *arg);

#endif 