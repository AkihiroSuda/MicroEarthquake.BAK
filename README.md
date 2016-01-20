# MicroEarthquake: process scheduling fuzzer

MicroEarthquake reproduces flaky bugs by fuzzing process scheduling with [`sched_setattr(2)`](http://man7.org/linux/man-pages/man2/sched_setattr.2.html).


## Build

    $ (cd microearthquake; python3 native_build.py)

## Usage
On Terminal 1:

    $ (cd /somewhere; mvn test)

On Terminal 2:

    $ ./bin/microearthquake pid $TERMINAL1_MVN_PID

Notes:

 * Requires `CAP_SYS_NICE`.
 * subprocesses and LWPs (i.e.,threads) are also fuzzed.


## How it works

Using Dirichlet distribution, MicroEarthquake finds the randomized utilization sequence `$u_i$` (`$0 <= i < NTASKS$`) that satisfies `$\sum u_i = NCPU$`.

Then MicroEarthquake determines actual parameters that almost satisfy `$WCET_i / P_i = u_i$`.

See [`sched-deadline.txt`](https://www.kernel.org/doc/Documentation/scheduler/sched-deadline.txt).

__We still need much more improvement.__

## Reproduced Bugs
 
 * YARN-{[1978](https://issues.apache.org/jira/browse/YARN-1978), [4168](https://issues.apache.org/jira/browse/YARN-4168), [4543](https://issues.apache.org/jira/browse/YARN-4543), [4548](https://issues.apache.org/jira/browse/YARN-4548), [4556](https://issues.apache.org/jira/browse/YARN-4556)}
 * etcd {[#4006](https://github.com/coreos/etcd/pull/4006), [#4039](https://github.com/coreos/etcd/issues/4039)}
 * ..

## Talks

 * [FOSDEM](https://fosdem.org/2016/schedule/event/nondeterminism_in_hadoop/) (January 30-31, 2016, Brussels)

## Related Project

 * [Earthquake: a programmable fuzzy scheduler for testing distributed systems](https://github.com/osrg/earthquake)

MicroEarthquake is planned to be rewritten in Go and merged to Earthquake;

Even after that, MicroEarthquake may continue as a lightweight version of Earthquake.


## Known Limitation
After running MicroEarthquake many times, `sched_setattr(2)` can fail with `EBUSY`.
This seems to be a bug of kernel; I'm looking into this.

