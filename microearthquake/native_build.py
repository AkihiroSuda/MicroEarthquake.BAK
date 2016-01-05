from cffi import FFI
ffi = FFI()
ffi.set_source("_native",
               """
#include <linux/unistd.h>
#include <linux/kernel.h>
#include <linux/types.h>
#include <sys/syscall.h>

#define SCHED_DEADLINE  6
#define SCHED_FLAG_RESET_ON_FORK 0x01

#if defined __x86_64__
#define __NR_sched_setattr 314
#define __NR_sched_getattr 315
#elif defined __i386__
#warning not tested on i386
#define __NR_sched_setattr 351
#define __NR_sched_getattr 352
#elif defined __arm__
#warning not tested on arm
#define __NR_sched_setattr 380
#define __NR_sched_getattr 381
#else
#error unknown arch
#endif

struct sched_attr {
  __u32 size;

  __u32 sched_policy;
  __u64 sched_flags;

  /* SCHED_NORMAL, SCHED_BATCH */
  __s32 sched_nice;

  /* SCHED_FIFO, SCHED_RR */
  __u32 sched_priority;

  /* SCHED_DEADLINE (nsec) */
  __u64 sched_runtime;
  __u64 sched_deadline;
  __u64 sched_period;
};

/* not available in glibc */
int sched_setattr(pid_t pid,
		  const struct sched_attr *attr,
		  unsigned int flags)
{
  return syscall(__NR_sched_setattr, pid, attr, flags);
}

/* not available in glibc */
int sched_getattr(pid_t pid,
		  struct sched_attr *attr,
		  unsigned int size,
		  unsigned int flags)
{
  return syscall(__NR_sched_getattr, pid, attr, size, flags);
}

int sched_setattr_deadline(pid_t pid, __u64 runtime, __u64 deadline, __u64 period) {
  /* https://www.kernel.org/doc/Documentation/scheduler/sched-deadline.txt */
  struct sched_attr attr;
  unsigned int flags = 0;
  attr.size = sizeof(attr);
  attr.sched_flags = SCHED_FLAG_RESET_ON_FORK;
  attr.sched_nice = 0;
  attr.sched_priority = 0;
  attr.sched_policy = SCHED_DEADLINE;
  attr.sched_runtime = runtime;
  attr.sched_deadline = deadline;
  attr.sched_period = period;
  return sched_setattr(pid, &attr, flags);
}

""")

ffi.cdef(
    """
typedef int pid_t;
typedef long __s32;
typedef unsigned long __u32;
typedef unsigned long long __u64;
struct sched_attr {
  __u32 size;

  __u32 sched_policy;
  __u64 sched_flags;

  /* SCHED_NORMAL, SCHED_BATCH */
  __s32 sched_nice;

  /* SCHED_FIFO, SCHED_RR */
  __u32 sched_priority;

  /* SCHED_DEADLINE (nsec) */
  __u64 sched_runtime;
  __u64 sched_deadline;
  __u64 sched_period;
};

int sched_setattr(pid_t pid,
		  const struct sched_attr *attr,
		  unsigned int flags);

int sched_getattr(pid_t pid,
		  struct sched_attr *attr,
		  unsigned int size,
		  unsigned int flags);

int sched_setattr_deadline(pid_t pid,
                           __u64 runtime,
                           __u64 deadline,
                           __u64 period);
"""
)


if __name__ == '__main__':
        ffi.compile()
