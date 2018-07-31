/*
 * Copyright 2018 Sandipan Das, IBM Corporation
 *
 * This will generate random-length prefixes of a
 * string and attempt to print it with the write
 * system call.
 *
 */

#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    int i;
    char str[] = "lorem ipsum dolor sit amet", buf[64];
    size_t bytes, lbound, ubound;

    /* Setup seed */
    srand(time(NULL));

    /* Setup lower and upper bounds for bytes to copy */
    lbound = 1;
    ubound = sizeof(str) - 1;

    for (i = 0; i < INT32_MAX; i++) {
        /* Generate a random number of bytes to copy */
        bytes = rand() % (ubound - lbound + 1) + lbound;

        /* Copy bytes to buffer */
        strncpy(buf, str, bytes);
        buf[bytes] = '\0';

        /* Print buffer with a write() system call */
        write(STDOUT_FILENO, buf, bytes);

        /* Wait for a couple of seconds */
        sleep(2);
    }

    return EXIT_SUCCESS;
}
