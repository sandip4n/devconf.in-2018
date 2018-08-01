/*
 * Copyright 2018 Sandipan Das, IBM Corporation
 *
 * This uses simple loops to make the execution
 * time of a function vary based on its arguments.
 *
 */

#include <time.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

int foo(int x)
{
    int i;

    /*
     * For different values of x, the execution
     * time of foo() will vary
     */
    if (x == 0) {
        for (i = 0; i < INT8_MAX; ++i);
    } else if (x == 1) {
        for (i = 0; i < INT16_MAX; ++i);
    } else if (x == 2) {
        for (i = 0; i < INT32_MAX; ++i);
    }

    return 0;
}

int main(int argc, char **argv)
{
    int i, x;

    /* Setup seed value */
    srand(time(NULL));

    for (i = 0; i < INT32_MAX; i++) {
        /* Pick a random value */
        x = rand() % 3;

        /* Call foo() */
        printf("call foo(%d)\n", x);
        foo(x);
    }

    return EXIT_SUCCESS;
}
