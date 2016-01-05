import glob
import logging
import os
import prctl
import psutil
import random
import sys


def init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class Util:

    @classmethod
    def probab(cls, probability):
        assert isinstance(probability, float)
        return random.uniform(0, 1) < probability

    @classmethod
    def stringify_process(cls, pid, verbose=False):
        assert isinstance(pid, int)
        p = psutil.Process(pid)
        try:
            cmdline = ' '.join(p.cmdline())
            lim = 32
            if len(cmdline) > lim and not verbose:
                cmdline = cmdline[0:lim] + '..'
            return '<Process name:%s, pid:%d, exe:%s, cmdline:%s>' % \
                (p.name(), p.pid, p.exe(), cmdline)
        except Exception as e:
            # psutil.AccessDenied and so on are caught here
            return str(p)

    @classmethod
    def check_caps(cls):
        assert prctl.cap_permitted.sys_nice, 'missing CAP_SYS_NICE'

    @classmethod
    def get_pids_under(cls, pid, recur_ctx=[]):
        pids = [x.pid for x in psutil.Process(pid).children(recursive=True)]
        pids.append(pid)
        return pids

    @classmethod
    def get_lwp_pids_under(cls, pid):
        return sorted([int(os.path.basename(x))
                       for x in glob.glob('/proc/%d/task/[0-9]*' % pid)])

    @classmethod
    def get_all_pids_under(cls, pid):
        proc_pids = cls.get_pids_under(pid)
        lwp_pids = []
        for p in proc_pids:
            lwp_pids.extend(cls.get_lwp_pids_under(p))
        union = sorted(list(set(proc_pids).union(lwp_pids)))
        return union
