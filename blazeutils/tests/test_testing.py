from __future__ import absolute_import
from __future__ import unicode_literals
import datetime as dt
import sys
import time

import mock
import pytest
from celery import shared_task

from blazeutils.testing import raises, assert_equal_sql, assert_equal_txt, \
    mock_date_today, mock_datetime_now, mock_datetime_utcnow
from blazeutils.testing.celery import (
    TaskFailedError,
    TaskTimeoutError,
    TasksInProgressError,
    celery_tasks_complete,
    task_tracker,
)


class LikeWerkzeugExc(Exception):
    description = None

    def __init__(self, description=None):
        Exception.__init__(self)
        if description is not None:
            self.description = description

    def __str__(self):
        return '%d: %s' % (self.code, self.name)


def _is_attribute_exception(exc):
    return isinstance(exc, AttributeError)


class TestRaisesDecorator(object):

    @raises(AttributeError)
    def test_arg1(self):
        assert sys.foo

    @raises("object has no attribute 'foo'")
    def test_arg2(self):
        raise Exception("object has no attribute 'foo'")

    @raises(AttributeError, "object has no attribute 'foo'")
    def test_arg3(self):
        raise AttributeError("object has no attribute 'foo'")

    @raises("object has no attribute 'foo'", AttributeError)
    def test_arg4(self):
        raise AttributeError("object has no attribute 'foo'")

    @raises(_is_attribute_exception)
    def test_callable_validator(self):
        assert sys.foo

    def test_non_matching_message(self):
        try:
            @raises("foobar", AttributeError)
            def wrapper():
                assert sys.foo
            wrapper()
            assert False, '@raises hid the exception but shouldn\'t have'
        except AttributeError as e:
            if "module object has no attribute foo" != str(e).replace("'", '') and \
                    "module sys has no attribute foo" != str(e).replace("'", ''):
                raise

    def test_non_matching_type(self):
        try:
            @raises(ValueError, "^.+object has no attribute 'foo'")
            def wrapper():
                assert sys.foo
            wrapper()
            assert False, '@raises hid the exception but shouldn\'t have'
        except AttributeError as e:
            if "module object has no attribute foo" != str(e).replace("'", '') and \
                    "module sys has no attribute foo" != str(e).replace("'", ''):
                raise

    def test_callable_validator_returns_false(self):
        try:
            @raises(_is_attribute_exception)
            def wrapper():
                raise ValueError('test ve')
            wrapper()
            assert False, '@raises hid the exception but shouldn\'t have'
        except ValueError as e:
            if "test ve" != str(e):
                raise

    def test_no_exception_raised(self):
        try:
            @raises(ValueError, "^.+object has no attribute 'foo'")
            def wrapper():
                pass
            wrapper()
            assert False, '@raises should have complained that an exception was not raised'
        except AssertionError as e:
            if "@raises: no exception raised in wrapper()" != str(e):
                raise

    @raises('[with brackets]')
    def test_non_regex(self):
        raise Exception('[with brackets]')

    @raises(LikeWerkzeugExc, description='Foobar')
    def test_custom_attributes_ok(self):
        raise LikeWerkzeugExc('Foobar')

    def test_custom_attributes_missing(self):
        try:
            @raises(LikeWerkzeugExc, description='Foobar')
            def wrapper():
                raise Exception('baz')
            wrapper()
            assert False, '@raises should have complained that the exception was ' \
                'missing the description attribute'
        except Exception as e:
            if "baz" != str(e):
                raise

    def test_custom_attributes_fails(self):
        try:
            @raises(LikeWerkzeugExc, description='Foobar')
            def wrapper():
                raise LikeWerkzeugExc('baz')
            wrapper()
            assert False, '@raises should have complained that the description ' \
                'attribute did not match'
        except LikeWerkzeugExc:
            pass


def test_assert_equal_sql():
    s2 = s1 = """
    select foo,
    bar,
    baz from bill"""
    assert_equal_sql(s1, s2)


def test_assert_equal_sql_diff():
    s2 = s1 = """
    select foo,
    bar,
    baz from bill"""
    s2 = s2[5:]
    with pytest.raises(AssertionError, match=r'.+!='):
        assert_equal_sql(s1, s2)


def test_assert_equal_txt():
    s1 = """
    line 1
    line 2
    line 3"""
    assert_equal_txt(s1, s1)

    s2 = """
    line 1
    line 25
    line 3"""

    try:
        assert_equal_txt(s1, s2)
        assert False, 'expected exception'
    except AssertionError as e:
        assert '-    line 25' in str(e)
        assert '+    line 2' in str(e)


class TestMockDateTime(object):

    @mock.patch('blazeutils.tests.date_imports.dt_date')
    def test_mock_today(self, m_date):
        from . import date_imports
        mock_date_today(m_date, 2012)
        assert dt.date(2012, 1, 1) == date_imports.dt_date.today()

    @mock.patch('blazeutils.tests.date_imports.dt_datetime')
    def test_mock_now(self, m_datetime):
        from . import date_imports
        mock_datetime_now(m_datetime, 2012)
        assert dt.datetime(2012, 1, 1, 0, 0, 0) == date_imports.dt_datetime.now()

    @mock.patch('blazeutils.tests.date_imports.dt_datetime')
    def test_mock_utcnow(self, m_datetime):
        from . import date_imports
        mock_datetime_utcnow(m_datetime, 2012)
        assert dt.datetime(2012, 1, 1, 0, 0, 0), date_imports.dt_datetime.utcnow()


@shared_task
def sleep_task(sleep_time=0.1):
    time.sleep(sleep_time)


@shared_task
def add_task(num1, num2):
    return num1 + num2


@shared_task
def failing_task():
    time.sleep(0.1)
    raise ValueError('Some Error')


@shared_task(bind=True, max_retries=10)
def retry_task(self, success_on_retry):
    try:
        time.sleep(0.1)
        if retry_task.request.retries == success_on_retry:
            return True
        else:
            assert False
    except AssertionError as e:
        raise self.retry(countdown=0.01, exc=e)


@shared_task
def chained_tasks():
    time.sleep(0.1)
    sleep_task.delay()
    time.sleep(0.1)


@pytest.mark.skipif(sys.platform == 'win32', reason='Linux only tests')
class TestCeleryTaskTracker:
    def test_wait_for_id(self, celery_session_worker):
        task1 = sleep_task.delay()
        task2 = sleep_task.delay()
        task3 = sleep_task.delay()

        result1 = task_tracker.wait_for_id(task1.id)
        result2 = task_tracker.wait_for_id(task2.id)
        result3 = task_tracker.wait_for_id(task3.id)

        assert result1.status == 'SUCCESS'
        assert result2.status == 'SUCCESS'
        assert result3.status == 'SUCCESS'

    def test_wait_for_name(self):
        sleep_task.delay()
        add_task.delay(2, 3)

        result1 = task_tracker.wait_for_task_name('blazeutils.tests.test_testing.sleep_task')
        result2 = task_tracker.wait_for_task_name('blazeutils.tests.test_testing.add_task')

        assert result1.status == 'SUCCESS'
        assert result2.status == 'SUCCESS'
        assert result2.retval == 5

    def test_wait_for_name_duplicate(self):
        task1 = sleep_task.delay()
        task2 = sleep_task.delay()
        task3 = sleep_task.delay()

        task_name = 'blazeutils.tests.test_testing.sleep_task'

        result1 = task_tracker.wait_for_task_name(task_name)
        result2 = task_tracker.wait_for_task_name(task_name)
        result3 = task_tracker.wait_for_task_name(task_name)

        assert result1.task_id == result2.task_id == result3.task_id
        assert result1.task_id in (task1.id, task2.id, task3.id)

        task_tracker.reset()

        task1 = sleep_task.delay()
        task2 = sleep_task.delay()
        task3 = sleep_task.delay()

        result1 = task_tracker.wait_for_task_name(task_name, pop=True)
        result2 = task_tracker.wait_for_task_name(task_name, pop=True)
        result3 = task_tracker.wait_for_task_name(task_name, pop=True)

        assert len({result1.task_id, result2.task_id, result3.task_id}) == 3
        assert result1.task_id in (task1.id, task2.id, task3.id)
        assert result2.task_id in (task1.id, task2.id, task3.id)
        assert result3.task_id in (task1.id, task2.id, task3.id)

    def test_wait_for_timeout(self):
        task1 = sleep_task.delay(sleep_time=0.5)

        with pytest.raises(TaskTimeoutError,
                           match=f'Waited too long for task {task1.id} to complete'):
            task_tracker.wait_for_id(task1, timeout=0.1)

        task_tracker.reset()

        sleep_task.delay(sleep_time=0.5)
        with pytest.raises(
            TaskTimeoutError,
            match='Waited too long for task blazeutils.tests.test_testing.sleep_task to complete'
        ):
            task_tracker.wait_for_task_name('blazeutils.tests.test_testing.sleep_task', timeout=0.1)

        task_tracker.reset()

    def test_wait_for_task_failed(self):
        task1 = failing_task.delay()
        with pytest.raises(TaskFailedError) as exc:
            task_tracker.wait_for_id(task1.id)

        assert exc.value.result.task_id == task1.id

        task2 = failing_task.delay()
        result = task_tracker.wait_for_id(task2.id, throw_failure=False)
        assert result.status == 'FAILURE'
        assert result.task_id == task2.id

    def test_wait_for_pop(self):
        task1 = sleep_task.delay()
        result1 = task_tracker.wait_for_id(task1.id)
        result2 = task_tracker.wait_for_id(task1.id)
        assert result1 is result2

        assert task1.id in task_tracker.completed_tasks

        task2 = sleep_task.delay()
        task_tracker.wait_for_id(task2.id, pop=True)
        assert task2.id not in task_tracker.completed_tasks

        with pytest.raises(TaskTimeoutError):
            task_tracker.wait_for_id(task2.id, timeout=0.1)

    def test_wait_with_retry(self):
        task = retry_task.delay(3)
        result1 = task_tracker.wait_for_id(task.id, throw_failure=False)
        assert result1.status == 'SUCCESS'

        task = retry_task.delay(11)
        result1 = task_tracker.wait_for_id(task.id, throw_failure=False)
        assert result1.status == 'FAILURE'

    def test_reset(self):
        task1 = sleep_task.delay()

        assert task1.id in task_tracker.inflight_tasks
        assert len(task_tracker.completed_tasks) == 0

        task_tracker.wait_for_id(task1.id)

        task2 = sleep_task.delay()
        assert task2.id in task_tracker.inflight_tasks
        assert task1.id in task_tracker.completed_tasks

        task_tracker.reset()
        assert len(task_tracker.inflight_tasks) == 0
        assert len(task_tracker.completed_tasks) == 0

    def test_reset_timeout(self):
        sleep_task.delay(sleep_time=0.5)

        with pytest.raises(TaskTimeoutError):
            task_tracker.reset(timeout=0.1)

        task_tracker.reset()

    def test_chained_tasks(self):
        task = chained_tasks.delay()

        result1 = task_tracker.wait_for_id(task.id)
        result2 = task_tracker.wait_for_task_name('blazeutils.tests.test_testing.sleep_task')
        assert result1.status == 'SUCCESS'
        assert result2.status == 'SUCCESS'

    def test_celery_tasks_complete(self):
        with pytest.raises(TasksInProgressError) as exc:
            with celery_tasks_complete():
                task = sleep_task.delay()

        assert task.id in [t.task_id for t in exc.value.tasks]

        task_tracker.reset()

        with celery_tasks_complete():
            task = sleep_task.delay()
            task_tracker.wait_for_id(task.id)
