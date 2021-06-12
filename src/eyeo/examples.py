#!/bin/env python3
# pylint: disable=missing-function-docstring,unused-wildcard-import,line-too-long,trailing-newlines,missing-module-docstring,wildcard-import,invalid-name

import sys
import os
from io import StringIO

import eyeo
from eyeo import (increment_verbose,
                  output_buffer,
                  eo as eo_orig,
                  vverb as vverb_orig,
                  output_pop as output_pop_orig)

TROUBLESHOOTING = False

def endl(s):
    """ return the passed string with a line ending appended """
    return s + os.linesep

class capture:
    """ decorator class for capturing stdout, stderr and the function result so that it can be tested """
    # pylint: disable=too-few-public-methods
    def __init__(self, f):
        self.f = f
    def __call__(self, *args, **kwargs):
        old_so = sys.stdout
        old_se = sys.stderr
        so = StringIO()
        se = StringIO()
        # hack to ensure stdout/stderr still captured even when being specified as a parameter
        if 'file' in kwargs:
            file = kwargs['file']
            if file == old_so:
                file = so
            elif file == old_se:
                file = se
            kwargs['file'] = file
        sys.stdout = so
        sys.stderr = se
        ret_orig = self.f(*args, **kwargs)
        sys.stdout = old_so
        sys.stderr = old_se
        so.seek(0)
        se.seek(0)
        ret = [ so.read(), se.read() ]
        if TROUBLESHOOTING:
            print(f"Captured from {self.f.__name__}:", ret, file=sys.stderr)
            print(f"Original return from {self.f.__name__}:", ret_orig, file=sys.stderr)
        return ret, ret_orig

@capture
def eo(*args, **kwargs):
    """ decorated version of eo_orig, which will capture the output """
    return eo_orig(*args, **kwargs)

@capture
def vverb(*args, **kwargs):
    """ decorated version of vverb_orig, which will capture the output """
    return vverb_orig(*args, **kwargs)

@capture
def output_pop(*args, **kwargs):
    """ decorated version of output_pop, which will capture the output """
    return output_pop_orig(*args, **kwargs)

def expected(stdout, stderr, normal_ret=None):
    """
    helper routine to build a data structure of expected results
    that will match the structure of the @captured decorator results
    """
    return ([stdout, stderr], normal_ret)

def test_eyeo_eo_levels():
    """
    Example usage of some routines provided by this module.
    """

    eyeo.DEBUG = 0
    eyeo.VERBOSE = 0

    assert vverb(1, "test 1") \
                 == expected("", "")

    increment_verbose(1)
    assert vverb(1, "test 1") \
                 == expected("", endl("test 1"))

def test_eyeo_basics():
    assert eo("A simple message") \
              == expected("", endl("A simple message"))

    assert eo("A simple message with", "extra", "data") \
              == expected("", endl("A simple message with extra data"))

    assert eo("A simple message with format strings {} {}", "for", "data") \
              == expected("", endl("A simple message with format strings for data"))

    assert eo(["a","list"]) \
              == expected("", endl("a list"))

def test_eyeo_buffers_captured():
    _sio = output_buffer()
    eo_orig("printed to buffer")
    captured, normally_returned = output_pop(print_to_upper=True)
    assert normally_returned is not None
    (_buf, buflen, bufdata) = normally_returned
    assert captured == [ "", endl("printed to buffer") ]
    assert(buflen) == len(endl("printed to buffer"))
    assert(bufdata) == endl("printed to buffer")

def test_eyeo_buffers_orig():
    _sio = output_buffer()
    eo_orig("printed to buffer")
    normally_returned = output_pop_orig(print_to_upper=False)
    (_buf, buflen, bufdata) = normally_returned
    assert(buflen) == len(endl("printed to buffer"))
    assert(bufdata) == endl("printed to buffer")

def test_eyeo_simple_string():
    assert eo("abc def") \
              == expected("", endl("abc def"))

def test_eyeo_eo_fstring():
    arg1 = "ABC"
    arg2 = "DEF"
    assert eo(f"{arg1} {arg2}") \
              == expected("", endl("ABC DEF"))

def test_eyeo_eo_joiner():
    arg1 = "DEF"
    # print all arguments, separated by a joiner(defaults to a space)
    assert eo("abc", arg1) \
              == expected("", endl("abc DEF"))

    # print comma separated
    assert eo("a","b","c","d", joiner=",") \
              == expected("", endl("a,b,c,d"))

def test_eyeo_eo_end():
    # write without line ending
    assert eo("no line ending", end="") \
              == expected("", "no line ending")

    assert eo("another line") \
              == expected("", endl("another line"))

def test_eyeo_file():
    assert eo("write to stdout", file=sys.stdout) \
              == expected(endl("write to stdout"), "")

def test_eyeo_indent():
    assert eo([1,2,3], indent="    ") \
              == expected("", endl("    1") + endl("    2") + endl("    3"))

def test_eyeo_fmt():
    assert eo(["a","b","c","d"], fmt="{idx:02d}. {val}\n", end="", joiner="") \
              == expected("", "00. a\n01. b\n02. c\n03. d\n")

    assert eo("a","b","c","d", fmt="{idx:02d}. {val}\n", end="", joiner="") \
              == expected("", "00. a\n01. b\n02. c\n03. d\n")

def test_eyeo_eo_quote_always():
    assert eo("a","b c d","", quote_if="always") \
              == expected("", endl("'a' 'b c d' ''"))

def test_eyeo_eo_quote_if():
    assert eo("a","b c d","", quote_if="empty,space") \
               == expected("", endl("a 'b c d' ''"))

def test_eyeo_eo_None_values():
    assert eo("print array with a None value", [ None, 1, 2, 3, "a" ]) \
              == expected("", endl("print array with a None value [None, 1, 2, 3, 'a']"))

    assert eo("print with a None value", "a", 1, None, "d") \
              == expected("", endl("print with a None value a 1 (None) d"))

    assert eo("print with a None value", "a", 1, None, "d", nonestr="<none>") \
              == expected("", endl("print with a None value a 1 <none> d"))

def run_examples():
    test_eyeo_eo_levels()
    test_eyeo_basics()
    test_eyeo_buffers_orig()
    test_eyeo_buffers_captured()
    test_eyeo_eo_fstring()
    test_eyeo_simple_string()
    test_eyeo_eo_joiner()
    test_eyeo_eo_end()
    test_eyeo_file()
    test_eyeo_indent()
    test_eyeo_fmt()
    test_eyeo_eo_quote_always()
    test_eyeo_eo_quote_if()
    test_eyeo_eo_None_values()

if __name__ == "__main__":
    run_examples()
