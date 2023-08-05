#    Copyright 2017 Alexey Stepanov aka penguinolog
##
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

"""Base class for decorators."""

from __future__ import absolute_import

import abc
import functools
import sys
import typing

PY3 = sys.version_info[:2] > (3, 0)


class BaseDecorator(typing.Callable):
    """Base class for decorators.

    Implements wrapping and __call__, wrapper getter is abstract.
    """

    def __init__(
        self,
        func=None  # type: typing.Optional[typing.Callable]
    ):
        """Decorator.

        :param func: function to wrap
        :type func: typing.Optional[typing.Callable]
        """
        # pylint: disable=assigning-non-slot
        self.__func = func
        if self.__func is not None:
            functools.update_wrapper(self, self.__func)
            if not PY3:  # pragma: no cover
                self.__wrapped__ = self.__func
        # pylint: enable=assigning-non-slot
        # noinspection PyArgumentList
        super(BaseDecorator, self).__init__()

    @property
    def _func(
        self
    ):  # type: (BaseDecorator) -> typing.Optional[typing.Callable]
        """Get wrapped function.

        :rtype: typing.Optional[typing.Callable]
        """
        return self.__func  # pragma: no cover

    @abc.abstractmethod
    def _get_function_wrapper(
        self,
        func  # type: typing.Callable
    ):  # type: (...) -> typing.Callable
        """Here should be constructed and returned real decorator.

        :param func: Wrapped function
        :type func: typing.Callable
        :rtype: typing.Callable
        """
        raise NotImplementedError()  # pragma: no cover

    def __call__(self, *args, **kwargs):
        """Main decorator getter."""
        args = list(args)
        wrapped = self.__func or args.pop(0)
        wrapper = self._get_function_wrapper(wrapped)
        if self.__func:
            return wrapper(*args, **kwargs)
        return wrapper

    def __repr__(self):
        """For debug purposes."""
        return "<{cls}({func!r}) at 0x{id:X}>".format(
            cls=self.__class__.__name__,
            func=self.__func,
            id=id(self)
        )  # pragma: no cover
