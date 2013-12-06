CC=gcc
CFLAGS=-O2
LDFLAGS=-lm

all: parsecoords

parsecoords: parsecoords.o kdtree.o
	$(CC) $(CFLAGS) $^ -o $@ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $<

clean:
	-$(RM) -f *.o parsecoords
