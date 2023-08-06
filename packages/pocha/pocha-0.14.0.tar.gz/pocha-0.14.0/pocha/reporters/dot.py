# coding: utf-8
"""
spec pocha reporter
"""

import time

from colored import fg, attr

from pocha.reporters.base import Reporter
from pocha.util import print_failures


_pass = fg('green')
_fail = fg('red')
_skip = fg('cyan')
_dim = attr('dim')
_reset = attr('reset')

class DotReporter(Reporter):

    def __init__(self):
        self.start = None
        self.passing = 0
        self.failing = 0
        self.skipping = 0
        self.total = 0
        self.failures = []

    def beforeTests(self, stdout):
        self.start = time.time()*1000
        stdout.write('\n')

    def afterTests(self, stdout):
        duration = time.time()*1000 - self.start

        if self.total > 0:
            stdout.write('\n\n')

        if stdout.isatty():
            stdout.write('  %s%d passing%s %s(%dms)%s\n' %
                         (_pass, self.passing, _reset, _dim, duration, _reset))

        else:
            stdout.write('  %d passing (%dms)\n' % (self.passing, duration))

        if self.skipping > 0:
            if stdout.isatty():
                stdout.write('  %s%d pending%s\n' % (_skip, self.skipping, _reset))

            else:
                stdout.write('  %d pending\n' % self.skipping)

        if self.failing != 0:
            if stdout.isatty():
                stdout.write('  %s%d failing%s\n' % (_fail, self.failing, _reset))

            else:
                stdout.write('  %d failing\n' % self.failing)

            stdout.write('\n')
            # list the tests in order with their associated stacktrace
            print_failures(self.failures, stdout)

        stdout.write('\n')

    def afterTest(self, stdout, test):

        if self.total == 0:
            stdout.write('  ')

        self.total += 1

        if test.status == 'pass':
            if stdout.isatty():
                stdout.write('%s.%s' % (_dim, _reset))

            else:
                stdout.write('.')

            self.passing += 1

        elif test.status == 'fail':
            if stdout.isatty():
                stdout.write('%s.%s' % (_fail, _reset))

            else:
                stdout.write('.')

            self.failures.append((test.name, test.exc_info))
            self.failing += 1

        elif test.status == 'skip':
            if stdout.isatty():
                stdout.write('%s.%s' % (_skip, _reset))

            else:
                stdout.write('.')

            self.skipping += 1

        stdout.flush()
