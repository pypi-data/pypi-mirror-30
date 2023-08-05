from django.test import TestCase
from locks.models import Lock
from locks.locks import DbLock, LockOffError, LockOnError
from locks.decorators import lock_and_log
import _thread



class LockTestCase(TestCase):

    def setUp(self):
        lock = Lock.objects.create(name="A")
        lock.save()

    def test_pre_created_lock(self):
        """Test locking behaviour of precreated lock"""
        lock = DbLock(name="A")

        lock.release(hard=True)

        # test if concurrent process is stopped
        lock.set()

        self.assertRaises(LockOnError, lock.set)

        # check if incorrect releasing of locks raises errors
        lock.release()

        self.assertRaises(LockOffError, lock.release)

    def test_auto_lock_creation(self):
        lock = DbLock("B")
        lock.set()
        self.assertRaises(LockOnError, lock.set)

class LockAndLogTestCase(TestCase):

    def test_decorator(self):
        import logging
        logger = logging.getLogger(__name__).disabled

        @lock_and_log(logger=logger, uid='id')
        def lock_me():
            return True

        res = lock_me()
        self.assertTrue(res)


class TestLockAtomicity(TestCase):
    def test_lock(self):
        lock = DbLock(name='D')

        def do():
            lock.set()
            lock.release()

        for i in range(5):
            _thread.start_new_thread(do, ())


    def test_decorator(self):
        import logging
        logger = logging.getLogger(__name__)


        @lock_and_log(logger, uid='G')
        def do():
            print('heyhey')

        for i in range(5):
            _thread.start_new_thread(do, ())