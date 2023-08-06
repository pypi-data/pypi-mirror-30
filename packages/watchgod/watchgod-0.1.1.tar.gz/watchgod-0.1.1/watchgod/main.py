import asyncio
import logging
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from multiprocessing import Process
from pathlib import Path
from time import sleep, time
from typing import Any, Awaitable, Callable, Dict, Set, Tuple, Type, Union

from .watcher import AllWatcher, Change, DefaultWatcher, PythonWatcher

__all__ = 'watch', 'awatch', 'run_process', 'arun_process'
logger = logging.getLogger('watchgod.main')


def unix_ms():
    return int(round(time() * 1000))


def watch(path: Union[Path, str], *,
          watcher_cls: Type[AllWatcher]=DefaultWatcher,
          debounce=400,
          min_sleep=100,
          stop_event=None):
    """
    Watch a directory and yield a set of changes whenever files change in that directory or its subdirectories.
    """
    w = watcher_cls(path)
    try:
        while True:
            if stop_event and stop_event.is_set():
                return
            start = unix_ms()
            changes = w.check()
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('time=%0.0fms files=%d changes=%d', unix_ms() - start, len(w.files), len(changes))

            if changes:
                yield changes

            sleep_time = max(debounce - (unix_ms() - start), min_sleep)
            sleep(sleep_time / 1000)
    except KeyboardInterrupt:
        logger.debug('KeyboardInterrupt, exiting')


def correct_aiter(func):  # pragma: no cover
    if sys.version_info >= (3, 5, 2):
        return func
    else:
        return asyncio.coroutine(func)


class awatch:
    """
    asynchronous equivalent of watch using a threaded executor.

    3.5 doesn't support yield in coroutines so we need all this fluff. Yawwwwn.
    """
    __slots__ = (
        '_loop', '_path', '_watcher_cls', '_debounce', '_min_sleep', '_stop_event', '_start', '_w', 'lock', '_executor'
    )

    def __init__(self, path: Union[Path, str], *,
                 watcher_cls: Type[AllWatcher]=DefaultWatcher,
                 debounce=400,
                 min_sleep=100,
                 stop_event: asyncio.Event=None):
        self._loop = asyncio.get_event_loop()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._path = path
        self._watcher_cls = watcher_cls
        self._debounce = debounce
        self._min_sleep = min_sleep
        self._stop_event = stop_event
        self._start = 0
        self._w = None
        self.lock = asyncio.Lock()

    @correct_aiter
    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._w:
            self._w = await self.run_in_executor(self._watcher_cls, self._path)
        while True:
            if self._stop_event and self._stop_event.is_set():
                raise StopAsyncIteration()
            async with self.lock:
                if self._start:
                    sleep_time = max(self._debounce - (unix_ms() - self._start), self._min_sleep)
                    await asyncio.sleep(sleep_time / 1000)

                self._start = unix_ms()
                changes = await self.run_in_executor(self._w.check)
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug('time=%0.0fms files=%d changes=%d',
                                 unix_ms() - self._start, len(self._w.files), len(changes))

                if changes:
                    return changes

    async def run_in_executor(self, func, *args):
        return await self._loop.run_in_executor(self._executor, func, *args)

    def __del__(self):
        self._executor.shutdown()


def _start_process(target, args, kwargs):
    process = Process(target=target, args=args, kwargs=kwargs or {})
    process.start()
    return process


def _stop_process(process):
    if process.is_alive():
        logger.debug('stopping process...')
        os.kill(process.pid, signal.SIGINT)
        process.join(5)
        if process.exitcode is None:
            logger.warning('process has not terminated, sending SIGKILL')
            os.kill(process.pid, signal.SIGKILL)
            process.join(1)
        else:
            logger.debug('process stopped')
    else:
        logger.warning('process already dead, exit code: %d', process.exitcode)


def run_process(path: Union[Path, str], target: Callable, *,
                args: Tuple=(),
                kwargs: Dict[str, Any]=None,
                callback: Callable[[Set[Tuple[Change, str]]], None]=None,
                watcher_cls: Type[AllWatcher]=PythonWatcher,
                debounce=400,
                min_sleep=100):
    """
    Run a function in a subprocess using multiprocessing.Process, restart it whenever files change in path.
    """

    process = _start_process(target=target, args=args, kwargs=kwargs)
    reloads = 0

    for changes in watch(path, watcher_cls=watcher_cls, debounce=debounce, min_sleep=min_sleep):
        callback and callback(changes)
        _stop_process(process)
        process = _start_process(target=target, args=args, kwargs=kwargs)
        reloads += 1
    return reloads


async def arun_process(path: Union[Path, str], target: Callable, *,
                       args: Tuple[Any]=(),
                       kwargs: Dict[str, Any]=None,
                       callback: Callable[[Set[Tuple[Change, str]]], Awaitable]=None,
                       watcher_cls: Type[AllWatcher]=PythonWatcher,
                       debounce=400,
                       min_sleep=100):
    """
    Run a function in a subprocess using multiprocessing.Process, restart it whenever files change in path.
    """
    watcher = awatch(path, watcher_cls=watcher_cls, debounce=debounce, min_sleep=min_sleep)
    start_process = partial(_start_process, target=target, args=args, kwargs=kwargs)
    process = await watcher.run_in_executor(start_process)
    reloads = 0

    async for changes in watcher:
        callback and await callback(changes)
        await watcher.run_in_executor(_stop_process, process)
        process = await watcher.run_in_executor(start_process)
        reloads += 1
    return reloads
