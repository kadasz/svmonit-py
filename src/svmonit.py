#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import smtplib
import logging
import argparse
import subprocess
from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from logging.handlers import SMTPHandler


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

class MailLogger(SMTPHandler):
    '''
    Custom MailLogger for the logger.
    '''

    def __init__(self, host, port, fromm, to, subject, credentials=None, secure=None):
        super(MailLogger, self).__init__(host, port, fromm, to, subject, credentials, secure)
        self.host = host
        self.port = smtplib.SMTP_PORT if port is 'default' else port
        self.fromm = fromm
        self.to = to
        self.subject = subject
        self.timeout = 5.0

    def emit(self, record):
        try:
            msg = self.format(record)
            msg  = msg = MIMEMultipart()
            msg['From'] = self.fromm
            msg['To'] = self.to
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = self.subject
            msg.attach(MIMEText(record.msg, 'plain'))
            smtp = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
            smtp.sendmail(self.fromm, self.to, msg.as_string())
            smtp.quit()
        except:
            self.handleError(record)


def main():

     parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__,
                        help='show version')
    parser.add_argument('-s', dest='svname', type=str,
                        help='select runit service')
    parser.add_argument('-m', dest='host', type=str,
                        help='select mail host address')
    parser.add_argument('-p', dest='port', type=int,
                        help='select mail host port - optional')
    parser.add_argument('-t', dest='sender', type=str,
                        help='select sender email')
    parser.add_argument('-r', dest='receiver', type=str,
                        help='select receiver email')
    args = parser.parse_args()

    try:
        if not args.svname:
            parser.print_help()
            sys.exit()
        elif not args.svname:
            parser.error("Please  select runit service name")
        elif args.svname:
            pass
    except Exception as e:
        print('Error - {}'.format(e))
        sys.exit(3)

    try:
        if not args.host:
            parser.error("Please select host mail name")
        elif not args.sender:
            parser.error("Please select sender email")
        elif not args.receiver:
            parser.error("Please select receiver email")
        elif args.host and not args.sender and not args.receiver:
            pass
    except Exception as e:
        print('Error - {}'.format(e))
        sys.exit(3)

    MAILHOST = "{}".format(args.host)
    MAILPORT = "{}".format('default' if args.port is None else args.port)
    SENDER = "{}".format(args.sender)
    RECIPIENT = "{}".format(args.receiver)
    SUBJECT = '[ALERT] Error while work a {} service'.format(args.svname)

    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    mail_handler = MailLogger(host=MAILHOST, port=MAILPORT, fromm=SENDER, to=RECIPIENT, subject=SUBJECT)
    mail_handler.setLevel(logging.INFO)
    mail_handler.setFormatter("%(msg)s")
    log.addHandler(mail_handler)

if __name__ == '__main__':
    main()
