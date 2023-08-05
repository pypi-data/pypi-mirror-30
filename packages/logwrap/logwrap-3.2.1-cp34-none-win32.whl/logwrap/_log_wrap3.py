#    Copyright 2016-2017 Alexey Stepanov aka penguinolog

#    Copyright 2016 Mirantis, Inc.

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""log_wrap: async part (python 3.4+).

This is no reason to import this submodule directly, all required methods is
available from the main module.
"""

from __future__ import absolute_import
from __future__ import unicode_literals

# noinspection PyCompatibility
import asyncio
import functools
import inspect
import logging
import typing


from . import _log_wrap_shared

__all__ = ('logwrap', 'LogWrap')


DEFAULT_DECORATOR_ARGUMENT = typing.Union[logging.Logger, typing.Callable]


class LogWrap(_log_wrap_shared.BaseLogWrap):
    """Python 3.3+ version of LogWrap."""

    __slots__ = ()

    def _get_function_wrapper(
        self,
        func: typing.Callable
    ) -> typing.Callable:
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :return: wrapped coroutine or function
        :rtype: typing.Callable
        """
        sig = inspect.signature(obj=self._spec or func)

        # pylint: disable=missing-docstring
        # noinspection PyCompatibility,PyMissingOrEmptyDocstring
        @functools.wraps(func)
        @asyncio.coroutine
        def async_wrapper(*args, **kwargs):
            args_repr = self._get_func_args_repr(
                sig=sig,
                args=args,
                kwargs=kwargs,
            )

            try:
                self._make_calling_record(
                    name=func.__name__,
                    arguments=args_repr,
                    method='Awaiting'
                )
                result = yield from func(*args, **kwargs)
                self._make_done_record(func.__name__, result)
            except BaseException as e:
                if isinstance(e, tuple(self.blacklisted_exceptions)):
                    raise
                self._make_exc_record(name=func.__name__, arguments=args_repr)
                raise
            return result

        # noinspection PyCompatibility,PyMissingOrEmptyDocstring
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_repr = self._get_func_args_repr(
                sig=sig,
                args=args,
                kwargs=kwargs,
            )

            try:
                self._make_calling_record(
                    name=func.__name__,
                    arguments=args_repr
                )
                result = func(*args, **kwargs)
                self._make_done_record(func.__name__, result)
            except BaseException as e:
                if isinstance(e, tuple(self.blacklisted_exceptions)):
                    raise
                self._make_exc_record(name=func.__name__, arguments=args_repr)
                raise
            return result

        # pylint: enable=missing-docstring
        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper


# pylint: disable=unexpected-keyword-arg, no-value-for-parameter
def logwrap(
    log: DEFAULT_DECORATOR_ARGUMENT = _log_wrap_shared.logger,
    log_level: int = logging.DEBUG,
    exc_level: int = logging.ERROR,
    max_indent: int = 20,
    spec: typing.Optional[typing.Callable] = None,
    blacklisted_names: typing.Optional[typing.List[str]] = None,
    blacklisted_exceptions: typing.Optional[typing.List[Exception]] = None,
    log_call_args: bool = True,
    log_call_args_on_exc: bool = True,
    log_result_obj: bool = True,
) -> typing.Union[LogWrap, typing.Callable]:
    """Log function calls and return values. Python 3.4+ version.

    :param log: logger object for decorator, by default used 'logwrap'
    :type log: typing.Union[logging.Logger, typing.Callable]
    :param log_level: log level for successful calls
    :type log_level: int
    :param exc_level: log level for exception cases
    :type exc_level: int
    :param max_indent: maximum indent before classic `repr()` call.
    :type max_indent: int
    :param spec: callable object used as spec for arguments bind.
                 This is designed for the special cases only,
                 when impossible to change signature of target object,
                 but processed/redirected signature is accessible.
                 Note: this object should provide fully compatible signature
                 with decorated function, or arguments bind will be failed!
    :type spec: typing.Optional[typing.Callable]
    :param blacklisted_names: list of exception,
                              which should be re-raised without
                              producing log record.
    :type blacklisted_names: typing.Optional[typing.Iterable[str]]
    :param blacklisted_exceptions: list of exception,
                                   which should be re-raised without
                                   producing log record.
    :type blacklisted_exceptions: typing.Optional[typing.Iterable[Exception]]
    :param log_call_args: log call arguments before executing wrapped function.
    :type log_call_args: bool
    :param log_call_args_on_exc: log call arguments if exception raised.
    :type log_call_args_on_exc: bool
    :param log_result_obj: log result of function call.
    :type log_result_obj: bool
    :return: built real decorator.
    :rtype: _log_wrap_shared.BaseLogWrap
    """
    if isinstance(log, logging.Logger):
        log, func = log, None
    else:
        log, func = _log_wrap_shared.logger, log

    wrapper = LogWrap(
        log=log,
        log_level=log_level,
        exc_level=exc_level,
        max_indent=max_indent,
        spec=spec,
        blacklisted_names=blacklisted_names,
        blacklisted_exceptions=blacklisted_exceptions,
        log_call_args=log_call_args,
        log_call_args_on_exc=log_call_args_on_exc,
        log_result_obj=log_result_obj
    )
    if func is not None:
        return wrapper(func)
    return wrapper
# pylint: enable=unexpected-keyword-arg, no-value-for-parameter
