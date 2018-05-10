CFLAGS= -g -Wall
STD= -std=c99
SRC= tcpserver.c main.c
LIB= -pthread

all: $(SRC)
	$(CC) $(CFLAGS) $(STD) $(SRC) $(LIB) -o svr

clean:
	rm -f svr
	rm -rf *.dSYM