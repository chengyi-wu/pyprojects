#include "tcpserver.h"

int main(int argc, char* argv[]) {
    if(argc < 2) exit(-1);

    server s;
    initServer(&s, argv[1], atoi(argv[2]));
    
    startServer(&s);
    exit(0);
}