/*
 * Copyright 2018 Sandipan Das, IBM Corporation
 *
 * This will perform memory allocations, go to sleep
 * and free up the previous allocations after waking
 * up. The allocations that are yet to be free can be
 * traced using the bcc memleak script.
 *
 */

#include <time.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

#define MAX_ALLOCS    5

int main(int argc, char **argv)
{
    void *ptr[MAX_ALLOCS];
    size_t bytes;
    int i, j;

    srand(time(NULL));

    for (i = 0; i < INT32_MAX; ++i) {

        /* Allocate memory */
        for (j = 0; j < MAX_ALLOCS; ++j) {
            bytes = rand() % (INT16_MAX - 1) + 1;
            printf("allocating %lu bytes\n", bytes);
            ptr[j] = malloc(bytes);
        }

        /* Wait for a couple of seconds */
        sleep(2);

        /* Free memory */
        for (j = 0; j < MAX_ALLOCS; ++j) {
            printf("freeing %lu bytes\n", bytes);
            free(ptr[j]);
        }
    }

    return EXIT_SUCCESS;
}
