# Copyright 2018 Sandipan Das, IBM Corporation
# A simple Makefile to build the workloads
#

CC = gcc
CFLAGS = -Wall -O0 -g

SRCS = $(wildcard *.c)
BINS = $(basename $(SRCS))

all: $(BINS)

%: %.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(BINS)
