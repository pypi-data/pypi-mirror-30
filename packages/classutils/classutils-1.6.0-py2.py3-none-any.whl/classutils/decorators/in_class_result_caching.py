# -*- coding: utf-8 -*-

import functools
import logging_helper
from timingsutil import Timeout

logging = logging_helper.setup_logging()

CLASS_CACHED_RESULT_PREFIX = u"_cached_"


def clear_class_cached_results(func):

    @functools.wraps(func)
    def wrapper(self,
                *args,
                **kwargs):

        """ Clears all class cached results.
        """
        [delattr(self, attr)
         for attr in dir(self)
         if attr.startswith(CLASS_CACHED_RESULT_PREFIX)]

        return func(self,
                    *args,
                    **kwargs)

    return wrapper


def class_cache_result(_func=None,
                       timeout=0):

    """ This decorator handles any decorator args.

    :param _func:       Possibly the function to be decorated _func's type depends on the usage of the decorator.
                        It's a function if it's used as `@decorator` but ``None`` if used as `@decorator()`.
    :param timeout:     If set to an integer/float value the cached result will only be held for the
                        number of seconds specified.  Default = 0 (no timeout)
    :return:
    """

    def arg_wrapper(func):

        """ This is the real decorator and  will cache the return value of the decorated 
        function for the lifetime of the object.

        NOTE: This should only be used for class functions!
        """
        cache_id = u'{prefix}{name}'.format(prefix=CLASS_CACHED_RESULT_PREFIX,
                                            name=func.__name__)

        timer = Timeout(seconds=timeout,
                        start_in_an_expired_state=True) if timeout > 0 else None

        @functools.wraps(func)
        def wrapper(self,
                    refresh=False,
                    *args,
                    **kwargs):
    
            """ Simple run time cache for the function result.
    
            :param self:        As this is for class methods we have to add self.
            :param refresh:     setting to True will force this cached result to refresh itself.
            :param args:        Args for the function.
            :param kwargs:      Kwargs for the function.
            :return:            The result of the function.
            """

            # Check whether we are using a timeout
            if timer is not None:
                # When the timer expires refresh the cache and restart the timer.
                if timer.expired:
                    refresh = True
                    timer.restart()

            try:
                cached_result = getattr(self, cache_id)
                action = u'Refreshing'
    
            except AttributeError:
                # Value has not been cached yet
                action = u'Caching'
    
            else:
                if not refresh:
                    logging.debug(u'Returning cached result for {id}'.format(id=cache_id))
                    return cached_result
    
            logging.debug(u'{action} result for {id}'.format(action=action,
                                                             id=cache_id))
    
            result = func(self,
                          *args,
                          **kwargs)
    
            setattr(self, cache_id, result)
    
            return result

        # Return the decorated function
        return wrapper

    # _func's type depends on the usage of the decorator.  It's a function
    # if it's used as `@decorator` but ``None`` if used as `@decorator()`.
    return arg_wrapper if _func is None else arg_wrapper(_func)
