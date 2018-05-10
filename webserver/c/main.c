#include "tcpserver.h"

int main(int argc, char* argv[]) {
    if(argc < 2) exit(-1);
    
    startServer(initServer(argv[1], atoi(argv[2])));
    exit(0);
}