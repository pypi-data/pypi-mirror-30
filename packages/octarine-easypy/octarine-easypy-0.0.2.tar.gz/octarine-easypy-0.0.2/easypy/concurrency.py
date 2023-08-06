# encoding: utf-8

from concurrent.futures import ThreadPoolExecutor, CancelledError, as_completed, Future, wait as futures_wait
from concurrent.futures import TimeoutError as FutureTimeoutError

import re
from collections import defaultdict, Counter
from contextlib import contextmanager, ExitStack
from functools import partial, wraps
from importlib import import_module
from itertools import chain
from traceback import format_tb, extract_stack
import atexit
import inspect
import logging
import os
import signal
import threading
import time
import warnings

from easypy.decorations import parametrizeable_decorator
from easypy.exceptions import TException, PException
from easypy.gevent import is_module_patched, non_gevent_sleep, defer_to_thread
from easypy.humanize import IndentableTextBuffer, time_duration
from easypy.misc import Hex
from easypy.humanize import format_thread_stack
from easypy.threadtree import iter_thread_frames
from easypy.timing import Timer, TimeoutException
from easypy.units import NEVER, MINUTE, HOUR


this_module = import_module(__name__)


MAX_THREAD_POOL_SIZE = 50


def async_raise_in_main_thread(exc, use_concurrent_loop=True):
    """
    Uses a unix signal to raise an exception to be raised in the main thread.
    """

    from plumbum import local
    pid = os.getpid()
    if not REGISTERED_SIGNAL:
        raise NotInitialized()

    # sometimes the signal isn't caught by the main-thread, so we should try a few times (WEKAPP-14543)
    def do_signal(raised_exc):
        global LAST_ERROR
        if LAST_ERROR is not raised_exc:
            _logger.debug("MainThread took the exception - we're done here")
            if use_concurrent_loop:
                raiser.stop()
            return

        _logger.info("Raising %s in main thread", type(LAST_ERROR))
        local.cmd.kill("-%d" % REGISTERED_SIGNAL, pid)

    if use_concurrent_loop:
        raiser = concurrent(do_signal, raised_exc=exc, loop=True, sleep=30, daemon=True, throw=False)
        raiser.start()
    else:
        do_signal(exc)


if is_module_patched("threading"):
    import gevent
    MAX_THREAD_POOL_SIZE = 5000  # these are not threads anymore, but greenlets. so we allow a lot of them

    def _rimt(exc):
        _logger.info('YELLOW<<killing main thread greenlet>>')
        main_thread_greenlet = threading.main_thread()._greenlet
        orig_throw = main_thread_greenlet.throw

        # we must override "throw" method so exception will be raised with the original traceback
        def throw(*args):
            if len(args) == 1:
                ex = args[0]
                return orig_throw(ex.__class__, ex, ex.__traceback__)
            return orig_throw(*args)
        main_thread_greenlet.throw = throw
        gevent.kill(main_thread_greenlet, exc)
        _logger.debug('exiting the thread that failed')
        raise exc
else:
    _rimt = async_raise_in_main_thread


_logger = logging.getLogger(__name__)
_verbose_logger = logging.getLogger('%s.locks' % __name__)  # logger for less important logs of RWLock.


_disabled = False


def disable():
    global _disabled
    _disabled = True
    logging.info("Concurrency disabled")


def enable():
    global _disabled
    _disabled = False
    logging.info("Concurrency enabled")


class ThreadTimeoutException(TException):
    template = "Thread timeout during execution {func}"


class ProcessExiting(TException):
    template = "Aborting thread - process is exiting"


class TimebombExpired(TException):
    template = "Timebomb Expired - process killed itself"
    exit_with_code = 234


class LockLeaseExpired(TException):
    template = "Lock Lease Expired - thread is holding this lock for too long"


_exiting = False  # we use this to break out of lock-acquisition loops


@atexit.register
def break_locks():
    global _exiting
    _exiting = True


def _check_exiting():
    if _exiting:
        raise ProcessExiting()


class MultiException(PException):

    template = "Exceptions raised from concurrent invocation ({0.common_type.__qualname__} x{0.count}/{0.invocations_count})"

    def __init__(self, exceptions, futures):
        # we want to keep futures in parallel with exceptions,
        # so some exceptions could be None
        assert len(futures) == len(exceptions)
        self.actual = list(filter(None, exceptions))
        self.count = len(self.actual)
        self.invocations_count = len(futures)
        self.common_type = concestor(*map(type, self.actual))
        self.one = self.actual[0] if self.actual else None
        self.futures = futures
        self.exceptions = exceptions
        self.complete = self.count == self.invocations_count
        if self.complete and hasattr(self.common_type, 'exit_with_code'):
            self.exit_with_code = self.common_type.exit_with_code
        super().__init__(self.template, self)

    def __repr__(self):
        return "{0.__class__.__name__}(<{0.common_type.__qualname__} x{0.count}/{0.invocations_count}>)".format(self)

    def __str__(self):
        return self.render(traceback=False, color=False)

    def walk(self, skip_multi_exceptions=True):
        if not skip_multi_exceptions:
            yield self
        for exc in self.actual:
            if isinstance(exc, MultiException):
                yield from exc.walk(skip_multi_exceptions=skip_multi_exceptions)
            else:
                yield exc

    def render(self, *, width=80, **kw):
        buff = self._get_buffer(**kw)
        return "\n"+buff.render(width=width)

    def _get_buffer(self, **kw):
        color = kw.get("color", True)
        buff = IndentableTextBuffer("{0.__class__.__qualname__}", self)
        if self.message:
            buff.write(("WHITE<<%s>>" % self.message) if color else self.message)

        traceback_fmt = "DARK_GRAY@{{{}}}@" if color else "{}"

        # workaround incompatibilty with rpyc, which serializes .actual into an str
        # instead of a list of exceptions. This makes the string flatten into a long
        # and incomprehensible text buffer.
        if hasattr(self, "_remote_tb"):
            with buff.indent("Remote Traceback:"):
                buff.write(self._remote_tb)
            return buff

        for exc in self.actual:
            with buff.indent("{.__class__.__qualname__}", exc):
                if isinstance(exc, self.__class__):
                    buff.extend(exc._get_buffer(**kw))
                elif hasattr(exc, "render"):
                    buff.write(exc.render(**kw))
                else:
                    if not hasattr(exc, "context"):
                        context = ""
                    elif not isinstance(exc.context, dict):
                        context = repr(exc)
                    else:
                        context = exc.context.copy()
                        context.pop("indentation", None)
                        if 'context' in context:  # 'context' should be renamed 'breadcrumbs'
                            context['context'] = ";".join(context['context'])
                        context = "(%s)" % ", ".join("%s=%s" % p for p in sorted(context.items()))
                    buff.write("{}: {}", exc, context)
                if hasattr(exc, "__traceback__"):
                    show_traceback = getattr(exc, 'traceback', None)
                    if show_traceback != False:
                        for line in format_tb(exc.__traceback__):
                            buff.write(traceback_fmt, line.rstrip())
        return buff


class Futures(list):

    def done(self):
        return all(f.done() for f in self)

    def cancelled(self):
        return all(f.cancelled() for f in self)

    def running(self):
        return all(f.running() for f in self)

    def wait(self, timeout=None):
        return futures_wait(self, timeout=timeout)

    def result(self, timeout=None):
        me = self.exception(timeout=timeout)
        if me:
            raise me
        return [f.result() for f in self]

    def exception(self, timeout=None):
        exceptions = [f.exception(timeout=timeout) for f in self]
        if any(exceptions):
            return MultiException(exceptions=exceptions, futures=self)

    def cancel(self):
        cancelled = [f.cancel() for f in self]  # list-comp, to ensure we call cancel on all futures
        return all(cancelled)

    def as_completed(self, timeout=None):
        return as_completed(self, timeout=timeout)

    @classmethod
    @contextmanager
    def executor(cls, workers=MAX_THREAD_POOL_SIZE, ctx={}):
        futures = cls()
        with ThreadPoolExecutor(workers) as executor:
            def submit(func, *args, log_ctx={}, **kwargs):
                _ctx = dict(ctx, **log_ctx)
                future = executor.submit(_run_with_exception_logging, func, args, kwargs, _ctx)
                future.ctx = _ctx
                future.funcname = _get_func_name(func)
                futures.append(future)
                return future
            futures.submit = submit
            futures.shutdown = executor.shutdown
            yield futures
        futures.result()  # bubble up any exceptions

    def dump_stacks(self, futures=None, verbose=False):
        futures = futures or self
        frames = dict(iter_thread_frames())
        for i, future in enumerate(futures, 1):
            try:
                frame = frames[future.ctx['thread_ident']]
            except KeyError:
                frame = None  # this might happen in race-conditions with a new thread starting
            if not verbose or not frame:
                if frame:
                    location = " - %s:%s, in %s(..)" % tuple(extract_stack(frame)[-1][:3])
                else:
                    location = "..."
                _logger.info("%3s - %s (DARK_YELLOW<<%s>>)%s",
                             i, future.funcname, _get_context(future), location)
                continue

            with _logger.indented("%3s - %s (%s)", i, future.funcname, _get_context(future), footer=False):
                lines = format_thread_stack(frame, skip_modules=[this_module]).splitlines()
                for line in lines:
                    _logger.info(line.strip())

    def logged_wait(self, timeout=None, initial_log_interval=None):
        log_interval = initial_log_interval or 2*MINUTE
        global_timer = Timer(expiration=timeout)
        iteration = 0

        while not global_timer.expired:
            completed, pending = self.wait(log_interval)
            if not pending:
                break

            iteration += 1
            if iteration % 5 == 0:
                log_interval *= 5
            with _logger.indented("(Waiting for %s on %s/%s tasks...)",
                                  time_duration(global_timer.elapsed),
                                  len(pending), sum(map(len, (completed, pending))),
                                  level=logging.WARNING, footer=False):
                self.dump_stacks(pending, verbose=global_timer.elapsed >= HOUR)


def _run_with_exception_logging(func, args, kwargs, ctx):
    with _logger.context(**ctx):
        ctx['thread_ident'] = Hex(threading.current_thread().ident)
        try:
            return func(*args, **kwargs)
        except StopIteration:
            # no need to log this
            raise
        except Exception:
            _logger.silent_exception("Exception in thread running %s (traceback in debug logs)", func)
            raise


def _to_args_list(params):
    return [args if isinstance(args, tuple) else (args,) for args in params]


def _get_func_name(func):
    kw = {}
    while isinstance(func, partial):
        if func.keywords:
            kw.update(func.keywords)
        func = func.func
    funcname = func.__qualname__
    if kw:
        funcname += "(%s)" % ", ".join("%s=%r" % p for p in sorted(kw.items()))
    return funcname


def _to_log_contexts(params, log_contexts):
    if not log_contexts:
        log_contexts = (dict(context=str(p) if len(p) > 1 else str(p[0])) for p in params)
    else:
        log_contexts = (p if isinstance(p, dict) else dict(context=str(p))
                        for p in log_contexts)
    return log_contexts


def _get_context(future):
    ctx = dict(future.ctx)
    context = "%X;" % ctx.pop("thread_ident", 0)
    context += ctx.pop("context", "")
    context += ";".join("%s=%s" % p for p in sorted(ctx.items()))
    return context


@contextmanager
def async(func, params=None, workers=None, log_contexts=None, final_timeout=2.0, **kw):
    if params is None:
        params = [()]
    if not isinstance(params, list):
        params = [params]
    params = _to_args_list(params)
    log_contexts = _to_log_contexts(params, log_contexts)

    workers = workers or min(MAX_THREAD_POOL_SIZE, len(params))
    executor = ThreadPoolExecutor(workers) if workers else None

    funcname = _get_func_name(func)

    try:
        signature = inspect.signature(func)
    except ValueError:
        # In Python 3.5+, inspect.signature returns this for built-in types
        pass
    else:
        if '_sync' in signature.parameters and '_sync' not in kw:
            assert len(params) <= executor._max_workers, 'SynchronizationCoordinator with %s tasks but only %s workers' % (
                len(params), executor._max_workers)
            synchronization_coordinator = SynchronizationCoordinator(len(params))
            kw['_sync'] = synchronization_coordinator

            func = synchronization_coordinator._abandon_when_done(func)

    futures = Futures()
    for args, ctx in zip(params, log_contexts):
        future = executor.submit(_run_with_exception_logging, func, args, kw, ctx)
        future.ctx = ctx
        future.funcname = funcname
        futures.append(future)

    def kill(wait=False):
        nonlocal killed
        futures.cancel()
        if executor:
            executor.shutdown(wait=wait)
        killed = True

    killed = False
    futures.kill = kill

    try:
        yield futures
    except:
        _logger.debug("shutting down ThreadPoolExecutor due to exception")
        kill(wait=False)
        raise
    else:
        if executor:
            executor.shutdown(wait=not killed)
        if not killed:
            # force exceptions to bubble up
            try:
                futures.result(timeout=final_timeout)
            except CancelledError:
                pass
    finally:
        # break the cycle so that the GC doesn't clean up the executor under a lock (https://bugs.python.org/issue21009)
        futures.kill = None
        futures = None


def concurrent_find(func, params, **kw):
    timeout = kw.pop("concurrent_timeout", None)
    with async(func, list(params), **kw) as futures:
        future = None
        try:
            for future in futures.as_completed(timeout=timeout):
                if not future.exception() and future.result():
                    futures.kill()
                    return future.result()
            else:
                if future:
                    return future.result()
        except FutureTimeoutError as exc:
            if not timeout:
                # ??
                raise
            futures.kill()
            _logger.warning("Concurrent future timed out (%s)", exc)


def nonconcurrent_map(func, params, log_contexts=None, **kw):
    futures = Futures()
    log_contexts = _to_log_contexts(params, log_contexts)
    has_exceptions = False
    for args, ctx in zip(_to_args_list(params), log_contexts):
        future = Future()
        futures.append(future)
        try:
            result = _run_with_exception_logging(func, args, kw, ctx)
        except Exception as exc:
            has_exceptions = True
            future.set_exception(exc)
        else:
            future.set_result(result)

    if has_exceptions:
        exceptions = [f.exception() for f in futures]
        raise MultiException(exceptions=exceptions, futures=futures)

    results = [f.result() for f in futures]
    del futures[:]
    return results


def concurrent_map(func, params, workers=None, log_contexts=None, initial_log_interval=None, **kw):
    if _disabled or len(params) == 1:
        return nonconcurrent_map(func, params, log_contexts, **kw)

    with async(func, list(params), workers, log_contexts, **kw) as futures:
        futures.logged_wait(initial_log_interval=initial_log_interval)
        return futures.result()


_LIST_DEPRECATION_MESSAGE = "MultiObject should not be used as a list"


class MultiObject(object):

    def __init__(self, items=None, log_ctx=None, workers=None, initial_log_interval=None):
        self._items = list(items) if items else []
        self._workers = workers
        self._initial_log_interval = initial_log_interval
        cstr = concestor(*map(type, self))
        if hasattr(cstr, '_multiobject_log_ctx'):
            # override the given log_ctx if the new items have it
            # some objects (Plumbum Cmd) are expensive to just get the attribute, so we require it
            # on the base class
            self._log_ctx = [item._multiobject_log_ctx for item in self._items]
        elif callable(log_ctx):
            self._log_ctx = list(map(log_ctx, self._items))
        elif log_ctx:
            self._log_ctx = list(log_ctx)
        elif issubclass(cstr, str):
            self._log_ctx = [dict(context="%s" % item) for item in self._items]
        else:
            self._log_ctx = [dict(context="%s<M%03d>" % (cstr.__name__, i)) for i, item in enumerate(self._items)]

        if self._workers is None and hasattr(cstr, '_multiobject_workers'):
            _workers = cstr._multiobject_workers
            if _workers == -1:
                self._workers = len(self._items) or None
            else:
                self._workers = _workers

    @property
    def L(self):
        return list(self)

    @property
    def C(self):
        from .collections import ListCollection
        return ListCollection(self)

    def __getattr__(self, attr):
        if attr.startswith("_"):
            raise AttributeError()
        get = lambda obj: getattr(obj, attr)
        ret = concurrent_map(get, self, log_contexts=self._log_ctx, workers=self._workers)
        return self._new(ret)

    def __call__(self, *args, **kwargs):
        if not self:
            return self._new(self)
        for obj in self:
            if not callable(obj):
                raise Exception("%s is not callable" % obj)

        def do_it(obj, **more_kwargs):
            more_kwargs.update(kwargs)
            return obj(*args, **more_kwargs)

        if all(hasattr(obj, "__qualname__") for obj in self):
            do_it = wraps(obj)(do_it)
        else:
            common_typ = concestor(*map(type, self))
            do_it.__qualname__ = common_typ.__qualname__
        initial_log_interval = kwargs.pop("initial_log_interval", None)
        ret = concurrent_map(
            do_it, self,
            log_contexts=self._log_ctx,
            workers=self._workers,
            initial_log_interval=initial_log_interval)
        return self._new(ret)

    def __dir__(self):
        return sorted(set.intersection(*(set(dir(obj)) for obj in self)))
    trait_names = __dir__

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, key):
        warnings.warn(_LIST_DEPRECATION_MESSAGE, PendingDeprecationWarning, stacklevel=2)
        ret = self._items[key]
        if isinstance(key, slice):
            return self._new(ret, self._log_ctx[key])
        else:
            return ret

    # === Mutation =====
    # TODO: ensure the relationship between items/workers/logctx
    def __delitem__(self, key):
        warnings.warn(_LIST_DEPRECATION_MESSAGE, PendingDeprecationWarning, stacklevel=2)
        del self._log_ctx[key]
        del self._items[key]

    def __len__(self):
        return len(self._items)

    def __add__(self, other):
        return self.__class__(chain(self, other))

    def __iadd__(self, other):
        self._log_ctx.extend(other._log_ctx)
        return self._items.extend(other)

    def sort(self, *args, **kwargs):
        order = {id(obj): log_ctx for (obj, log_ctx) in zip(self._items, self._log_ctx)}
        ret = self._items.sort(*args, **kwargs)
        self._log_ctx[:] = [order[id(obj)] for obj in self._items]
        return ret

    def append(self, item, *, log_ctx=None):
        warnings.warn(_LIST_DEPRECATION_MESSAGE, PendingDeprecationWarning, stacklevel=2)

        self._log_ctx.append(log_ctx)
        return self._items.append(item)

    def insert(self, pos, item, *, log_ctx=None):
        warnings.warn(_LIST_DEPRECATION_MESSAGE, PendingDeprecationWarning, stacklevel=2)

        self._log_ctx.insert(pos, log_ctx)
        return self._items.insert(pos, item)

    def pop(self, *args):
        warnings.warn(_LIST_DEPRECATION_MESSAGE, PendingDeprecationWarning, stacklevel=2)

        self._log_ctx.pop(*args)
        return self._items.pop(*args)

    # ================

    def __repr__(self):
        common_typ = concestor(*map(type, self))
        if common_typ:
            return "<MultiObject '%s' (x%s/%s)>" % (common_typ.__name__, len(self), self._workers)
        else:
            return "<MultiObject (Empty)>"

    def _new(self, items=None, ctxs=None, workers=None, initial_log_interval=None):
        return self.__class__(
            self._items if items is None else items,
            self._log_ctx if ctxs is None else ctxs,
            self._workers if workers is None else workers,
            self._initial_log_interval if initial_log_interval is None else initial_log_interval)

    def with_workers(self, workers):
        "Return a new MultiObject based on current items with the specified number of workers"
        return self._new(workers=workers)

    def call(self, func, *args, **kw):
        "Concurrently call a function on each of the object contained by this MultiObject (as first param)"
        initial_log_interval = kw.pop("initial_log_interval", self._initial_log_interval)
        if kw:
            func = wraps(func)(partial(func, **kw))
        params = [((item,) + args) for item in self] if args else self
        return self._new(concurrent_map(
            func, params,
            log_contexts=self._log_ctx,
            workers=self._workers,
            initial_log_interval=initial_log_interval), initial_log_interval=initial_log_interval)
    each = call

    def filter(self, pred):
        if not pred:
            pred = bool
        filtering = self.call(pred)
        filtered = [t for (*t, passed) in zip(self, self._log_ctx, filtering) if passed]
        return self._new(*(zip(*filtered) if filtered else ((),())))

    def chain(self):
        "Chain the iterables contained by this MultiObject"
        return self.__class__(chain(*self))

    def zip_with(self, *collections):
        mo = self._new(zip(self, *collections))
        assert len(mo) == len(self), "All collection must have at least %s items" % len(self)
        return mo

    def enumerate(self, start=0):
        """
        Replaces this pattern, which loses the log contexts:
            >> MultiObject(enumerate(items)).call(lambda idx, item: ...)
        with this pattern, which retains log contexts:
            >> MultiObject(items).enumerate().call(lambda idx, item: ...)
        """
        return self._new(zip(range(start, start + len(self)), self))

    def zip(self):
        "Concurrently iterate through the iterables contained by this MultiObject"
        iters = list(map(iter, self))
        while True:
            try:
                ret = concurrent_map(next, iters, log_contexts=self._log_ctx, workers=self._workers)
            except MultiException as me:
                if me.common_type == StopIteration and me.complete:
                    break
                raise
            else:
                yield self._new(ret)

    def concurrent_find(self, func=lambda f: f(), **kw):
        return concurrent_find(func, self, log_contexts=self._log_ctx, workers=self._workers, **kw)

    def __enter__(self):
        return self.call(lambda obj: obj.__enter__())

    def __exit__(self, *args):
        self.call(lambda obj: obj.__exit__(*args))


def concestor(*cls_list):
    "Closest common ancestor class"
    mros = [list(inspect.getmro(cls)) for cls in cls_list]
    track = defaultdict(int)
    while mros:
        for mro in mros:
            cur = mro.pop(0)
            track[cur] += 1
            if track[cur] == len(cls_list):
                return cur
            if len(mro) == 0:
                mros.remove(mro)
    return object  # the base-class that rules the all


LAST_ERROR = None
REGISTERED_SIGNAL = None


class Error(TException):
    pass


class NotMainThread(Error):
    template = "Binding must be invoked from main thread"


class SignalAlreadyBound(Error):
    template = "Signal already bound to another signal handler(s)"


class LastErrorEmpty(Error):
    template = "Signal caught, but no error to raise"


class NotInitialized(Error):
    template = "Signal type not initialized, must use bind_to_subthread_exceptions in the main thread"


class TerminationSignal(TException):
    template = "Process got a termination signal: {_signal}"


def initialize_exception_listener():  # must be invoked in main thread in "geventless" runs in order for raise_in_main_thread to work
    global REGISTERED_SIGNAL
    if REGISTERED_SIGNAL:
        # already registered
        return

    if threading.current_thread() is not threading.main_thread():
        raise NotMainThread()

    def handle_signal(sig, stack):
        global LAST_ERROR
        error = LAST_ERROR
        LAST_ERROR = None
        if error:
            raise error
        raise LastErrorEmpty(signal=sig)

    custom_signal = signal.SIGUSR1
    if signal.getsignal(custom_signal) in (signal.SIG_DFL, signal.SIG_IGN):  # check if signal is already trapped
        signal.signal(custom_signal, handle_signal)
        REGISTERED_SIGNAL = custom_signal
    else:
        raise SignalAlreadyBound(signal=custom_signal)


@contextmanager
def raise_in_main_thread(exception_type=Exception):

    try:
        yield
    except ProcessExiting:
        # this exception is meant to stay within the thread
        raise
    except exception_type as exc:
        if threading.current_thread() is threading.main_thread():
            raise
        exc._raised_asynchronously = True

        global LAST_ERROR
        if LAST_ERROR:
            _logger.warning("a different error (%s) is pending - skipping", type(LAST_ERROR))
            raise
        LAST_ERROR = exc
        _rimt(exc)


def initialize_termination_listener(sig=signal.SIGTERM, _registered=[]):
    if _registered:
        # already registered
        return
    _registered.append(True)

    def handle_signal(sig, stack):
        _logger.error("RED<<SIGNAL %s RECEIVED>>", sig)
        raise TerminationSignal(_signal=sig)

    if signal.getsignal(sig) in (signal.SIG_DFL, signal.SIG_IGN):  # check if signal is already trapped
        _logger.info("Listening to signal %s", sig)
        signal.signal(sig, handle_signal)
    else:
        raise SignalAlreadyBound(signal=sig)


def kill_subprocesses():
    from plumbum import local
    pid = os.getpid()
    return local.cmd.pkill['-HUP', '-P', pid].run(retcode=None)


def kill_this_process(graceful=False):
    from plumbum import local
    pid = os.getpid()
    if graceful:
        flag = '-HUP'
    else:
        flag = '-9'
    local.cmd.kill(flag, pid)


class Timebomb(object):

    def __init__(self, timeout, alert_interval=None, quiet=False):
        self.fuse = threading.Event()  # use this to cancel the timebomb
        self.timeout = timeout
        self.alert_interval = alert_interval
        self.quiet = quiet

    def __enter__(self):
        return self.start()

    def __exit__(self, *args):
        self.cancel()

    def start(self):
        self.t = concurrent(self.wait_and_kill, daemon=True, threadname="Timebomb(%s)" % self.timeout)
        self.t.start()
        return self

    def cancel(self):
        self.fuse.set()

    @raise_in_main_thread()
    def wait_and_kill(self):
        timer = Timer(expiration=self.timeout)
        if not self.quiet:
            _logger.info("Timebomb set - this process will YELLOW<<self-destruct>> in RED<<%r>>...", timer.remain)
        while not timer.expired:
            if self.alert_interval:
                _logger.info("Time Elapsed: MAGENTA<<%r>>", timer.elapsed)
            log_level = logging.WARNING if timer.remain < 5*MINUTE else logging.DEBUG
            _logger.log(log_level, "This process will YELLOW<<self-destruct>> in RED<<%r>>...", timer.remain)
            if self.fuse.wait(min(self.alert_interval or 60, timer.remain)):
                _logger.info("Timebomb cancelled")
                return
        _logger.warning("RED<< 💣 Timebomb Expired! 💣 >>")
        with _logger.indented("Killing children"):
            kill_subprocesses()
        with _logger.indented("Committing suicide"):
            kill_this_process(graceful=False)
            raise Exception("Timebomb Expired")


def set_timebomb(timeout, alert_interval=None):
    return Timebomb(timeout=timeout, alert_interval=alert_interval).start()


class concurrent(object):

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.throw = kwargs.pop('throw', True)
        self.daemon = kwargs.pop('daemon', True)
        self.threadname = kwargs.pop('threadname', 'anon-%X' % id(self))
        self.stopper = kwargs.pop('stopper', threading.Event())
        self.sleep = kwargs.pop('sleep', 1)
        self.loop = kwargs.pop('loop', False)
        self.timer = None

        real_thread_no_greenlet = kwargs.pop('real_thread_no_greenlet', False)
        if is_module_patched("threading"):
            # in case of using apply_gevent_patch function - use this option in order to defer some jobs to real threads
            self.real_thread_no_greenlet = real_thread_no_greenlet
        else:
            # gevent isn't active, no need to do anything special
            self.real_thread_no_greenlet = False

        rimt = kwargs.pop("raise_in_main_thread", False)
        if rimt:
            exc_type = Exception if rimt is True else rimt
            self.func = raise_in_main_thread(exc_type)(self.func)

    def __repr__(self):
        flags = ""
        if self.daemon:
            flags += 'D'
        if self.loop:
            flags += 'L'
        if self.real_thread_no_greenlet:
            flags += 'T'
        return "<%s[%s] '%s'>" % (self.__class__.__name__, self.threadname, flags)

    def _logged_func(self):
        self.timer = Timer()
        self.exc = None
        try:
            _logger.debug("%s - starting", self)
            while True:
                self.result = self.func(*self.args, **self.kwargs)
                if not self.loop:
                    return
                if self.wait(self.sleep):
                    _logger.debug("%s - stopped", self)
                    return
        except Exception as exc:
            _logger.silent_exception("Exception in thread running %s (traceback can be found in debug-level logs)", self.func)
            self.exc = exc
        finally:
            self.timer.stop()
            self.stop()

    def stop(self):
        _logger.debug("%s - stopping", self)
        self.stopper.set()

    def wait(self, timeout=None):
        if self.real_thread_no_greenlet:
            # we can't '.wait' on this gevent event object, so instead we test it and sleep manually:
            if self.stopper.is_set():
                return True
            non_gevent_sleep(timeout)
            if self.stopper.is_set():
                return True
            return False
        return self.stopper.wait(timeout)

    @contextmanager
    def paused(self):
        self.stop()
        yield
        self.start()

    @contextmanager
    def _running(self):
        if _disabled:
            self._logged_func()
            yield self
            return

        if self.real_thread_no_greenlet:
            _logger.debug('sending job to a real OS thread')
            self._join = defer_to_thread(func=self._logged_func, threadname=self.threadname)
        else:
            # threading.Thread could be a real thread or a gevent-patched thread...
            self.thread = threading.Thread(target=self._logged_func, name=self.threadname, daemon=self.daemon)
            _logger.debug('sending job to %s', self.thread)
            self.stopper.clear()
            self.thread.start()
            self._join = self.thread.join
        try:
            yield self
        finally:
            self.stop()  # if we loop, stop it
        self._join()
        if self.throw and self.exc:
            raise self.exc

    def __enter__(self):
        self._ctx = self._running()
        return self._ctx.__enter__()

    def __exit__(self, *args):
        return self._ctx.__exit__(*args)

    def __iter__(self):
        with self:
            self.iterations = 0
            while not self.wait(self.sleep):
                yield self
                self.iterations += 1

    start = __enter__

    def join(self):
        self.__exit__(None, None, None)

    __del__ = join


@parametrizeable_decorator
def skip_if_locked(func=None, lock=None, default=None):
    if not lock:
        lock = threading.RLock()

    def inner(*args, **kwargs):
        if not lock.acquire(blocking=False):
            _logger.debug("lock acquired - skipped %s", func)
            return default
        try:
            return func(*args, **kwargs)
        finally:
            lock.release()
    return inner


@parametrizeable_decorator
def with_my_lock(method, lock_attribute="_lock"):

    def inner(self, *args, **kwargs):
        ctx = getattr(self, lock_attribute)
        if callable(ctx):
            ctx = ctx()
        with ctx:
            return method(self, *args, **kwargs)

    return inner


@parametrizeable_decorator
def synchronized(func, lock=None):
    if not lock:
        lock = threading.RLock()

    def inner(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)

    return inner


def _get_my_ident():
    return Hex(threading.current_thread().ident)


class LoggedRLock():
    """
    Like RLock, but more logging friendly.

        name: give it a name, so it's identifiable in the logs
        log_interval: the interval between log messages
        lease_expiration: throw an exception if the lock is held for more than this duration
    """

    # we could inherit from this and support other types, but that'll require changes in the repr
    LockType = threading.RLock

    __slots__ = ("_lock", "_name", "_lease_expiration", "_lease_timer", "_log_interval", "_get_data")
    _RE_OWNER = re.compile(".*owner=(\d+) count=(\d+).*")
    _MIN_TIME_FOR_LOGGING = 10

    def __init__(self, name=None, log_interval=15, lease_expiration=NEVER):
        self._lock = self.__class__.LockType()
        self._name = name or '{}-{:X}'.format(self.LockType.__name__, id(self))
        self._lease_expiration = lease_expiration
        self._lease_timer = None
        self._log_interval = log_interval

        # we want to support both the gevent and builtin lock
        try:
            self._lock._owner
        except AttributeError:
            def _get_data():
                return tuple(map(int, self._RE_OWNER.match(repr(self._lock)).groups()))
        else:
            def _get_data():
                return self._lock._owner, self._lock._count
        self._get_data = _get_data

    def __repr__(self):
        owner, count = self._get_data()
        try:
            owner = threading._active[owner].name
        except KeyError:
            pass
        if owner:
            return "<{}, owned by <{}>x{} for {}>".format(self._name, owner, count, self._lease_timer.elapsed)
        else:
            return "<{}, unowned>".format(self._name)

    def _acquired(self, lease_expiration, should_log=False):
        # we don't want to replace the lease timer, so not to effectively extend the original lease
        self._lease_timer = self._lease_timer or Timer(expiration=lease_expiration or self._lease_expiration)
        if should_log:
            _logger.debug("%s - acquired", self)

    def acquire(self, blocking=True, timeout=-1, lease_expiration=None):
        if not blocking:
            ret = self._lock.acquire(blocking=False)
            lease_timer = self._lease_timer  # touch it once, so we don't hit a race since it occurs outside of the lock acquisition
            if ret:
                self._acquired(lease_expiration)
            elif lease_timer and lease_timer.expired:
                raise LockLeaseExpired(lock=self)
            return ret

        # this timer implements the 'timeout' parameter
        acquisition_timer = Timer(expiration=NEVER if timeout < 0 else timeout)
        while not acquisition_timer.expired:

            # the timeout on actually acquiring this lock is the minimum of:
            # 1. the time remaining on the acquisition timer, set by the 'timeout' param
            # 2. the logging interval - the minimal frequency for logging while the lock is awaited
            # 3. the time remaining on the lease timer, which would raise if expired
            timeout = min(acquisition_timer.remain, self._log_interval)
            lease_timer = self._lease_timer  # touch it once, so we don't hit a race since it occurs outside of the lock acquisition
            if lease_timer:
                timeout = min(lease_timer.remain, timeout)

            if self._lock.acquire(blocking=True, timeout=timeout):
                self._acquired(lease_expiration, should_log=acquisition_timer.elapsed > self._MIN_TIME_FOR_LOGGING)
                return True

            lease_timer = self._lease_timer  # touch it once, so we don't hit a race since it occurs outside of the lock acquisition
            if lease_timer and lease_timer.expired:
                raise LockLeaseExpired(lock=self)

            _logger.debug("%s - waiting...", self)

    def release(self, *args):
        _, count = self._get_data()
        if count == 1:
            # we're last: clear the timer before releasing the lock!
            if self._lease_timer.elapsed > self._MIN_TIME_FOR_LOGGING:
                _logger.debug("%s - releasing...", self)
            self._lease_timer = None
        self._lock.release()

    __exit__ = release
    __enter__ = acquire


class RWLock(object):
    """
    Read-Write Lock: allows locking exclusively and non-exclusively:

        rwl = RWLock()

        with rwl:
            # other can acquire this lock, but not exclusively

        with rwl.exclusive():
            # no one can acquire this lock - we are alone here

    """

    def __init__(self, name=None):
        self.lock = threading.RLock()
        self.cond = threading.Condition(self.lock)
        self.owners = Counter()
        self.name = name or '{}-{:X}'.format(self.__class__.__name__, id(self.lock))
        self._lease_timer = None

    def __repr__(self):
        owners = ", ".join(map(str, sorted(self.owners.keys())))
        lease_timer = self._lease_timer  # touch once to avoid races
        if lease_timer:
            mode = "exclusively ({})".format(lease_timer.elapsed)
        else:
            mode = "non-exclusively"
        return "<{}, owned by <{}> {}>".format(self.name, owners, mode)

    @property
    def owner_count(self):
        return sum(self.owners.values())

    def __call__(self):
        return self

    def __enter__(self):
        try:
            while not self.cond.acquire(timeout=15):
                _logger.debug("%s - waiting...", self)
            self.owners[_get_my_ident()] += 1
            _verbose_logger.debug("%s - acquired (non-exclusively)", self)
            return self
        finally:
            self.cond.release()

    def __exit__(self, *args):
        try:
            while not self.cond.acquire(timeout=15):
                _logger.debug("%s - waiting...", self)
            my_ident = _get_my_ident()
            self.owners[my_ident] -= 1
            if not self.owners[my_ident]:
                self.owners.pop(my_ident)  # don't inflate the soft lock keys with threads that does not own it
            self.cond.notify()
            _verbose_logger.debug("%s - released (non-exclusive)", self)
        finally:
            self.cond.release()

    @contextmanager
    def exclusive(self, need_to_wait_message=None):
        while not self.cond.acquire(timeout=15):
            _logger.debug("%s - waiting...", self)

        # wait until this thread is the sole owner of this lock
        while not self.cond.wait_for(lambda: self.owner_count == self.owners[_get_my_ident()], timeout=15):
            _check_exiting()
            if need_to_wait_message:
                _logger.info(need_to_wait_message)
                need_to_wait_message = None  # only print it once
            _logger.debug("%s - waiting (for exclusivity)...", self)
        my_ident = _get_my_ident()
        self.owners[my_ident] += 1
        self._lease_timer = Timer()
        _verbose_logger.debug("%s - acquired (exclusively)", self)
        try:
            yield
        finally:
            _verbose_logger.debug('%s - releasing (exclusive)', self)
            self._lease_timer = None
            self.owners[my_ident] -= 1
            if not self.owners[my_ident]:
                self.owners.pop(my_ident)  # don't inflate the soft lock keys with threads that does not own it
            self.cond.notify()
            self.cond.release()


SoftLock = RWLock


class TagAlongThread(object):

    def __init__(self, func, name, minimal_sleep=0):
        self._func = func
        self.minimal_sleep = minimal_sleep

        self._iteration_trigger = threading.Event()

        self._iterating = threading.Event()
        self._not_iterating = threading.Event()
        self._not_iterating.set()

        self._last_exception = None
        self._last_result = None

        self._thread = threading.Thread(target=self._loop, daemon=True, name=name)
        self._thread.start()

    def _loop(self):
        while True:
            self._iteration_trigger.wait()
            self._iteration_trigger.clear()

            # Mark that we are now iterating
            self._not_iterating.clear()
            self._iterating.set()

            try:
                self._last_exception, self._last_result = None, self._func()
            except Exception as e:
                self._last_exception = e

            # Mark that we are no longer iterating
            self._iterating.clear()
            self._not_iterating.set()

            time.sleep(self.minimal_sleep)

    def __call__(self):
        # We can't use an iteration that's already started - maybe it's already at a too advanced stage?
        if self._iterating.is_set():
            self._not_iterating.wait()

        self._iteration_trigger.set()  # Signal that we want an iteration

        while not self._iterating.wait(1):  # Wait until an iteration starts
            # It is possible that we missed the loop and _iterating was already
            # cleared. If this is the case, _not_iterating will not be set -
            # and we can use it as a signal to stop waiting for iteration.
            if self._not_iterating.is_set():
                break
        else:
            self._not_iterating.wait()  # Wait until it finishes

        # To avoid races, copy last exception and result to local variables
        last_exception, last_result = self._last_exception, self._last_result
        if last_exception:
            raise last_exception
        else:
            return last_result


def throttled(duration):
    """
    Syntax sugar over timecache decorator
    With accent on throttling calls and not actual caching of values
    Concurrent callers will block if function is executing, since they might depend on side effect of function call
    """
    from easypy.caching import timecache
    return timecache(expiration=duration)


class synchronized_on_first_call():
    "Decorator, that make a function synchronized but only on its first invocation"

    def __init__(self, func):
        self.lock = threading.RLock()
        self.func = func
        self.initialized = False

    def __call__(self, *args, **kwargs):
        with ExitStack() as stack:
            with self.lock:
                if not self.initialized:
                    stack.enter_context(self.lock)
            ret = self.func(*args, **kwargs)
            if not self.initialized:
                self.initialized = True
            return ret


class SynchronizedSingleton(type):
    _instances = {}

    @synchronized
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)

        return cls._instances[cls]

    @synchronized
    def get_instance(cls):
        return cls._instances.get(cls)


class SynchronizationCoordinatorWrongWait(TException):
    template = "Task is waiting on {this_file}:{this_line} instead of {others_file}:{others_line}"


class SynchronizationCoordinator(object):
    """
    Synchronization helper for functions that run concurrently.

        sync = SynchronizationCoordinator(5)

        def foo(a):
            sync.wait_for_everyone()
            sync.collect_and_call_once(a, lambda a_values: print(a))

        MultiObject(range(5)).call(foo)

    When MultiObject/concurrent_map/sync runs a function with a _sync=SYNC
    argument, it will replace it with a proper SynchronizationCoordinator instance:

        def foo(a, _sync=SYNC):
            _sync.wait_for_everyone()
            _sync.collect_and_call_once(a, lambda a_values: print(a))

        MultiObject(range(5)).call(foo)
    """

    def __init__(self, num_participants):
        self.num_participants = num_participants
        self._reset_barrier()
        self._lock = threading.Lock()
        self._call_once_collected_param = []
        self._call_once_function = None
        self._call_once_result = None
        self._call_once_raised_exception = False

        self._wait_context = None

    def _reset_barrier(self):
        self.barrier = threading.Barrier(self.num_participants, action=self._post_barrier_action)

    def _post_barrier_action(self):
        if self.num_participants != self.barrier.parties:
            self._reset_barrier()
        self._wait_context = None

        if self._call_once_function:
            call_once_function, self._call_once_function = self._call_once_function, None
            collected_param, self._call_once_collected_param = self._call_once_collected_param, []

            try:
                self._call_once_result = call_once_function(collected_param)
                self._call_once_raised_exception = False
            except BaseException as e:
                self._call_once_result = e
                self._call_once_raised_exception = True

    def wait_for_everyone(self, timeout=HOUR):
        """
        Block until all threads that participate in the synchronization coordinator reach this point.

        Fail if one of the threads is waiting at a different point

            def foo(a, _sync=SYNC):
                sleep(a)
                # Each thread will reach this point at a different time
                _sync.wait_for_everyone()
                # All threads will reach this point together

            MultiObject(range(5)).call(foo)
        """
        self._verify_waiting_on_same_line()
        self.barrier.wait(timeout=timeout)

    def abandon(self):
        """
        Stop participating in this synchronization coordinator.

        Note: when using with MultiObject/concurrent_map/async and _sync=SYNC, this
        is called automatically when a thread terminates on return or on exception.
        """
        with self._lock:
            self.num_participants -= 1
        self.barrier.wait()

    def collect_and_call_once(self, param, func, *, timeout=HOUR):
        """
        Call a function from one thread, with parameters collected from all threads.

            def foo(a, _sync=SYNC):
                result = _sync.collect_and_call_once(a, lambda a_values: set(a_values))
                assert result == {0, 1, 2, 3, 4}

            MultiObject(range(5)).call(foo)
        """
        self._verify_waiting_on_same_line()

        self._call_once_collected_param.append(param)
        self._call_once_function = func  # this will be set multiple times - but there is no race so that's OK

        self.barrier.wait(timeout=timeout)

        if self._call_once_raised_exception:
            raise self._call_once_result
        else:
            return self._call_once_result

    def _verify_waiting_on_same_line(self):
        frame = inspect.currentframe().f_back.f_back
        wait_context = (frame.f_code, frame.f_lineno, frame.f_lasti)

        existing_wait_context = self._wait_context
        if existing_wait_context is None:
            with self._lock:
                # Check again inside the lock, in case it was changed
                existing_wait_context = self._wait_context
                if existing_wait_context is None:
                    self._wait_context = wait_context
        if existing_wait_context is not None:  # could have changed inside the lock
            if wait_context != existing_wait_context:
                self.barrier.abort()
                raise SynchronizationCoordinatorWrongWait(
                    this_file=wait_context[0].co_filename,
                    this_line=wait_context[1],
                    others_file=existing_wait_context[0].co_filename,
                    others_line=existing_wait_context[1])

    def _abandon_when_done(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                if hasattr(result, '__enter__') and hasattr(result, '__exit__'):
                    @contextmanager
                    def wrapper_cm():
                        try:
                            with result as yielded_value:
                                yield yielded_value
                        finally:
                            self.abandon()
                    return wrapper_cm()
                else:
                    self.abandon()
                    return result
            except:
                self.abandon()
                raise
        return wrapper


class SYNC(SynchronizationCoordinator):
    """Mimic SynchronizationCoordinator for running in single thread."""

    def __init__(self):
        pass

    def wait_for_everyone(self):
        pass
    wait_for_everyone.__doc__ = SynchronizationCoordinator.wait_for_everyone.__doc__

    def abandon(self):
        pass
    abandon.__doc__ = SynchronizationCoordinator.abandon.__doc__

    def collect_and_call_once(self, param, func):
        return func([param])
    collect_and_call_once.__doc__ = SynchronizationCoordinator.collect_and_call_once.__doc__


SYNC = SYNC()


class LoggedCondition():
    """
    Like Condition, but easier to use and more logging friendly

        name: give it a name, so it's identifiable in the logs
        log_interval: the interval between log messages

    Unlike threading.condition, .acquire() and .release() are not needed here.
    Just use .wait_for() to wait for a predicate and perform the
    condition-changing statements inside a .notifying_all() context:

        some_flag = False
        cond = Condition('some flag cond')

        # Wait for condition:
        cond.wait_for(lambda: some_flag, 'some flag become True')

        # Trigger the condition:
        with cond.notifying_all('Setting some flag to true'):
            some_flag = True
    """

    ConditionType = threading.Condition

    __slots__ = ("_cond", "_name", "_log_interval")

    def __init__(self, name=None, log_interval=15):
        self._cond = self.__class__.ConditionType()
        self._name = name or '{}-{:X}'.format(self.ConditionType.__name__, id(self))
        self._log_interval = log_interval

    def __repr__(self):
        return '<{}>'.format(self._name)

    @contextmanager
    def _acquired_for(self, msg, *args):
        while not self._cond.acquire(timeout=self._log_interval):
            _logger.debug('%s - waiting to be acquired for ' + msg, self, *args)
        try:
            yield
        finally:
            self._cond.release()

    @contextmanager
    def notifying_all(self, msg, *args):
        """
        Acquire the condition lock for the context, and notify all waiters afterward.

            msg: Message to print to the DEBUG log after performing the command
            args: Format arguments for msg

        Users should run the command that triggers the conditions inside this context manager.
        """
        with self._acquired_for('performing a %s notifying all waiters' % msg, *args):
            yield
            _logger.debug('%s - performed: ' + msg, self, *args)
            self._cond.notifyAll()

    @contextmanager
    def __wait_for_impl(self, pred, msg, *args, timeout=None):
        timer = Timer(expiration=timeout)

        def timeout_for_condition():
            remain = timer.remain
            if remain:
                return min(remain, self._log_interval)
            else:
                return self._log_interval

        with self._acquired_for('checking ' + msg, *args):
            while not self._cond.wait_for(pred, timeout=timeout_for_condition()):
                if timer.expired:
                    # NOTE: without a timeout we will never get here
                    if pred():  # Try one last time, to make sure the last check was not (possibly too long) before the timeout
                        return
                    raise TimeoutException('{condition} timed out after {duration} waiting for {msg}',
                                           condition=self, msg=msg % args, duration=timer.elapsed)
                _logger.debug('%s - waiting for ' + msg, self, *args)
            yield

    def wait_for(self, pred, msg, *args, timeout=None):
        """
        Wait for a predicate. Only check it when notified.

            msg: Message to print to the DEBUG log while waiting for the predicate
            args: Format arguments for msg
            timeout: Maximal time to wait
        """
        with self.__wait_for_impl(pred, msg, *args, timeout=timeout):
            pass

    @contextmanager
    def waited_for(self, pred, msg, *args, timeout=None):
        """
        Wait for a predicate, keep the condition lock for the context, and notify all other waiters afterward.

            msg: Message to print to the DEBUG log while waiting for the predicate
            args: Format arguments for msg
            timeout: Maximal time to wait

        The code inside the context should be used for altering state other waiters are waiting for.
        """
        with self.__wait_for_impl(pred, msg, *args, timeout=timeout):
            yield
            self._cond.notifyAll()

    @property
    def lock(self):
        """
        Use the underlying lock without notifying the waiters.
        """

        return self._cond._lock
