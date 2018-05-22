CFLAGS= -g -Wall -D_BSD_SOURCE
STD= -std=c99
SRC= tcpserver2.c main.c
LIB= -pthread

all: $(SRC)
	$(CC) $(CFLAGS) $(STD) $(SRC) $(LIB) -o svr

clean:
	rm -f svr
	rm -rf *.dSYM