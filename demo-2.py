#!/usr/bin/env python
#
# Copyright 2018 Sandipan Das, IBM Corporation
#
# Trace the write() system call by attaching kprobes that are
# triggered on entry and exit. This will print the arguments
# and return value each time we enter or exit from this system
# call only for a specific process.
#

from bcc import BPF
import argparse

# setup argument parsing
parser = argparse.ArgumentParser(
    description="",
    formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", "--pid", type=int, required=True,
    dest="pid", metavar="PID", help="the pid to trace")
args = parser.parse_args()

# define BPF program
prog = """
#include <uapi/linux/ptrace.h>

DEFINE_FILTER_PID

int on_write_entry(struct pt_regs *ctx) {

    /*
     * ssize_t write(int fd, const void *buf, size_t count);
     * write() writes up to 'count' bytes from the buffer pointed by 'buf'
     * to the file referred to by the file descriptor 'fd'
     */

#ifdef __x86_64__
    struct pt_regs args;

    /* Read argument to stub */
    bpf_probe_read(&args, sizeof(struct pt_regs), (void *) PT_REGS_PARM1(ctx));

    /* Read arguments to actual function */
    int fd = (unsigned int) PT_REGS_PARM1(&args);
    char *buf = (char *) PT_REGS_PARM2(&args);
    size_t count = (size_t) PT_REGS_PARM3(&args);
#else
    /* Read arguments */
    int fd = (int) PT_REGS_PARM1(ctx);
    char *buf = (char *) PT_REGS_PARM2(ctx);
    size_t count = (size_t) PT_REGS_PARM3(ctx);
#endif

    /* Read PID of current process */
    unsigned int pid = bpf_get_current_pid_tgid();

    /* Check if PID matches */
    if (pid != FILTER_PID)
        return 0;

    bpf_trace_printk("entry: %d, %s, %lu\\n", fd, buf, count);
    return 0;
}

int on_write_exit(struct pt_regs *ctx) {

    /*
     * ssize_t write(int fd, const void *buf, size_t count);
     * On success, the number of bytes written is returned (zero indicates
     * nothing was written). On error, -1 is returned, and errno is set
     * appropriately.
     */

    /* Read return value */
    size_t ret = (size_t) PT_REGS_RC(ctx);

    /* Read PID of current process */
    unsigned int pid = bpf_get_current_pid_tgid();

    /* Check if PID matches */
    if (pid != FILTER_PID)
        return 0;

    bpf_trace_printk("exit: %lu\\n", ret);
    return 0;
}
""".replace("DEFINE_FILTER_PID", "#define FILTER_PID %u" % args.pid if args.pid > 0 else "")

# load BPF program
b = BPF(text=prog)
b.attach_kprobe(event=b.get_syscall_fnname("write"), fn_name="on_write_entry")
b.attach_kretprobe(event=b.get_syscall_fnname("write"), fn_name="on_write_exit")

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
