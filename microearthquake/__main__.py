import argparse
import sys
from microearthquake.core import MicroEarthquake


def create_parser():
    parser = argparse.ArgumentParser(
        prog='microearthquake',
        description='MicroEarthquake: process scheduling fuzzer')
    target_modes = ['pid']
    parser.add_argument('TARGET_MODE',
                        choices=target_modes,
                        metavar='TARGET_MODE',
                        help='target mode (one of %s)' % target_modes)
    parser.add_argument('TARGET_SPEC',
                        type=str,
                        nargs=argparse.REMAINDER,
                        help="target specification (depends on TARGET_MODE)")
    parser.add_argument('-i', '--interval',
                        required=False,
                        type=float,
                        default=1.0,
                        help='interval in seconds')
    parser.add_argument('-p', '--probability',
                        required=False,
                        type=float,
                        default=1.0,
                        help='probability (0.0-1.0)')
    parser.add_argument('--dry-run',
                        action='store_true',
                        help='dry run')
    return parser


def create_meq(args):
    if args.TARGET_MODE != 'pid':
        raise RuntimeError('Unknown target mode %s' % args.TARGET_MODE)
    pid = -1
    if len(args.TARGET_SPEC) == 0:
        raise RuntimeError('No pid were specified')
    elif len(args.TARGET_SPEC) == 1:
        try:
            pid = int(args.TARGET_SPEC[0])
        except ValueError as ve:
            raise RuntimeError('Bad pid', ve)
    else:
        raise RuntimeError(
            'You have to specify only one pid number as TARGET_SPEC')
    meq = MicroEarthquake(pid,
                          interval=args.interval,
                          probability=args.probability,
                          dry_run=args.dry_run)
    return meq


def main():
    parser = create_parser()
    args = parser.parse_args()
    meq = create_meq(args)
    meq.run()
    return 0

if __name__ == '__main__':
    sys.exit(main())
