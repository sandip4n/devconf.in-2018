#!/usr/bin/env python
#
# Copyright 2018 Sandipan Das, IBM Corporation
#
# Trace the foo() function from the workload by attaching
# uprobes that are triggered on entry and exit. This will
# print the approximate execution time of foo() and shows
# how the value of the argument affects it.
#

from bcc import BPF
import argparse

# setup argument parsing
parser = argparse.ArgumentParser(
    description="",
    formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", "--pid", type=int,
    dest="pid", metavar="PID", help="the pid to trace")
parser.add_argument("-t", "--threshold", type=int,
    dest="threshold", metavar="THRESHOLD", help="the threshold in ns")
args = parser.parse_args()

# define BPF program
prog = """
#include <uapi/linux/ptrace.h>

DEFINE_FILTER_PID
DEFINE_THRESHOLD_LATENCY

/*
 * To preserve state across entry and exit handlers
 */
BPF_ARRAY(entry, u64, 1);
BPF_ARRAY(argument, int, 1);

int on_entry(struct pt_regs *ctx) {

    int zero = 0;

    /* Record entry time */
    u64 time = bpf_ktime_get_ns();

    /*
     * Read the first argument of
     * int foo(int x);
     */
    int x = (size_t) PT_REGS_PARM1(ctx);

    /* Read PID of current process */
    u32 pid = bpf_get_current_pid_tgid();

#ifdef FILTER_PID
    /* Check if PID matches */
    if (pid != FILTER_PID) {
        return 0;
    }
#endif

    /* Write entry time and argument to maps */
    entry.update(&zero, &time);
    argument.update(&zero, &x);

    return 0;
}

int on_exit(struct pt_regs *ctx) {

    int zero = 0;
    u64 *entry_ptr, delta = 0;
    int *argument_ptr;

    /* Record exit time */
    u64 time = bpf_ktime_get_ns();

    /* Read PID of current process */
    u32 pid = bpf_get_current_pid_tgid();

#ifdef FILTER_PID
    /* Check if PID matches */
    if (pid != FILTER_PID) {
        return 0;
    }
#endif

    /* Read entry time and count from maps */
    entry_ptr = entry.lookup(&zero);
    argument_ptr = argument.lookup(&zero);

    if (!entry_ptr || !argument_ptr)
        return 0;

    /* Find time difference */
    delta = time - *entry_ptr;

#ifdef THRESHOLD_LATENCY
    /* Check if latency does not exceed threshold */
    if (delta < THRESHOLD_LATENCY) {
        return 0;
    }
#endif

    bpf_trace_printk("latency = %lu ns for x = %llu\\n", delta, *argument_ptr);
    return 0;
}
""".replace("DEFINE_FILTER_PID", "#define FILTER_PID %u" % args.pid if args.pid > 0 else "") \
   .replace("DEFINE_THRESHOLD_LATENCY", "#define THRESHOLD_LATENCY %u" % args.threshold if args.threshold > 0 else "")

# load BPF program
b = BPF(text=prog)
b.attach_uprobe(name="./busy-loop", sym="foo", fn_name="on_entry")
b.attach_uretprobe(name="./busy-loop", sym="foo", fn_name="on_exit")

# header
print("%-18s %-16s %-6s %s" % ("TIME(s)", "COMM", "PID", "MESSAGE"))

# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    except KeyboardInterrupt:
        print
        break
    print("%-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
