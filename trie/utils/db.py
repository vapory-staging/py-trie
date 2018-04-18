import contextlib


class ScratchDB:
    """
    A wrapper of basic DB objects with uncommitted DB changes stored in local cache,
    which represents as a dictionary of database keys and values.
    None values cannot be represented, because they signify a deleted value.

    The method batch_commit() can be used as a context manager.
    Upon exiting the context, it writes all of the key value pairs from the cache into
    the underlying database. It optionally pushes deletes to the underlying databes.
    If any exception occurrs before committing phase, no changes are applied.
    """
    def __init__(self, wrapped_db):
        self.wrapped_db = wrapped_db
        self.cache = {}

    #
    # Dictionary API
    #
    # if not key is found, return None
    def __getitem__(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            return self.wrapped_db.get(key, None)

    def __setitem__(self, key, value):
        self.cache[key] = value

    def __delitem__(self, key):
        self.cache[key] = None

    def __contains__(self, key):
        if key in self.cache:
            return self.cache[key] is not None
        else:
            return key in self.wrapped_db

    @contextlib.contextmanager
    def batch_commit(self, *, do_deletes=False):
        '''
        Batch and commit and end of context
        '''
        try:
            yield
        except Exception as exc:
            raise exc
        else:
            for key, value in self.cache.items():
                if value is not None:
                    self.wrapped_db[key] = value
                elif do_deletes:
                    self.wrapped_db.pop(key, None)
                # if do_deletes is False, ignore deletes to underlying db
        finally:
            self.cache = {}
