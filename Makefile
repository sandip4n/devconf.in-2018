# Copyright 2018 Sandipan Das, IBM Corporation
# A simple Makefile to build the workloads
#

CC = gcc
CFLAGS = -Wall -O0 -g

SRCS = random-prefix.c busy-loop.c
BINS = $(basename $(SRCS))

all: $(BINS)

$(BINS): %: $(SRCS)
	$(CC) $(CFLAGS) $@.c -o $@

clean:
	rm -f $(BINS)
