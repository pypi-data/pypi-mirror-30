# -*- coding: UTF-8 -*-
# @Time    : 2017/5/16 11:22
# @Author  : HeYongbiao
# @email   : gzheyongbiao@corp.netease.com
import re
from collections import namedtuple
from datetime import datetime, timedelta
import time
import sys

_ranges = [
    (0, 59),
    (0, 23),
    (1, 31),
    (1, 12),
    (0, 6),
    (1970, 2099),
]
_attribute = [
    'minute',
    'hour',
    'day',
    'month',
    'isoweekday',
    'year'
]
_alternate = {
    3: {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12},
    4: {'sun': 0, 'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6},
}
_aliases = {
    '@yearly': '0 0 1 1 *',
    '@annually': '0 0 1 1 *',
    '@monthly': '0 0 1 * *',
    '@weekly': '0 0 * * 0',
    '@daily': '0 0 * * *',
    '@hourly': '0 * * * *',
}

if sys.version_info >= (3, 0):
    _number_types = (int, float)
    xrange = range
else:
    _number_types = (int, long, float)

MINUTE = timedelta(minutes=1)
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
WEEK = timedelta(days=7)
MONTH = timedelta(days=28)
YEAR = timedelta(days=365)

WARN_CHANGE = object()


# find the next scheduled time
def _end_of_month(dt):
    ndt = dt + DAY
    while dt.month == ndt.month:
        dt += DAY
    return ndt.replace(day=1) - DAY


def _month_incr(dt, m):
    odt = dt
    dt += MONTH
    while dt.month == odt.month:
        dt += DAY
    # get to the first of next month, let the backtracking handle it
    dt = dt.replace(day=1)
    return dt - odt


def _year_incr(dt, m):
    # simple leapyear stuff works for 1970-2099 :)
    mod = dt.year % 4
    if mod == 0 and (dt.month, dt.day) < (2, 29):
        return YEAR + DAY
    if mod == 3 and (dt.month, dt.day) > (2, 29):
        return YEAR + DAY
    return YEAR


_increments = [
    lambda *a: MINUTE,
    lambda *a: HOUR,
    lambda *a: DAY,
    _month_incr,
    lambda *a: DAY,
    _year_incr,
    lambda dt, x: dt.replace(minute=0),
    lambda dt, x: dt.replace(hour=0),
    lambda dt, x: dt.replace(day=1) if x > DAY else dt,
    lambda dt, x: dt.replace(month=1) if x > DAY else dt,
    lambda dt, x: dt,
]


# find the previously scheduled time
def _day_decr(dt, m):
    if m.day.input != 'l':
        return -DAY
    odt = dt
    ndt = dt = dt - DAY
    while dt.month == ndt.month:
        dt -= DAY
    return dt - odt


def _month_decr(dt, m):
    odt = dt
    # get to the last day of last month, let the backtracking handle it
    dt = dt.replace(day=1) - DAY
    return dt - odt


def _year_decr(dt, m):
    # simple leapyear stuff works for 1970-2099 :)
    mod = dt.year % 4
    if mod == 0 and (dt.month, dt.day) > (2, 29):
        return -(YEAR + DAY)
    if mod == 1 and (dt.month, dt.day) < (2, 29):
        return -(YEAR + DAY)
    return -YEAR


def _day_decr_reset(dt, x):
    if x >= -DAY:
        return dt
    cur = dt.month
    while dt.month == cur:
        dt += DAY
    return dt - DAY


_decrements = [
    lambda *a: -MINUTE,
    lambda *a: -HOUR,
    _day_decr,
    _month_decr,
    lambda *a: -DAY,
    _year_decr,
    lambda dt, x: dt.replace(minute=59),
    lambda dt, x: dt.replace(hour=23),
    _day_decr_reset,
    lambda dt, x: dt.replace(month=12) if x < -DAY else dt,
    lambda dt, x: dt,
]

Matcher = namedtuple('Matcher', 'minute, hour, day, month, weekday, year')


def _assert(condition, message, *args):
    if not condition:
        raise ValueError(message % args)


class _Matcher(object):
    __slots__ = 'allowed', 'end', 'any', 'input', 'which', 'split'

    def __init__(self, which, entry):
        _assert(0 <= which <= 5,
                "improper number of cron entries specified")
        self.input = entry.lower()
        self.split = self.input.split(',')
        self.which = which
        self.allowed = set()
        self.end = None
        self.any = '*' in self.split or '?' in self.split

        for it in self.split:
            al, en = self._parse_crontab(which, it)
            if al is not None:
                self.allowed.update(al)
            self.end = en
        _assert(self.end is not None,
                "improper item specification: %r", entry.lower()
                )

    def __call__(self, v, dt):
        for i, x in enumerate(self.split):
            if x == 'l':
                if v == _end_of_month(dt).day:
                    return True

            elif x.startswith('l'):
                # We have to do this in here, otherwise we can end up, for
                # example, accepting *any* Friday instead of the *last* Friday.
                if dt.month == (dt + WEEK).month:
                    continue

                x = x[1:]
                if x.isdigit():
                    x = int(x) if x != '7' else 0
                    if v == x:
                        return True
                    continue

                start, end = map(int, x.partition('-')[::2])
                allowed = set(range(start, end + 1))
                if 7 in allowed:
                    allowed.add(0)
                if v in allowed:
                    return True

        return self.any or v in self.allowed

    def __lt__(self, other):
        if self.any:
            return self.end < other
        return all(item < other for item in self.allowed)

    def __gt__(self, other):
        if self.any:
            return _ranges[self.which][0] > other
        return all(item > other for item in self.allowed)

    def _parse_crontab(self, which, entry):
        """
        This parses a single crontab field and returns the data necessary for
        this matcher to accept the proper values.

        See the README for information about what is accepted.
        """

        # this handles day of week/month abbreviations
        def _fix(it):
            if which in _alternate and not it.isdigit():
                if it in _alternate[which]:
                    return _alternate[which][it]
            _assert(it.isdigit(),
                    "invalid range specifier: %r (%r)", it, entry)
            it = int(it, 10)
            _assert(_start <= it <= _end_limit,
                    "item value %r out of range [%r, %r]",
                    it, _start, _end_limit)
            return it

        # this handles individual items/ranges
        def _parse_piece(it):
            if '-' in it:
                start, end = map(_fix, it.split('-'))
                # Allow "sat-sun"
                if which == 4 and end == 0:
                    end = 7
            elif it == '*':
                start = _start
                end = _end
            else:
                start = _fix(it)
                end = _end
                if increment is None:
                    return set([start])

            _assert(_start <= start <= _end_limit,
                    "range start value %r out of range [%r, %r]",
                    start, _start, _end_limit)
            _assert(_start <= end <= _end_limit,
                    "range end value %r out of range [%r, %r]",
                    end, _start, _end_limit)
            _assert(start <= end,
                    "range start value %r > end value %r", start, end)
            return set(range(start, end + 1, increment or 1))

        _start, _end = _ranges[which]
        _end_limit = _end
        # wildcards
        if entry in ('*', '?'):
            if entry == '?':
                _assert(which in (2, 4),
                        "cannot use '?' in the %r field", _attribute[which])
            return None, _end

        # last day of the month
        if entry == 'l':
            _assert(which == 2,
                    "you can only specify a bare 'L' in the 'day' field")
            return None, _end

        # for the last 'friday' of the month, for example
        elif entry.startswith('l'):
            _assert(which == 4,
                    "you can only specify a leading 'L' in the 'weekday' field")
            es, _, ee = entry[1:].partition('-')
            _assert((entry[1:].isdigit() and 0 <= int(es) <= 7) or
                    (_ and es.isdigit() and ee.isdigit() and 0 <= int(es) <= 7 and 0 <= int(ee) <= 7),
                    "last <day> specifier must include a day number or range in the 'weekday' field, you entered %r", entry)
            return None, _end

        increment = None
        # increments
        if '/' in entry:
            entry, increment = entry.split('/')
            increment = int(increment, 10)
            _assert(increment > 0,
                    "you can only use positive increment values, you provided %r",
                    increment)

        # allow Sunday to be specified as weekday 7
        if which == 4:
            _end_limit = 7

        # handle singles and ranges
        good = _parse_piece(entry)

        # change Sunday to weekday 0
        if which == 4 and 7 in good:
            good.discard(7)
            good.add(0)

        return good, _end


class CrontabTrigger(object):
    __slots__ = 'matchers',

    def __init__(self, crontab):
        # check if the job_trigger is illegal
        configs = re.split("\s+", crontab)
        for config in configs:
            if config != "*" and not config.isdigit():
                raise ValueError("crontab expression error: %s" % crontab)
        self.matchers = self._make_matchers(crontab)

    def _make_matchers(self, crontab):
        """
        This constructs the full matcher struct.
        """
        crontab = _aliases.get(crontab, crontab)
        matchers = [_Matcher(which, entry)
                    for which, entry in enumerate(crontab.split())]

        if len(matchers) == 5:
            matchers.append(_Matcher(5, '*'))
        _assert(len(matchers) == 6,
                "improper number of cron entries specified")

        return Matcher(*matchers)

    def _test_match(self, index, dt):
        """
        This tests the given field for whether it matches with the current
        datetime object passed.
        """
        at = _attribute[index]
        attr = getattr(dt, at)
        if at == 'isoweekday':
            attr = attr() % 7
        return self.matchers[index](attr, dt)

    def get_next_runtime(self, start_time, equals=False):
        """
        获取下次需要触发的时间(返回时间戳为>=start_time 或者>start_time)
        :param start_time上次运行时间, 0表示无上次运行时间
        :param equals True表示返回结果>=start_time, False表示返回结果>start_time
        :return: timestamp，0表示不再执行
        """
        if equals:
            start_time = start_time - 1
        start_time = datetime.fromtimestamp(start_time)
        # handle timezones if the datetime object has a timezone and get a
        # reasonable future/past start time
        future = start_time.replace(second=0, microsecond=0) + _increments[0]()
        if future < start_time:
            # we are going backwards...
            _test = lambda: future.year < self.matchers.year
            if start_time.second or start_time.microsecond:
                future = start_time.replace(second=0, microsecond=0)
        else:
            # we are going forwards
            _test = lambda: self.matchers.year < future.year

        # Start from the year and work our way down. Any time we increment a
        # higher-magnitude value, we reset all lower-magnitude values. This
        # gets us performance without sacrificing correctness. Still more
        # complicated than a brute-force approach, but also orders of
        # magnitude faster in basically all cases.
        to_test = 5
        while to_test >= 0:
            if not self._test_match(to_test, future):
                inc = _increments[to_test](future, self.matchers)
                future += inc
                for i in xrange(0, to_test):
                    future = _increments[6 + i](future, inc)
                if _test():
                    return 0
                to_test = 5
                continue
            to_test -= 1

        # verify the match
        match = [self._test_match(i, future) for i in xrange(6)]
        if not all(match):
            sys.stderr.write("there is a bug in Crontab, please replace another one")
            return 0
        return int(time.mktime(future.timetuple()))
