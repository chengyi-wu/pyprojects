CFLAGS= -g -Wall -D_BSD_SOURCE
STD= -std=c99
SRC= ae.c cServer.c
TARGET= cSrv

all: $(SRC)
	$(CC) $(CFLAGS) $(STD) $(SRC)  -o $(TARGET)

clean:
	rm -f $(TARGET)
	rm -rf *.dSYM