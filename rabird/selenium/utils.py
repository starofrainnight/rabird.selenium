# -*- coding: utf-8 -*-

import gc
import copy
import inspect
from lxml import etree
from lxml.etree import XPathEvalError
from selenium.common.exceptions import InvalidSelectorException


def verify_xpath(pattern):

    html = etree.HTML("<root></root>")
    err = None

    try:
        html.xpath(pattern)
    except XPathEvalError as e:
        err = e

    if err:
        raise InvalidSelectorException(str(err))


def merge_kwargs(func, args=list(), kwargs=dict()):
    kwargs = copy.deepcopy(kwargs)

    argspec = inspect.getargspec(func)
    for i in range(0, len(args)):
        kwargs[argspec.args[i]] = args[i]

    return kwargs


def get_current_func():
    outer_frame = inspect.getouterframes(inspect.currentframe())[1].frame

    for obj in gc.get_referrers(outer_frame.f_code):
        if isinstance(obj, FunctionType):
            return obj

    raise ValueError("Current frame not a function!")
