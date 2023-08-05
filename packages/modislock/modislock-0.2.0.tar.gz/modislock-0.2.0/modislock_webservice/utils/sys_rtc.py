
from subprocess import run, PIPE, CalledProcessError, TimeoutExpired
import re

from tzlocal import get_localzone


def ntp_clock_sync(enabled=None):
    """Sets/Gets NTP clock sync

    :param bool enabled:
    :return bool:
    """
    args = ['timedatectl']
    result = False

    if enabled is not None:
        if isinstance(enabled, bool):
            args.append('set-ntp')
            args.append('true' if enabled else 'false')

            try:
                run(args, timeout=5)
            except (CalledProcessError, TimeoutExpired):
                pass
    else:
        try:
            args.append('status')
            output = run(args, stdout=PIPE, timeout=5)
        except (CalledProcessError, TimeoutExpired):
            pass
        else:
            if output.returncode == 0 and output.stdout:
                output = output.stdout.decode()
                ntp = re.search(r'(?:System clock synchronized|System clock synchronized)[: ]+(?P<enable>(?:yes|no))',
                                output, re.IGNORECASE)

                if ntp is not None:
                    try:
                        result = True if ntp.group('enable') == 'yes' else False
                    except IndexError:
                        result = False

    return result


def time_zone(tzone=None):
    """Sets / Gets system timezone

    :param str tzone:
    :return str tzone:
    """
    if tzone is None:
        return get_localzone().zone

    if not isinstance(tzone, str):
        return None

    try:
        args = ['timedatectl', 'set-timezone', tzone]
        run(args, timeout=10)
    except (CalledProcessError, TimeoutExpired):
        return None
    else:
        return tzone


def system_time(time_date):
    """Get system date and time

    :param time_date:
    :return:
    """
    if not isinstance(time_date, str):
        raise TypeError
    if re.match('^\d{2}:\d{2}:\d{2} \d{4}-\d{2}-\d{2}$', time_date):
        args = ['timedatectl', 'set-time', time_date]

        try:
            run(args, timeout=10)
        except (CalledProcessError, TimeoutExpired):
            pass
    else:
        raise TypeError
