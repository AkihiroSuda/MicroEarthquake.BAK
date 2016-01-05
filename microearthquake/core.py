import colorama
import os
import multiprocessing
import numpy as np
import numpy.random
import random
import time

import microearthquake
from microearthquake.common import Util
import microearthquake._native as _native

LOG = microearthquake.LOG.getChild(__name__)

BASE = 1e6
R = 1.0


class MicroEarthquake(object):

    def __init__(self,
                 root_pid,
                 interval,
                 probability,
                 dry_run=False):
        assert isinstance(root_pid, int)
        assert isinstance(interval, float)
        assert isinstance(probability, float)
        assert not probability < 0.0
        assert not probability > 1.0
        assert isinstance(dry_run, bool)

        # set args
        self.root_pid = root_pid
        self.interval = interval
        self.probability = probability
        self.dry_run = dry_run

        # others
        self.cpu_count = multiprocessing.cpu_count()

    def _apply_sched(self, pid, runtime, deadline, period):
        """
        Apply SCHED_DEADLINE(runtime,deadline,period) to pid.
        runtime, deadline, and period are in nanoseconds. see sched_setattr(2).
        Should satisfy runtime <= deadline <= period.
        """
        LOG.info('Applying SCHED_DEADLINE(%f,%f,%f) for %s',
                 runtime / BASE,
                 deadline / BASE,
                 period / BASE,
                 Util.stringify_process(pid))

        if self.dry_run:
            return

        res = _native.lib.sched_setattr_deadline(pid,
                                                 runtime,
                                                 deadline,
                                                 period)
        assert res == 0 or res == -1
        if res < 0:
            LOG.warning(colorama.Back.RED + colorama.Fore.WHITE +
                        'sched_setattr() returned errno %d (%s)' +
                        colorama.Style.RESET_ALL,
                        _native.ffi.errno,
                        os.strerror(_native.ffi.errno))
        return res == 0

    def _choose_scheds(self, pids):
        """
        list of pid -> list of (pid, runtime, deadline, period)
        TODO: check sched_rt_{runtime,period}_us (by default: 0.95e6, 1e6)
        TODO: anti-aging
        """
        l = []
        ratios = [f for f in np.random.dirichlet(
            np.ones(len(pids)), size=1)[0]]
        for i, pid in enumerate(pids):
            runtime = int(BASE * ratios[i] * R * self.cpu_count)
            deadline = int(BASE)
            period = deadline
            l.append((pid, runtime, deadline, period))
        return l

    def _choose_scheds_fair(self, pids):
        l = []
        for i, pid in enumerate(pids):
            runtime = int(BASE / len(pids) * 0.95 * self.cpu_count)
            deadline = int(BASE)
            period = deadline
            l.append((pid, runtime, deadline, period))
        return l

    def step(self):
        # nop in 1.0 - prob
        if not Util.probab(self.probability):
            return

        pids = Util.get_all_pids_under(self.root_pid)
        random.shuffle(pids)

        scheds = self._choose_scheds(pids)

        applied_count = 0
        for (pid, runtime, deadline, period) in scheds:
            applied = self._apply_sched(pid, runtime, deadline, period)
            if applied:
                applied_count += 1

        LOG.info(colorama.Back.GREEN + colorama.Fore.WHITE +
                 'Applied: %d of %d, #PID=%d' + colorama.Style.RESET_ALL,
                 applied_count, len(scheds), len(pids))
        time.sleep(self.interval)

    def run(self):
        LOG.info('Starting MicroEarthquake for %s',
                 Util.stringify_process(self.root_pid))
        if not self.dry_run:
            Util.check_caps()
        while True:
            try:
                self.step()
            except Exception as e:
                LOG.warning('got an exception')
                LOG.exception(e)
