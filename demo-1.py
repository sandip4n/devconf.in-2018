#!/usr/bin/env python
#
# Copyright 2018 Sandipan Das, IBM Corporation
#
# Trace the write() system call by attaching kprobes that are
# triggered on entry and exit. This will print the arguments
# and return value each time we enter or exit from this system
# call on a system-wide basis.
#

from bcc import BPF

# define BPF program
prog = """
#include <linux/ptrace.h>

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

    bpf_trace_printk("sys_write() entry: fd = %d, buf = \\"%s\\", count = %lu\\n", fd, buf, count);
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

    bpf_trace_printk("sys_write() return: %lu\\n", ret);
    return 0;
}
"""

# load BPF program
b = BPF(text=prog)
b.attach_kprobe(event=b.get_syscall_fnname("write"), fn_name="on_write_entry")
b.attach_kretprobe(event=b.get_syscall_fnname("write"), fn_name="on_write_exit")

# header
print("%-6s %s" % ("PID", "MESSAGE"))

# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    except KeyboardInterrupt:
        print
        break
    print("%-6d %s" % (pid, msg))
