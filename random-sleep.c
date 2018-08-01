/*
 * Copyright 2018 Sandipan Das, IBM Corporation
 *
 * This will sleep for random intervals and during
 * this time will be moved out of the CPU. This can
 * be traced using the bcc cpudist script.
 *
 */

#include <time.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

#define MIN_SECS    1
#define MAX_SECS    5

int main(int argc, char **argv)
{
    unsigned int delay;
    int i;

    /* Setup seed value */
    srand(time(NULL));

    for (i = 0; i < INT32_MAX; ++i) {
        /* Compute a randon value between MIN_SECS and MAX_SECS */
        delay = rand() % (MAX_SECS - MIN_SECS) + MIN_SECS;
        printf("sleeping for %u seconds...\n", delay);

        /* Sleep for anytime between MIN_SECS and MAX_SECONDS seconds */
        sleep(delay);
    }

    return EXIT_SUCCESS;
}
