import argparse
from datetime import datetime, timedelta
from sched import scheduler
from sys import stdout
from time import time

from .husmow import TokenConfig, API


def run_logger(tc, args, stop_time):
    mow = API()
    mow.set_token(tc.token, tc.provider)
    mow.select_robot(args.mower)

    sch = scheduler(timefunc=time)
    status = {'status': None, 'status_changed': None}

    def write_log(*strings, fName=args.file, mode='a'):
        out = open(fName, mode) if fName else stdout
        print(*strings, sep=',', file=out)
        if fName:
            out.close()

    def now():
        return datetime.now().replace(microsecond=0)

    def log_status():
        mow_status = mow.status()
        start = datetime.utcfromtimestamp(
            mow_status['nextStartTimestamp']) if mow_status['nextStartTimestamp'] else None
        if status['status'] != mow_status['mowerStatus']:
            if args.summary and status['status'] is not None:
                # Write the summary. Skip the first iteration
                write_log(
                    now().isoformat(),
                    status['status'],
                    now() - status['status_changed'],
                    fName=args.summary)
            status['status'] = mow_status['mowerStatus']
            status['status_changed'] = now()
        # The latest location has index 0
        location = mow_status['lastLocations'][0]
        currentTime = datetime.now()
        write_log(currentTime.isoformat(), mow_status['mowerStatus'], mow_status['batteryPercent'],
                  start.isoformat() if start else '',
                  now() - status['status_changed'], location['latitude'], location['longitude'])
        if stop_time >= currentTime:
            if mow_status['mowerStatus'] == 'PARKED_TIMER' and mow_status['batteryPercent'] == 100:
                # The mower has a full battery and is waiting for the next timer.
                # Skip until 2 minutes before the next timer start
                nextStart = start - timedelta(0, 2 * 60)
                if nextStart > datetime.now():
                    # fallback to the usual operation if the nextStart is not in the future
                    return sch.enterabs(nextStart.timestamp(), 1, log_status)
            sch.enter(args.delay, 1, log_status)
        elif args.summary and status['status'] is not None:
            write_log(
                now(), status['status'], now() - status['status_changed'], fName=args.summary)

    write_log(
        'time',
        'status',
        'battery %',
        'next start time',
        'status duration',
        'latitude',
        'longitude',
        mode='w')
    if args.summary:
        write_log('time', 'status', 'status duration', fName=args.summary, mode='w')
    log_status()
    sch.run()


def parse_until(args):
    until = args.until.lower()
    try:
        num = int(until[:-1])
    except Exception:
        print('The until argument is not valid.', until)
        exit(2)
    if until.endswith('m'):
        return datetime.now() + timedelta(0, 60 * num)
    if until.endswith('d'):
        return datetime.now() + timedelta(num)
    print('The until argument is not valid.')
    exit(3)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Periodically log the mower status.',
        epilog='A valid token.cfg config file is required. Use husmow to create it.')
    parser.add_argument(
        '-d',
        '--delay',
        help='How often (in seconds) should the status be logged.',
        default=60,
        type=int)
    parser.add_argument(
        '-u',
        '--until',
        help='When to stop logging. Use NUMm for minutes or NUMd for days. \
        Es: 20m is 20 minutes; 10d if 10 days',
        default='1d')
    parser.add_argument('-f', '--file', help='Save output on a file')
    parser.add_argument(
        '-s',
        '--summary-file',
        dest='summary',
        help='Save the summary on a file. This command will print a line only when \
        the mower status changes.')
    parser.add_argument(
        '-m',
        '--mower',
        dest='mower',
        help='Select the mower to use. When not provied the first mower will be used.')
    args = parser.parse_args()

    stop_time = parse_until(args)

    tc = TokenConfig()
    tc.load_config()
    if tc.token_valid():
        run_logger(tc, args, stop_time)
    else:
        print('The token is not valid.')
        exit(1)
