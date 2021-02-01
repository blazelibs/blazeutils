import pytest

import blazeutils.testing.celery as ct


pytest_plugins = ('celery.contrib.pytest', 'blazeutils.testing.celery')


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'amqp://',
        'result_backend': 'rpc',
        **ct.celery_config_annotations
    }


@pytest.fixture(scope='session')
def celery_parameters():
    return {
        **ct.celery_parameters
    }


@pytest.fixture(scope='session')
def celery_worker_parameters():
    return {
        'concurrency': 3
    }
