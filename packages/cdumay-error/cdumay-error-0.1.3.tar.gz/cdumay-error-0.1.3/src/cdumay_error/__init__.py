#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import sys
import traceback
from marshmallow import Schema, fields


class Error(Exception):
    """Error"""
    MSGID = "Err-00000"

    def __init__(self, code=1, message=None, extra=None, msgid=None):
        self.message = message if message else self.__doc__
        Exception.__init__(self, code, self.message)
        self.code = code
        self.extra = extra or dict()
        self.stack = None
        self.msgid = msgid or self.MSGID

        exc_t, exc_v, exc_tb = sys.exc_info()
        if exc_t and exc_v and exc_tb:
            self.stack = "\n".join([
                x.rstrip() for x in traceback.format_exception(
                    exc_t, exc_v, exc_tb
                )
            ])

    def to_json(self):
        return ErrorSchema().dumps(self)

    @classmethod
    def from_json(cls, data):
        return ErrorSchema().load(data)

    def __repr__(self):
        return "{}<code={}, msgid={}, message={}>".format(
            self.__class__.__name__, self.code, self.msgid, self.message
        )

    def __str__(self):
        return "{}: {}".format(self.msgid, self.message)


class ErrorSchema(Schema):
    code = fields.Integer(required=True)
    name = fields.Method("class_name")
    message = fields.String(required=True)
    msgid = fields.String()
    extra = fields.Dict()
    stack = fields.String()

    def class_name(self, data):
        return data.__class__.__name__


class ConfigurationError(Error):
    """Configuration error"""
    MSGID = "ERR-19036"

    def __init__(self, message=None, extra=None, msgid=None):
        Error.__init__(
            self, code=500, message=message, extra=extra, msgid=msgid
        )


# noinspection PyShadowingBuiltins
class IOError(Error):
    """I/O Error"""
    MSGID = "ERR-27582"

    def __init__(self, message=None, extra=None, msgid=None):
        Error.__init__(
            self, code=500, message=message, extra=extra, msgid=msgid
        )


# noinspection PyShadowingBuiltins
class NotImplemented(Error):
    """Not Implemented"""
    MSGID = "ERR-04766"

    def __init__(self, message=None, extra=None, msgid=None):
        Error.__init__(
            self, code=501, message=message, extra=extra, msgid=msgid
        )


class ValidationError(Error):
    """Validation error"""
    MSGID = "ERR-04413"

    def __init__(self, message=None, extra=None, msgid=None):
        Error.__init__(
            self, code=400, message=message, extra=extra, msgid=msgid
        )


class NotFound(Error):
    """Not Found"""
    MSGID = "ERR-08414"

    def __init__(self, message=None, extra=None, msgid=None):
        Error.__init__(
            self, code=404, message=message, extra=extra, msgid=msgid
        )


class InternalError(Error):
    """Internal Error"""
    MSGID = "ERR-29885"

    def __init__(self, message=None, extra=None, msgid=None):
        Error.__init__(
            self, code=500, message=message, extra=extra, msgid=msgid
        )
