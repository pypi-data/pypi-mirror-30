from subprocess import run, PIPE, CalledProcessError, TimeoutExpired
import re


def system_ssh(enabled=None):
    """Enable / Disable SSH or return active status

    :param bool enabled:
    :return bool:
    """
    args = ['systemctl', 'is-active', 'ssh']

    try:
        output = run(args, timeout=10)
    except (CalledProcessError, TimeoutExpired):
        return False
    else:
        if output.returncode == 0 and output.stdout:
            output = re.search(r'(?P<enable>(?:active|inactive))', output.stdout.decode())
        else:
            return False

    try:
        output = True if output.group('enable') == 'active' else False
    except IndexError:
        return False

    if enabled is None:
        return output
    else:
        if enabled:
            args = ['systemctl', 'enable', 'ssh', ';', 'systemctl', 'start', 'ssh']
        else:
            args = ['systemctl', 'stop', 'ssh', ';', 'systemctl', 'disable', 'ssh']

        try:
            result = run(args, timeout=10, stdout=PIPE)
        except (CalledProcessError, TimeoutExpired):
            return False
        else:
            return True
