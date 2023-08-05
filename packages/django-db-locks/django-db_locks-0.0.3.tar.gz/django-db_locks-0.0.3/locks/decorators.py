from locks.locks import DbLock
import time


def lock_and_log(logger, uid, raise_error=True, sleep=0):
    """
    decorator to create a unique lock for a function, log the function and release the lock if an exception occurs.
    if raise_error is set to false, it will simple exit the function (handy for if you don't want to log)
    if sleep is set, it will sleep for x seconds before releasing the lock
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            lock_name = func.__name__ + __name__ + uid
            lock = DbLock(lock_name)
            lock.set()
            try:
                res = func(*args, **kwargs)
                time.sleep(sleep)
                lock.delete()
                return res
            except Exception:
                time.sleep(sleep)
                lock.delete()
                logger.exception('error in {}'.format(func.__name__))
                return None
        return wrapper
    return decorator