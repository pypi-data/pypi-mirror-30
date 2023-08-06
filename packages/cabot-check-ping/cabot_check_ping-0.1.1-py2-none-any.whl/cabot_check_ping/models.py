import re
import subprocess

from django.core.validators import MinValueValidator
from django.db import models

from cabot.cabotapp.models import StatusCheck, StatusCheckResult


RE_MATCH_STATS = re.compile(r'^(?P<tx>[0-9]+) [^,]+, ' +
                            r'(?P<rx>[0-9]+) [^,]+, ' +
                            r'(?:\+?(?P<errors>[0-9]+) [^,]+, )?' +
                            r'(?P<packet_loss>[0-9\.]+)% [^,]+, ' +
                            r'.+ (?P<time>[0-9]+[a-z]+)$').match


class PingStatusCheck(StatusCheck):
    check_name = 'ping'
    edit_url_name = 'update-ping-check'
    duplicate_url_name = 'duplicate-ping-check'
    icon_class = 'glyphicon-link'
    host = models.TextField(
        help_text=b'Host to check.',
    )
    packet_size = models.PositiveIntegerField(
        verbose_name=b'Packet size',
        help_text=b'Packet size in data bytes.',
        default=56,
    )
    count = models.PositiveIntegerField(
        help_text=b'Ping count.',
        default=3,
    )
    max_rtt = models.FloatField(
        verbose_name=b'Max RTT',
        help_text=b'Maximum RTT.',
        validators=[MinValueValidator(0.0)],
        default=70,
    )

    @property
    def check_category(self):
        return "Ping Check"

    def _parse_output(self, output):
        r = {'tx':          None,
             'rx':          None,
             'packet_loss': None,
             'errors':      None,
             'time':        None,
             'rtt':
                {'min':  None,
                 'avg':  None,
                 'max':  None,
                 'mdev': None,
                 'unit': None}}

        is_stats = 0

        for x in output.split('\n'):
            if x.startswith('--- '):
                is_stats = 1
                continue
            elif is_stats == 1:
                is_stats = 2
                m = RE_MATCH_STATS(x)
                if m:
                    r.update(m.groupdict())
                    r['packet_loss'] = float(r['packet_loss'])
                    r['tx'] = int(r['tx'])
                    r['tx'] = int(r['rx'])
            elif is_stats == 2 and x.startswith('rtt '):
                legends, values = x[4:].split('=')
                (values, r['rtt']['unit']) = values.strip().split(' ', 1)
                r['rtt'].update(dict(zip(legends.strip().split('/'),
                                     [float(i) for i in values.strip().split('/')])))
                break

        return r

    def _run(self):
        result = StatusCheckResult(status_check=self)

        args = ['ping',
                '-s', str(self.packet_size),
                '-c', str(self.count),
                '-W', str(self.timeout),
                self.host]

        try:
            result.raw_data = subprocess.check_output(args, stderr=subprocess.STDOUT, shell=False)
            r = self._parse_output(result.raw_data)
            if r['packet_loss'] > 0.0:
                raise Exception("%0.1f%% packet loss" % r['packet_loss'])
            elif self.max_rtt and r['rtt']['avg'] > self.max_rtt:
                raise Exception("Maximum average RTT reached: %s" % r['rtt']['avg'])
        except subprocess.CalledProcessError as e:
            result.succeeded = False
            result.error = e.output
        except Exception as e:
            result.error = u"{}, Host: {}".format(e.message, self.host)
            result.succeeded = False
        else:
            result.succeeded = True

        return result
