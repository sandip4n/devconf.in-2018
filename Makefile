# Copyright 2018 Sandipan Das, IBM Corporation
# A simple Makefile to build the workloads
#

CC = gcc
CFLAGS = -Wall -O0 -g

SRCS = demo-2-workload.c demo-3-workload.c
BINS = $(basename $(SRCS))

all: $(BINS)

$(BINS): %: $(SRCS)
	$(CC) $(CFLAGS) $@.c -o $@

clean:
	rm -f $(BINS)
