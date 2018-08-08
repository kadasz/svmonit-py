#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import subprocess


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

    def __init__(self, action, service):
        regex = r'^(?P<status>(.*?)):\s+(?P<proc>(.*?)):\s+(\(pid\s+(?P<pid>\d+)\)\s+)?(?P<ttl>\d+)s'
        self.cmd = Run()
        sv = self.cmd('sv', action, service)
        match = re.match(regex, sv)
        self.status = match.groupdict()

    def __str__(self):
        return "{}".format(self.status)

#print(Runsv('status', 'cron'))
