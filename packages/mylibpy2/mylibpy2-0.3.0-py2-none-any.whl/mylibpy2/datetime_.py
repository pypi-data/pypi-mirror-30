#-*- coding: utf-8 -*-
import sys as _sys
import time as _time
import math as _math
from datetime import datetime as _datetime
from datetime import tzinfo as _tzinfo
from datetime import timedelta as _timedelta

#default_encoding = _sys.getdefaultencoding()
_filesystem_encoding = _sys.getfilesystemencoding()
_timezone_offset_seconds = -_time.timezone
_timezone_offset_hours = int(_timezone_offset_seconds / 3600)
_timezone_names = [
    _time.tzname[0].decode(_filesystem_encoding or 'utf-8'),
    _time.tzname[1].decode(_filesystem_encoding or 'utf-8')
]

ZERO = _timedelta(0)

class _TZ(_tzinfo):
    def __init__(self, offset_hours, name):
        self._offset = _timedelta(hours=offset_hours)
        self._name = name
    
    def utcoffset(self, dt):
        return self._offset

    def tzname(self, dt):
        return self._name

    def dst(self, dt):
        return ZERO

_TZ_LOCAL = _TZ(_timezone_offset_hours, _timezone_names[0])
_TZ_UTC = _TZ(0, 'UTC')


class Datetime:
    def __init__(self):
        self._dt = None
        self._millis = 0
        self._tz_offset_hours = 0

    @staticmethod
    def now(tz_offset_hours=None):
        if tz_offset_hours is None:
            tz = _TZ_LOCAL
            tz_offset_hours = _timezone_offset_hours
        else:
            tz = _TZ(tz_offset_hours, '')
        d = Datetime()
        # discard microsecond
        t = _time.time()
        d._millis = long(_math.floor(t * 1000))
        d._dt = _datetime.fromtimestamp(t, tz)
        d._tz_offset_hours = tz_offset_hours
        return d

    @staticmethod
    def from_epoch_millis(epoch_millis, tz_offset_hours=None):
        if type(epoch_millis) != long:
            raise TypeError()
        elif tz_offset_hours is None:
            tz = _TZ_LOCAL
            tz_offset_hours = _timezone_offset_hours
        else:
            tz = _TZ(tz_offset_hours, '')
        d = Datetime()
        d._millis = epoch_millis
        d._dt = _datetime.fromtimestamp(epoch_millis / 1000.0, tz)
        d._tz_offset_hours = tz_offset_hours
        return d

    @staticmethod
    def from_local_millis(local_millis, tz_offset_hours=None):
        if type(local_millis) != unicode:
            raise TypeError('The local_millis must be unicode: %s' % (type(local_millis)))
        elif tz_offset_hours is None:
            tz = _TZ_LOCAL
            tz_offset_hours = _timezone_offset_hours
        else:
            tz = _TZ(tz_offset_hours, '')
        d = Datetime()
        # qpython's locale module is not valid. and strptime doesn't work.
        #d._dt = datetime.strptime(local_millis+u'000', '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=tz)
        # 2017-01-01 00:00:00.000
        # 01234567890123456789012
        d._dt = _datetime(
            int(local_millis[0:4]), int(local_millis[5:7]), int(local_millis[8:10]),
            int(local_millis[11:13]), int(local_millis[14:16]), int(local_millis[17:19]),
            int(local_millis[20:23]+u'000'), tz
        )
        d._millis = long(_math.floor((d._dt - _datetime.fromtimestamp(0, tz)).total_seconds() * 1000))
        d._tz_offset_hours = tz_offset_hours
        return d

    @staticmethod
    def from_compact_millis(compact_millis, tz_offset_hours=None):
        if type(compact_millis) != unicode:
            raise TypeError('The compact_millis must be unicode: %s' % (type(compact_millis)))
        elif tz_offset_hours is None:
            tz = _TZ_LOCAL
            tz_offset_hours = _timezone_offset_hours
        else:
            tz = _TZ(tz_offset_hours, '')
        d = Datetime()
        # qpython's locale module is not valid. and strptime doesn't work.
        # d._dt = datetime.strptime(compact_millis+u'000', '%Y%m%d%H%M%S%f').replace(tzinfo=tz)
        # 20170101000000000
        # 01234567890123456
        d._dt = _datetime(
            int(compact_millis[0:4]), int(compact_millis[4:6]), int(compact_millis[6:8]),
            int(compact_millis[8:10]), int(compact_millis[10:12]), int(compact_millis[12:14]),
            int(compact_millis[14:17]+u'000'), tz
        )
        d._millis = long(_math.floor((d._dt - _datetime.fromtimestamp(0, tz)).total_seconds() * 1000))
        d._tz_offset_hours = tz_offset_hours
        return d

    @staticmethod
    def from_iso_millis(iso_millis):
        if type(iso_millis) != unicode:
            raise TypeError('The iso_millis must be unicode: %s' % (type(iso_millis)))
        elif iso_millis[-1:] == 'Z':
            tz = _TZ_UTC
            tz_offset_hours = 0
            iso_millis = iso_millis[:-1]
        else:
            tz = _TZ(int(iso_millis[-3:]), '?')
            tz_offset_hours = int(iso_millis[-3:])
            iso_millis = iso_millis[:-3]
        d = Datetime()
        # qpython's locale module is not valid. and strptime doesn't work.
        #d._dt = datetime.strptime(iso_millis+u'000', '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=tz)
        # 2017-01-01T00:00:00.000
        # 01234567890123456789012
        d._dt = _datetime(
            int(iso_millis[0:4]), int(iso_millis[5:7]), int(iso_millis[8:10]),
            int(iso_millis[11:13]), int(iso_millis[14:16]), int(iso_millis[17:19]),
            int(iso_millis[20:23]+u'000'), tz
        )
        d._millis = long(_math.floor((d._dt - _datetime.fromtimestamp(0, tz)).total_seconds() * 1000))
        d._tz_offset_hours = tz_offset_hours
        return d

    def to_epoch_millis(self):
        return self._millis

    def to_local_millis(self):
        return unicode(self._dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

    def to_compact_millis(self):
        return unicode(self._dt.strftime('%Y%m%d%H%M%S%f')[:-3])

    def to_iso_millis(self):
        if self._dt.tzinfo is None:
            raise ValueError('There is no timezone info')
        tz = self._dt.strftime('%z')
        if tz == '+0000': tz = 'Z'
        else: tz = tz[:3]
        return unicode(self._dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + tz)

    def add_millis(self, millis):
        if type(millis) != int:
            raise TypeError()
        return Datetime.from_epoch_millis(self.to_epoch_millis() + millis, self._tz_offset_hours)

    def sub(self, dt):
        if not isinstance(dt, Datetime):
            raise TypeError()
        return int(self._millis - dt._millis)

    def replace_timezone(self, tz_offset_hours):
        return Datetime.from_epoch_millis(self.to_epoch_millis(), tz_offset_hours)

    def floor_millis(self, modular):
        millis = self.to_epoch_millis() + self._tz_offset_hours * 3600000
        millis = millis // modular * modular
        millis = millis - self._tz_offset_hours * 3600000
        return Datetime.from_epoch_millis(millis, self._tz_offset_hours)

if __name__ == '__main__':
    pass
