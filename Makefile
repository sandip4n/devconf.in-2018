CC = gcc
CFLAGS = -Wall -O0 -g

SRCS = demo-2-workload.c demo-3-workload.c
BINS = $(basename $(SRCS))

all: $(BINS)

$(BINS): %: $(SRCS)
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -f $(BINS)