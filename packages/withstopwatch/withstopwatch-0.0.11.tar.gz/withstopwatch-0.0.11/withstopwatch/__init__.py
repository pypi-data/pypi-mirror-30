from __future__ import print_function
import datetime


class Stopwatch:  # pylint: disable=too-many-instance-attributes
    r"""
    Basic usage:
    >>> with Stopwatch():
    ...     pass
    0 ms

    Using fields:
    >>> with Stopwatch() as s:
    ...     pass
    0 ms
    >>> assert isinstance(s.label, str) and s.label == '0 ms'
    >>> assert isinstance(s.ms, int) and s.ms == 0
    >>> assert isinstance(s.s, int) and s.s == 0
    >>> assert isinstance(s.seconds, float) and s.seconds > 0
    >>> assert isinstance(s.timedelta, datetime.timedelta)
    >>> assert isinstance(s.start, datetime.datetime)
    >>> assert isinstance(s.stop, datetime.datetime)
    >>> print(s)  # doctest: +ELLIPSIS
    0:00:00.000...
    >>> repr(s)  # doctest: +ELLIPSIS
    '<Stopwatch: datetime.timedelta(0, 0, ...)>'

    Silence options:
    >>> with Stopwatch(template=None) as s:
    ...     pass
    >>> assert s.label is None
    >>> with Stopwatch(file=None) as s:
    ...     pass
    >>> assert s.label == '0 ms'

    With different templates:
    >>> with Stopwatch(template='passing'):
    ...     pass
    0 ms: passing
    >>> with Stopwatch('passing'):
    ...     pass
    0 ms: passing
    >>> with Stopwatch('{ms} ms'):
    ...     pass
    0 ms
    >>> with Stopwatch('{s} s'):
    ...     pass
    0 s
    >>> with Stopwatch('{:.03f} (i.e. {seconds:.03f})'):
    ...     pass
    0.000 (i.e. 0.000)
    >>> with Stopwatch('{timedelta}'):
    ...     pass   # doctest: +ELLIPSIS
    0:00:00.000...
    >>> with Stopwatch('from {start!r} to {stop!r}') as s:
    ...     pass   # doctest: +ELLIPSIS
    from datetime.datetime(...) to datetime.datetime(...)
    >>> assert s.stop - s.start == s.timedelta

    With an exception:
    >>> with Stopwatch(file=None):
    ...     raise Exception()
    Traceback (most recent call last):
    Exception
    >>> try:
    ...     with Stopwatch() as s:
    ...        raise Exception()
    ... except Exception as exc:
    ...     print(repr(s))  # doctest: +ELLIPSIS
    0 ms
    <Stopwatch: datetime.timedelta(0, 0, ...)>

    Testing with `time.sleep` (note: the tests may fail during a slower run):
    >>> import time
    >>> with Stopwatch() as s:
    ...     time.sleep(0.1)
    100 ms
    >>> assert 0.1 < s.seconds < 0.2

    Embedded stopwatchs:
    >>> with Stopwatch('outer'):
    ...     with Stopwatch('inner'):
    ...         pass
    0 ms: inner
    0 ms: outer

    Measuring the overhead of Stopwatch using Stopwatch itself
    (note: the tests may fail during a slower run):
    >>> with Stopwatch(file=None) as s1:
    ...     with Stopwatch('inner') as s2:
    ...         pass
    0 ms: inner
    >>> with Stopwatch(file=None) as s3:
    ...     pass
    >>> overhead = s1.seconds - s3.seconds
    >>> assert 0 <= overhead < 0.0001  # actually ~20 us on i5@2.60GHz, Linux
    """
    # Note: `sys.stdout` didn't work with doctests in Python 3.6.0.
    _FILE_DEFAULT = object()

    @classmethod
    def _normalize_template(cls, template):
        if template is None:
            return template
        if not isinstance(template, str):
            raise TypeError('template must be None or a string')
        if '{' in template:
            return template
        return '{ms} ms: ' + template

    def __init__(self, template='{ms} ms', *, file=_FILE_DEFAULT):
        self.template = self._normalize_template(template)
        self.file = file
        self.start = None
        self.stop = None
        self.timedelta = None
        self.seconds = None
        self.s = None  # pylint: disable=invalid-name
        self.ms = None  # pylint: disable=invalid-name
        self.label = None

    def __enter__(self):
        self.start = datetime.datetime.now()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop = datetime.datetime.now()
        self.timedelta = self.stop - self.start

        self.seconds = self.timedelta.total_seconds()
        self.s = round(self.seconds)
        self.ms = round(self.seconds * 1000)
        if self.template is not None:
            self.label = self.template.format(self.seconds, **self.__dict__)
            if self.file is self._FILE_DEFAULT:
                print(self.label)
            elif self.file is not None:
                print(self.label, file=self.file)

    def __repr__(self):
        return '<Stopwatch: {!r}>'.format(self.timedelta)

    def __str__(self):
        return str(self.timedelta)
