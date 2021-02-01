import contextlib
import threading
import time
import warnings
from typing import (
    Callable,
    NamedTuple,
    Any,
    Optional,
    Tuple,
    Dict,
)

import celery.signals
import pytest

from blazeutils import OrderedDict
from blazeutils.functional import first_where


class TaskResult(NamedTuple):
    task_name: str
    status: str
    retval: Any
    task_id: str
    args: Tuple[Any]
    kwargs: Dict[str, Any]
    einfo: Any
    thread_id: int


class ScheduledTask(NamedTuple):
    task_id: str
    task_name: str
    args: Tuple[Any]
    kwargs: Dict[str, Any]


WaitPredicate = Callable[[Dict[str, TaskResult]], Optional[str]]


def after_return_handler(task, status, retval, task_id, args, kwargs, einfo):
    result = TaskResult(
        task_name=task.name,
        status=status,
        retval=retval,
        task_id=task_id,
        args=args,
        kwargs=kwargs,
        einfo=einfo,
        thread_id=threading.get_ident(),
    )
    task_tracker.task_completed(result)


class TestingTask(celery.Task):
    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None,
                    link=None, link_error=None, shadow=None, **options):
        if task_id is None:
            task_id = celery.uuid()
        task = ScheduledTask(
            task_id=task_id,
            task_name=self.name,
            args=args,
            kwargs=kwargs,

        )
        task_tracker.task_sent(task)
        return super().apply_async(args=args, kwargs=kwargs, task_id=task_id, producer=producer,
                                   link=link, link_error=link_error, shadow=shadow, **options)


"""
Task annotations required in the celery configuration to use TaskTracker functionality
"""
celery_config_annotations = {
    'task_annotations': {'*': {'after_return': after_return_handler}},
}

"""
Parameters required for celery to use TaskTracker functionality
"""
celery_parameters = {
    'task_cls':  TestingTask,
}


class CeleryTestingError(Exception):
    pass


class TaskTimeoutError(CeleryTestingError):
    pass


class TaskFailedError(CeleryTestingError):
    def __init__(self, result):
        self.result = result
        super().__init__(result.einfo)


class TasksInProgressError(CeleryTestingError):
    def __init__(self, tasks):
        self.tasks = tasks
        task_names = ', '.join(list({t.task_name for t in self.tasks}))
        super().__init__(
            f'The following celery tasks were still in progress when the test completed: '
            f'[{task_names}]'
        )


@contextlib.contextmanager
def celery_tasks_complete():
    """
    A context manager to ensure all celery tasks have completed by the time it exits.
    """
    yield

    current_tasks = task_tracker.inflight_tasks
    if current_tasks:
        raise TasksInProgressError(list(current_tasks.values()))


@pytest.fixture(scope='function', autouse=True)
def current_celery_tasks():
    """
    An automatic fixture to ensure all celery tasks started within each test are completed
    when the test exits.
    """
    with celery_tasks_complete():
        yield
    task_tracker.reset()


class TaskTracker:
    """
    A singleton class used to track celery tasks within each test.

    To use the TaskTracker with pytest:

    Add the following to your project's conftest.py:

    .. highlight:: python
    .. code-block:: python

        import blazeutils.testing.celery as ct

        pytest_plugins = ('celery.contrib.pytest', 'blazeutils.testing.celery')

        @pytest.fixture(scope='session')
        def celery_config():
            return {
                ...
                **ct.celery_config_annotations,
                ...
            }

        @pytest.fixture(scope='session')
        def celery_parameters():
            return {
                ...
                **ct.celery_parameters,
                ...
            }

    Optionally, if you wish to test with multiple worker threads to better simulate the concurrency
    in a typical production environment, you can configure your concurrency by adding the following:

    .. highlight:: python
    .. code-block:: python

        @pytest.fixture(scope='session')
        def celery_worker_parameters():
            return {
                'concurrency': 3
            }

    """
    def __init__(self):
        self._current_tasks = {}
        self._task_results = OrderedDict()
        self._condition = threading.Condition()

    def task_sent(self, task: ScheduledTask):
        """
        Called by the TestingTask's apply_async method to begin tracking the task
        """
        with self._condition:
            self._current_tasks[task.task_id] = task

    def task_completed(self, task_result: TaskResult):
        """
        Called by the after_return_handler annotation to store the task results and notify any
        waiters that the task was completed.
        """
        with self._condition:
            self._current_tasks.pop(task_result.task_id)
            existing_result = self._task_results.get(task_result.task_id)
            if existing_result is not None:
                warnings.warn(
                    f'Overwriting task result '
                    f'{existing_result.task_name}[{existing_result.task_id}] with '
                    f'{task_result.task_name}[{task_result.task_id}]'
                )
            self._task_results[task_result.task_id] = task_result
            self._condition.notify()

    def reset(self, timeout=2):
        """
        Wait for any current tasks to complete and then resets the results store
        """
        start_time = time.time()
        with self._condition:
            while self._current_tasks:
                if time.time() - start_time > timeout:
                    raise TaskTimeoutError('Waited too long for in-flight tasks to complete')
                self._condition.wait(timeout=timeout)

            # Must happen after while loop so tasks waited for are not added
            self._task_results = OrderedDict()

    def _wait_for_task(self, predicate: WaitPredicate, timeout=2, pop=False, throw_failure=True):
        """
        Waits for a task identified by predicate to complete. This method is provided to allow
        subclasses to await tasks based on whatever attributes are available in TaskResult.

        :param predicate: A callable that takes a dict of task results and returns a result's
            task ID if the desired result is found or None if the result is not present in the dict.
        :param timeout: Maximum time in seconds to wait for the task to complete.
        :param pop: If True, the task result will be removed from the tracked results upon return.
        :param throw_failure: If True, an exception will be raised if the awaited task encountered
            an error.
        :returns: A TaskResult object containing info about the awaited task.
        """
        start_time = time.time()
        with self._condition:
            while True:
                result_id = predicate(self._task_results)
                if result_id is not None:
                    break

                if time.time() - start_time > timeout:
                    raise TaskTimeoutError
                self._condition.wait(timeout=timeout)

            if pop:
                result = self._task_results.pop(result_id)
            else:
                result = self._task_results[result_id]

            if throw_failure and result.status != 'SUCCESS':
                raise TaskFailedError(result)
            return result

    def wait_for_id(self, task_id, timeout=2, pop=False, throw_failure=True):
        """
        Wait for the task with the given task ID to complete and return the results.
        :param task_id: The ID of the task to await.
        :param timeout: Maximum time in seconds to wait for the task to complete.
        :param pop: If True, the task result will be removed from the tracked results upon return.
        :param throw_failure: If True, an exception will be raised if the awaited task encountered
            an error.
        :returns: A TaskResult object containing info about the awaited task.
        """
        def predicate(results):
            return task_id if task_id in results else None

        try:
            return self._wait_for_task(predicate, timeout=timeout, pop=pop,
                                       throw_failure=throw_failure)
        except TaskTimeoutError:
            raise TaskTimeoutError(f'Waited too long for task {task_id} to complete')

    def wait_for_task_name(self, task_name, timeout=2, pop=False, throw_failure=True):
        def predicate(results):
            result = first_where(lambda r: r.task_name == task_name, results.values())
            return result.task_id if result else None

        try:
            return self._wait_for_task(predicate, timeout=timeout, pop=pop,
                                       throw_failure=throw_failure)
        except TaskTimeoutError:
            raise TaskTimeoutError(f'Waited too long for task {task_name} to complete')

    @property
    def completed_tasks(self):
        """
        Returns a copy of the dict tracking all tasks that have been completed
        """
        with self._condition:
            return self._task_results.copy()

    @property
    def inflight_tasks(self):
        """
        Returns a copy of the dict tracking all tasks that have yet to complete
        """
        with self._condition:
            return self._current_tasks.copy()


task_tracker = TaskTracker()
