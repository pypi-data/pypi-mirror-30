from locks.models import Lock
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.utils import IntegrityError
from locks.exceptions import LockOffError, LockOnError
import datetime

"""
Atomic locks to ensure only a single instance of a process is running.
"""


class DbLock:
    def __init__(self, name):
        self.name = name

    def set(self, hard=False, expire=False, expiration=datetime.datetime.now()):
        try:
            lock = Lock.objects.select_for_update().filter(name=self.name, locked=False).update(locked=True, expire=expire, expiration=expiration)
            if not lock:
                lock, created = Lock.objects.get_or_create(name=self.name, locked=True)
                if not created:
                    if lock.expire:
                        if lock.expiration < datetime.datetime.now():
                            lock.expire = expire
                            lock.expiration = expiration
                            lock.save()
                            return
                        if not hard:
                            raise LockOnError("Lock {} hasn't expired yet".format(self.name))
                    if not hard:
                        raise LockOnError("Lock {} was on while trying to turn it on".format(self.name))
        except ObjectDoesNotExist:
            Lock.objects.select_for_update().create(name=self.name, locked=False).update(locked=True)

    @transaction.atomic
    def release(self, hard=False):
        lock = Lock.objects.select_for_update().filter(name=self.name, locked=True).update(locked=False)
        if not lock and not hard:
            raise LockOffError("Lock {} was off while trying to turn it off".format(self.name))

    def state(self):
        try:
            lock = Lock.objects.get(name=self.name).locked
            return lock.locked
        except ObjectDoesNotExist:
            lock = Lock.objects.select_for_update().create(name=self.name, locked=False)
            return lock.locked

    def delete(self):
        """
        remove the lock from the db
        """
        try:
            Lock.objects.get(name=self.name).delete()
            return True
        except ObjectDoesNotExist:
            return False
