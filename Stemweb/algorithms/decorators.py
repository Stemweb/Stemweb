def synchronized(lock):
    ''' Synchronization decorator. '''
    def wrap(f):
        def syncedFunction(*args, **kw):
            lock.acquire()
            try: 
                return f(*args, **kw)
            finally: 
                lock.release()
        return syncedFunction
    return wrap
