#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import argparse
import subprocess


__author__ = 'Karol D. Sz.'
__contact__ = 'karol_sz@poczta.fm'
__version__ = '0.0.1'
__doc__ = 'Simple python script that monitor runit service'


def sec_to_dhms(sec):
    days = sec // (3600 * 24)
    hours = (sec // 3600) % 24
    minutes = (sec // 60) % 60
    seconds = sec % 60
    if days > 0:
        return '{:0.0f}d{:0.0f}h{:0.0f}m{:0.0f}s'.format(days, hours, minutes, seconds)
    elif hours > 0:
        return '{:0.0f}h{:0.0f}m{:0.0f}s'.format(hours, minutes, seconds)
    elif minutes > 0:
        return '{:0.0f}m{:0.0f}s'.format(minutes, seconds)
    else:
        return '{:0.0f}s'.format(seconds)


class Run:

    def __call__(self, cmd, *args):
        try:
            result = False
            command = [str(i) for i in args]
            command.insert(0, cmd)
            p = subprocess.Popen(command,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (result, error) = p.communicate()
            if p.returncode != 0:
                raise ValueError
        except ValueError:
            return None
        except Exception as e:
            return False
        finally:
            return result.decode("utf-8").rstrip()

class Runsv:

    def __init__(self, service, restart=None):
        cmd = CMD()
        self.sv = cmd('sv', '{}'.format('restart' if restart else 'status'), service)
        for k, v in self._status_dict().items():
            self.__dict__[k] = v

    def _status_dict(self):
        regex = r'^(?P<status>(.*?)):\s+(?P<proc>(.*?)):\s+(\(pid\s+(?P<pid>\d+)\)\s+)?(?P<ttl>\d+)s'
        status = self.sv
        if not status.startswith('fail'):
            match = re.match(regex, status)
            ret =  match.groupdict()
            ret.update({'ttl': "{}".format(sec_to_dhms(int(ret['ttl'])))})
        else:
            ret = dict(status=None)
        return ret

def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__,
                        help='show version')
    parser.add_argument('-s', dest='sv_name', type=str,
                        help='select runit service')
    args = parser.parse_args()
    try:
        if not args.sv_name:
            parser.print_help()
            sys.exit()
        elif args.sv_name:
           print(SV(args.sv_name))
    except Exception as e:
        print('Error - {}'.format(e))
        sys.exit(3)

if __name__ == '__main__':
    main()
