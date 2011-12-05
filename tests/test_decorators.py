from mock import Mock, patch, call
from nose.tools import eq_

from blazeutils import curry, decorator
from blazeutils.decorators import exc_emailer
from blazeutils.testing import raises

def test_curry():

    @curry
    def myfunc(a, b, c):
        return a+b+c;

    f = myfunc(1)
    f = f(2)
    assert f(3) == 6

def test_decorator():

    @decorator
    def mydec(fn, toadd):
        return 4 + fn(toadd)

    @mydec
    def myfunc(toreturn):
        return toreturn

    assert myfunc(5) == 9

class TestExcEmailer(object):

    @patch('blazeutils.decorators.log')
    def test_no_exception(self, m_log):
        send_mail = Mock()

        @exc_emailer(send_mail)
        def myfunc():
            pass

        myfunc()

        assert send_mail.call_count == 0
        assert m_log.exception.call_count == 0

    @patch('blazeutils.decorators.log')
    def test_exception(self, m_log):
        send_mail = Mock()

        @exc_emailer(send_mail)
        def myfunc():
            raise ValueError('test')

        myfunc()

        assert send_mail.call_count == 1
        traceback = send_mail.call_args[0][0]
        assert 'Traceback' in traceback
        assert 'raise ValueError(\'test\')' in traceback
        m_log.exception.assert_called_once_with('exc_mailer() caught an exception, email will be sent')

    @patch('blazeutils.decorators.log')
    def test_send_mail_func_exception(self, m_log):

        def send_mail(body):
            raise ValueError('send_mail')

        @exc_emailer(send_mail)
        def myfunc():
            raise ValueError('myfunc')

        try:
            myfunc()
            assert False, 'expected exception'
        except ValueError, e:
            if str(e) != 'myfunc':
                raise

        eq_(m_log.exception.call_args_list, [
            call('exc_mailer() caught an exception, email will be sent'),
            call('exc_mailer(): send_mail_func() threw an exception, logging it & then re-raising original exception'),
        ])

    @raises(ValueError)
    def test_catch_arg_usage(self):
        send_mail = Mock()

        @exc_emailer(send_mail, catch=TypeError)
        def myfunc():
            raise ValueError('myfunc')

        myfunc()

    @patch('blazeutils.decorators.log')
    def test_custom_logger(self, m_log):
        logger = Mock()

        def send_mail(body):
            raise ValueError('send_mail')

        @exc_emailer(send_mail, logger)
        def myfunc():
            raise ValueError('myfunc')

        try:
            myfunc()
            assert False, 'expected exception'
        except ValueError, e:
            if str(e) != 'myfunc':
                raise

        assert m_log.exception.call_count == 0
        assert logger.exception.call_count == 2
