from contextlib import contextmanager, ExitStack
import sys
import time
import warnings
import threading
from datetime import datetime, timedelta
from functools import wraps

from .bunch import Bunch
from .decorations import parametrizeable_decorator
from .units import Duration
from .exceptions import PException
from .humanize import time_duration  # due to interference with jrpc
from .misc import stack_level_to_get_out_of_file
from .decorations import kwargs_resilient

IS_A_TTY = sys.stdout.isatty()


class TimeoutException(PException, TimeoutError):
    pass


class Timer(object):

    """
    Multi-purpose timer object:

    t = Timer()
    # do something ...
    t.stop()
    print(t.elapsed)

    t = Timer(expiration=120)
    while not t.expired:
        print("Time remaining: %r" % t.remain)
        # do something ...

    for remain in Timer(expiration=120).iter(sleep=2):
        print("Time remaining: %r" % remain)
        # do something ...
    """

    def __init__(self, now=None, expiration=None):
        self.reset(now)
        self.t1 = None
        self.expiration = expiration

    def reset(self, now=None):
        self.t0 = now or time.time()

    def stop(self):
        self.t1 = time.time()
        return self.t1 - self.t0

    def iter(self, sleep=1):
        while not self.expired:
            time.sleep(sleep)
            yield self.remain

    __iter__ = iter

    @property
    def stopped(self):
        return self.t1 is not None

    @property
    def duration_delta(self):
        return timedelta(seconds=(self.t1 or time.time()) - self.t0)

    @property
    def duration(self):
        return Duration(self.duration_delta.total_seconds())

    @property
    def elapsed_delta(self):
        return timedelta(seconds=time.time() - self.t0)

    @property
    def elapsed(self):
        return Duration(self.elapsed_delta.total_seconds())

    @property
    def expired(self):
        return Duration(max(0, self.elapsed-self.expiration) if self.expiration is not None else 0)

    @property
    def remain(self):
        return Duration(max(0, self.expiration-self.elapsed)) if self.expiration is not None else None

    @property
    def start_time(self):
        return datetime.fromtimestamp(self.t0)

    @property
    def stop_time(self):
        if self.t1 is None:
            return None
        else:
            return datetime.fromtimestamp(self.t1)

    def render(self):
        t0, duration, elapsed, expired, stopped = self.t0, self.duration, self.elapsed, self.expired, self.stopped
        st = time.strftime("%T", time.localtime(t0))
        if expired:
            duration = "{:0.1f}+{:0.2f}".format(self.expiration, expired)
        else:
            duration = "{:0.2f}".format(duration)
        if stopped:
            et = time.strftime("%T", time.localtime(self.t1))
            fmt = "{st}..({duration})..{et}"
        elif expired:
            fmt = "{st}..({duration})"
        else:
            fmt = "{st}..({duration})"
        return fmt.format(**locals())

    def __str__(self):
        return "<T %s>" % self.render()

    def __repr__(self):
        return "Timer(%s)" % self.render()


class BackoffTimer(Timer):

    def __init__(self, expiration, now=None, backoff_every=5, backoff_by=5, max_interval=None):
        super().__init__(expiration=expiration, now=now)
        self.backoff_by = backoff_by
        self.backoff_every = backoff_every
        self.iteration = 0
        self.max_interval = max_interval

    def backoff(self):
        self.iteration += 1
        if self.iteration % self.backoff_every == 0:
            self.expiration *= self.backoff_by
            if self.max_interval:
                self.expiration = min(self.max_interval, self.expiration)
        super().reset()


class StopWatch(object):
    def __init__(self):
        self._last_pause = 0
        self._timer = Timer()
        self.paused = True

    @property
    def elapsed(self):
        if self.paused:
            return self._last_pause
        return self._last_pause + self._timer.elapsed

    def pause(self):
        self._last_pause += self._timer.elapsed
        self.paused = True

    def start(self):
        self.paused = False
        self._timer.reset()

    def reset_and_start(self, last_paused=None):
        self._last_pause = 0
        self.start()


@contextmanager
def timing(t=None):
    if not t:
        t = Timer()
    try:
        yield t
    finally:
        t.stop()


# cache result only when predicate succeeds
class CachingPredicate():
    def __init__(self, pred):
        self.pred = pred

    def __call__(self, *args, **kwargs):
        try:
            return self.result
        except AttributeError:
            pass
        ret = self.pred(*args, **kwargs)
        if ret in (False, None):
            return ret
        self.result = ret
        return self.result


def make_multipred(preds):
    preds = list(map(CachingPredicate, preds))

    def pred(*args, **kwargs):
        results = [pred(*args, **kwargs) for pred in preds]
        if all(results):
            return results
    return pred


def iter_wait(timeout, pred=None, sleep=0.5, message=None,
              progressbar=True, throw=True, allow_interruption=False, caption=None):

    # Calling wait() with a predicate and no message is very not informative
    # (throw=False or message=False disables this behavior)
    if message is False:
        message = None
    elif throw and pred and not message:
        raise Exception(
            "Function iter_wait()'s parameter `message` is required if "
            "`pred` is passed",
        )

    if timeout is None:
        msg = "Waiting indefinitely%s"
    else:
        msg = "Waiting%%s up to %s" % time_duration(timeout)

    if message is None:
        if caption:
            message = "Waiting %s timed out after {duration:.1f} seconds" % (caption,)
        elif pred:
            message = "Waiting on predicate (%s) timed out after {duration:.1f} seconds" % (pred,)
        else:
            message = "Timed out after {duration:.1f} seconds"

    if pred:
        pred_decorator = kwargs_resilient(negligible=['is_final_attempt'])
        if hasattr(pred, "__iter__"):
            pred = make_multipred(map(pred_decorator, pred))
        else:
            pred = pred_decorator(pred)
        if not caption:
            caption = "on predicate (%s)" % pred
    else:
        pred = lambda **kwargs: False
        throw = False

    if caption:
        msg %= " %s" % (caption,)
    else:
        msg %= ""

    if isinstance(sleep, tuple):
        data = list(sleep)  # can't use nonlocal since this module is indirectly used in python2

        def sleep():
            cur, mx = data
            try:
                return cur
            finally:
                data[0] = min(mx, cur*1.5)

    if not IS_A_TTY:
        # can't interrupt
        allow_interruption = False
        progressbar = False

    if progressbar and threading.current_thread() is not threading.main_thread():
        # prevent clutter
        progressbar = False

    if allow_interruption:
        msg += " (hit <ESC> to continue)"

    l_timer = Timer(expiration=timeout)

    with ExitStack() as stack:
        if progressbar:
            from .logging import PROGRESS_BAR
            pr = stack.enter_context(PROGRESS_BAR())
            pr.set_message(msg)

        while True:
            s_timer = Timer()
            expired = l_timer.expired
            ret = pred(is_final_attempt=bool(expired))
            if ret not in (None, False):
                yield ret
                return
            if expired:
                duration = l_timer.stop()
                if throw:
                    if callable(message):
                        message = message()
                    raise TimeoutException(message, duration=duration)
                yield None
                return
            yield l_timer.remain
            sleep_for = sleep() if callable(sleep) else sleep
            if allow_interruption:
                from termenu.keyboard import keyboard_listener
                timer = Timer(expiration=sleep_for-s_timer.elapsed)
                for key in keyboard_listener(heartbeat=0.25):
                    if key == "esc":
                        yield None
                        return
                    if key == "enter":
                        break
                    if timer.expired:
                        break
            else:
                s_timeout = max(0, sleep_for-s_timer.elapsed)
                if l_timer.expiration:
                    s_timeout = min(l_timer.remain, s_timeout)
                time.sleep(s_timeout)


@wraps(iter_wait)
def wait(*args, **kwargs):
    for ret in iter_wait(*args, **kwargs):
        pass
    return ret


def repeat(timeout, callback, sleep=0.5, progressbar=True):
    pred = lambda: callback() and False  # prevent 'wait' from stopping when the callback returns a nonzero
    return wait(timeout, pred=pred, sleep=sleep, progressbar=progressbar, throw=False)


def wait_progress(*args, **kwargs):
    for _ in iter_wait_progress(*args, **kwargs):
        pass


def iter_wait_progress(state_getter, advance_timeout, total_timeout=float("inf"), state_threshold=0, sleep=0.5, throw=True,
                       allow_regression=True, advancer_name=None, progressbar=True):

    ADVANCE_TIMEOUT_MESSAGE = "did not advance for {duration: .1f} seconds"
    TOTAL_TIMEOUT_MESSAGE = "advanced but failed to finish in {duration: .1f} seconds"

    state = state_getter()  # state_getter should return a number, represent current state

    progress = Bunch(state=state, finished=False, changed=False)
    progress.total_timer = Timer(expiration=total_timeout)
    progress.advance_timer = Timer(expiration=advance_timeout)

    def did_advance():
        current_state = state_getter()
        progress.advanced = progress.state > current_state
        progress.changed = progress.state != current_state
        if progress.advanced or allow_regression:
            progress.state = current_state
        return progress.advanced

    # We want to make sure each iteration sleeps at least once,
    # since the internal 'wait' could return immediately without sleeping at all,
    # and if the external while loop isn't done we could be iterating too much
    min_sleep = None

    while progress.state > state_threshold:
        progress.timeout, message = min(
            (progress.total_timer.remain, TOTAL_TIMEOUT_MESSAGE),
            (progress.advance_timer.remain, ADVANCE_TIMEOUT_MESSAGE))
        if advancer_name:
            message = advancer_name + ' ' + message

        if min_sleep:
            wait(min_sleep.remain)
        min_sleep = Timer(expiration=sleep)

        result = wait(progress.timeout, pred=did_advance, sleep=sleep, message=message, throw=throw, progressbar=progressbar)
        if not result:  # if wait times out without throwing
            return

        if progress.total_timer.expired:
            raise TimeoutException(message, duration=progress.total_timer.duration)

        progress.advance_timer.reset()
        yield progress

    progress.finished = True
    yield progress  # indicate success


@parametrizeable_decorator
def at_period(func, period=None):
    if not period:
        raise NotImplementedError('must specify a period')
    timer = Timer(expiration=period)

    def inner(*args, **kwargs):
        if timer.expired:
            ret = func(*args, **kwargs)
            timer.reset()
            return ret
    return inner


class StateTimeHistogram(object):
    def __init__(self):
        self._state = None
        self._states_times = {}
        self._timer = Timer()

    def _update_state_time(self, states_times=None):
        if states_times is None:
            states_times = self._states_times
        if self._state is not None:
            states_times[self._state] = states_times.get(self._state, 0) + self._timer.elapsed

    def finish(self):
        self._update_state_time()
        self._state = None
        self._timer.stop()

    def set_state(self, state):
        self._update_state_time()
        self._state = state
        self._timer.reset()

    @property
    def states_times(self):
        states_times = dict(self._states_times)
        self._update_state_time(states_times)
        return states_times
