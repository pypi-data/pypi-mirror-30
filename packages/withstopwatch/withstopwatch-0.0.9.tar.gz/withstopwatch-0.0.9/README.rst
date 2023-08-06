.. code-block:: python

    Basic usage:
    >>> with Stopwatch() as s:
    ...     pass
    0 ms
    >>> assert isinstance(s.ms, int) and s.ms == 0
    >>> assert isinstance(s.s, int) and s.s == 0
    >>> assert isinstance(s.seconds, float) and s.seconds > 0
    >>> assert isinstance(s.timedelta, datetime.timedelta)
    >>> assert isinstance(s.start, datetime.datetime)
    >>> assert isinstance(s.stop, datetime.datetime)

    Silent:
    >>> with Stopwatch(template=None) as s:
    ...     pass
    >>> assert s.label is None
    >>> with Stopwatch(file=None) as s:
    ...     pass
    >>> assert s.label == '0 ms'

    With different templates:
    >>> with Stopwatch(template='passing') as s:
    ...     pass
    0 ms: passing
    >>> with Stopwatch('passing') as s:
    ...     pass
    0 ms: passing
    >>> with Stopwatch('{ms} ms') as s:
    ...     pass
    0 ms
    >>> with Stopwatch('{s} s') as s:
    ...     pass
    0 s
    >>> with Stopwatch('{:.03f} (i.e. {seconds:.03f})') as s:
    ...     pass
    0.000 (i.e. 0.000)
    >>> with Stopwatch('{timedelta}') as s:
    ...     pass   # doctest: +ELLIPSIS
    0:00:00.000...
    >>> with Stopwatch('from {start!r} to {stop!r}') as s:
    ...     pass   # doctest: +ELLIPSIS
    from datetime.datetime(...) to datetime.datetime(...)
    >>> assert s.stop - s.start == s.timedelta

    With an exception:
    >>> with Stopwatch(file=None) as s:
    ...     raise Exception()
    Traceback (most recent call last):
    Exception
    >>> try:
    ...     with Stopwatch() as s:
    ...        raise Exception()
    ... except Exception as exc:
    ...     print(type(exc))
    0 ms
    <class 'Exception'>

    Testing with `time.sleep` (note: the tests may fail during a slower run):
    >>> import time
    >>> with Stopwatch() as s:
    ...     time.sleep(0.1)
    100 ms
    >>> assert 0.1 < s.seconds < 0.2

    Embedded stopwatchs:
    >>> with Stopwatch() as s:
    ...     with Stopwatch('s2') as s2:
    ...         pass
    0 ms: s2
    0 ms

    Measuring the overhead of Stopwatch using Stopwatch itself
    (note: the tests may fail during a slower run):
    >>> with Stopwatch(file=None) as s1:
    ...     with Stopwatch('s2') as s2:
    ...         pass
    0 ms: s2
    >>> with Stopwatch(file=None) as s3:
    ...     pass
    >>> overhead = s1.seconds - s3.seconds
    >>> assert 0 <= overhead < 0.0001  # actually ~20 us on i5@2.60GHz, Linux
    
