# MicroEarthquake: process scheduling fuzzer

MicroEarthquake reproduces flaky bugs by fuzzing process scheduling with [`sched_setattr(2)`](http://man7.org/linux/man-pages/man2/sched_setattr.2.html).


## Usage
On Terminal 1:

    $ (cd /somewhere; mvn test)

On Terminal 2:

    $ ./bin/microearthquake pid $TERMINAL1_BASH_PID

Notes:

 * Requires `CAP_SYS_NICE`.
 * subprocesses and LWPs (i.e.,threads) are also fuzzed.


## How it works

Using Dirichlet distribution, MicroEarthquake finds the randomized utilization sequence `$u_i$` (`$0 <= i < NTASKS$`) that satisfies `$\sum u_i = NCPU$`.

Then MicroEarthquake determines actual parameters that almost satisfy `$WCET_i / P_i = u_i$`.

See [`sched-deadline.txt`](https://www.kernel.org/doc/Documentation/scheduler/sched-deadline.txt).

__We still need much more improvement.__


## Related Project

 * [Earthquake: a programmable fuzzy scheduler for testing distributed systems](https://github.com/osrg/earthquake)

MicroEarthquake is planned to be rewritten in Go and merged to Earthquake;

Even after that, MicroEarthquake may continue as a lightweight version of Earthquake.

