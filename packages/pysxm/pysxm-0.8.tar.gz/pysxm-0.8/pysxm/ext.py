# Copyright (c) 2017 Josue Kouka
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (Pysxm), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import unicode_literals, absolute_import

from dateutil.parser import parse as dateutil_parse

from pysxm import BaseType, ComplexType, SimpleType


class GenericDateTime(BaseType):

    def __init__(self, value, part=None):
        parsed_date = dateutil_parse(value)
        self.value = parsed_date.isoformat()
        if part:
            self.value = getattr(parsed_date, part)().isoformat()


class DateTimeType(GenericDateTime):

    def __init__(self, value):
        super(DateTimeType, self).__init__(value)


class DateType(GenericDateTime):

    def __init__(self, value):
        super(DateType, self).__init__(value, 'date')


class TimeType(GenericDateTime):

    def __init__(self, value):
        super(TimeType, self).__init__(value, 'time')


class XSimpleType(object):

    def __init__(self, restriction_values, name=None):
        self.restriction_values = restriction_values
        if name:
            self.name = name

    def __set__(self, instance, value):
        if instance is None:
            return self
        self.check_restriction(instance, value)
        instance.__dict__[self.name] = value

    def __get__(self, instance, klass):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def check_restriction(self, instance, value):
        raise NotImplementedError


class XDateTimeType(object):

    dtype = None

    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def __set__(self, instance, value):
        if instance is None:
            return self
        parsed_date = dateutil_parse(value)
        if self.dtype:
            instance.__dict__[self.name] = getattr(parsed_date, self.dtype)().isoformat()
        else:
            instance.__dict__[self.name] = parsed_date.isoformat()

    def __get__(self, instance, klass):
        if instance is None:
            return self
        return instance.__dict__[self.name]


class XDateType(XDateTimeType):

    dtype = 'date'


class XTimeType(XDateTimeType):

    dtype = 'time'


__all__ = ["SimpleType", "DateTimeType", "DateType", "TimeType", "ComplexType",
           "XSimpleType", "XDateTimeType", "XDateType", "XTimeType"]
