# -*- coding: utf-8 -*-

import time

'''
timeunit:
    timeunit base on java.util.concurrent.TimeUnit

    Sample:
        >>> import timeunit
        >>> timeunit.seconds.to_millis(5)
        5000
'''


# Handy constants for conversion methods
C0 = 1.0
C1 = C0 * 1000
C2 = C1 * 1000
C3 = C2 * 1000
C4 = C3 * 60
C5 = C4 * 60
C6 = C5 * 24

C = [C0, C1, C2, C3, C4, C5, C6]

class _BaseTimeUnit(object):
    def __init__(self, index, name):
        self._index = index
        self._name = name

    @property
    def index(self):
        return self._index

    @property
    def name(self):
        return self._name

    def to_nanos(self, d):
        return int(d / (C[0]/C[self.index]))

    def to_micros(self, d):
        return int(d / (C[1]/C[self.index]))

    def to_millis(self, d):
        return int(d / (C[2]/C[self.index]))

    def to_seconds(self, d):
        return int(d / (C[3]/C[self.index]))

    def to_minutes(self, d):
        return int(d / (C[4]/C[self.index]))

    def to_hours(self, d):
        return int(d / (C[5]/C[self.index]))

    def to_days(self, d):
        return int(d / (C[6]/C[self.index]))

    def convert(self, source_duration, source_unit):
        return source_duration/ (C[self._index] / C[source_unit.index])

    def sleep(self, timeout):
        if timeout < 0:
            timeout = 0
        time.sleep(self.to_seconds(timeout))

nanoseconds = _BaseTimeUnit(0, "nanoseconds")
microseconds = _BaseTimeUnit(1, "microseconds")
milliseconds = _BaseTimeUnit(2, "milliseconds")
seconds = _BaseTimeUnit(3, "seconds")
minutes = _BaseTimeUnit(4, "minutes")
hours = _BaseTimeUnit(5, "hours")
days = _BaseTimeUnit(6, "days")
