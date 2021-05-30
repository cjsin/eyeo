#!/bin/bash

__pdoc__ = {
    'pytest': False
}

import pytest

import eyeo
from eyeo import *

def test_setup_logging(capsys):
    assert capsys.readouterr().err == ""

def test_register_type_representer(capsys):
    class ExampleObj:
        def __init__(self, value=None):
            self.value = value

    def represent_ExampleObj(o):
        return str(o.value)

    # pylint: disable=comparison-with-callable
    register_type_representer(ExampleObj, represent_ExampleObj)
    assert get_type_representer(ExampleObj) == represent_ExampleObj
    assert get_type_representer(ExampleObj)(ExampleObj("abc")) == "abc"
    eo(ExampleObj("blah"), fmt="example {idx} is {val}")
    assert capsys.readouterr().err == "example 0 is blah\n"
    eo(ExampleObj("blah"), fmt="example is {val}")
    assert capsys.readouterr().err == "example is blah\n"

# this routine also tested by test_regiser_type_representer
def test_get_type_representer():
    pass

def test_todo(capsys):
    todo("run a test")
    assert capsys.readouterr().err == "TODO: run a test\n"

def test__init_level():
    # pylint: disable=protected-access
    key = "TEST_LEVEL"
    if key in os.environ:
        del os.environ[key]
    assert eyeo._init_level(key, defaultval=3) == 3
    os.environ[key] = "5"
    assert eyeo._init_level(key, 0) == 5

def test_set_debug_regex(capsys):
    set_debug_regex(".*TEST.*")
    set_debug(1)
    dbgmsg("should not show this")
    dbgmsg("should show TEST A")
    dbgmsg("should not show this either")
    dbgmsg("should show TEST B")
    result = capsys.readouterr().err.splitlines()
    assert len(result) == 2
    assert result[0].endswith("should show TEST A")
    assert result[1].endswith("should show TEST B")

def test_increment_debug():
    set_debug(0)
    assert get_debug() == 0
    increment_debug()
    assert get_debug() == 1

def test_progname():
    assert progname() in ["pytest", "pytest-3", "pytest3"]

def test_scriptname():
    assert scriptname() in ["pytest", "pytest-3", "pytest3"]

def test_increment_verbose():
    set_verbose(0)
    assert get_verbose() == 0
    increment_verbose()
    assert get_verbose() == 1

def test_get_verbose():
    set_verbose(-1)
    assert get_verbose() == -1
    set_verbose(0)
    assert get_verbose() == 0
    set_verbose(1)
    assert get_verbose() == 1

# test_set_verbose is also tested by test_get_verbose
def test_set_verbose():
    pass

def test_get_debug():
    set_debug(-1)
    assert get_debug() == -1
    set_debug(0)
    assert get_debug() == 0
    set_debug(1)
    assert get_debug() == 1

# test_set_debug is also tested by test_get_debug
def test_set_debug():
    pass

#output_stack = []
#output_handle = None

def test_output_add(capsys):
    assert capsys.readouterr().err == ""

def test_output_buffer(capsys):
    buf = output_buffer()
    msg("this goes to string buf")
    assert capsys.readouterr().err == ""
    buf.seek(0)
    assert buf.read() == "this goes to string buf\n"
    output_pop()
    msg("this goes to stderr")
    assert capsys.readouterr().err == "this goes to stderr\n"

# this one tested by test_output_buffer
def test_output_pop():
    pass

def test_reopen_to(capsys):
    pass

def test_reopen_to_devnull(capsys):
    pass

def test_eoind(capsys):
    eoind("data:", "a","b",1,2,3, indent=" :")
    assert capsys.readouterr().err == "data:\n :a\n :b\n :1\n :2\n :3\n"

def test_quoted(capsys):
    assert quoted("a") == "a"
    assert quoted("x", quote='"', quote_if="a") == '"x"'
    assert quoted("a b", quote="'") == "a b"
    assert quoted("a b", quote="'", quote_if="s") == "'a b'"
    assert quoted("a'b", quote="'", quote_if="q") == "'a\\'b'"

    assert quoted("") == ""
    assert quoted("",quote='"', quote_if="e") == '""'
    assert quoted("",quote="'", quote_if="e") == "''"

def test_eocmd(capsys):
    cmd = ["an","example", "bash command", "which", "quotes", "", "empty", "args", "and args with quotes like ' that"]
    eocmd(cmd)
    assert capsys.readouterr().err == "an example 'bash command' which quotes '' empty args 'and args with quotes like \\' that'\n"

def test_pretty(capsys):
    assert capsys.readouterr().err == ""

def test_eo(capsys):
    assert capsys.readouterr().err == ""

def test_eod(capsys):
    assert capsys.readouterr().err == ""

def test_eodir(capsys):
    assert capsys.readouterr().err == ""

def test_eostack(capsys):
    assert capsys.readouterr().err == ""

def test_msgx(capsys):
    assert capsys.readouterr().err == ""

def test_msg(capsys):
    assert capsys.readouterr().err == ""

def test_warnmsg(capsys):
    warnmsg("a warnmsg message")
    assert capsys.readouterr().err == "WARNING: a warnmsg message\n"

def test_warn(capsys):
    warn("a warn message")
    assert capsys.readouterr().err == "WARNING: a warn message\n"

def test_msgl(capsys):
    assert capsys.readouterr().err == ""

def test_err(capsys):
    err("an err message")
    assert capsys.readouterr().err == "ERROR: an err message\n"

def test_errmsg(capsys):
    errmsg("an errmsg message")
    assert capsys.readouterr().err == "ERROR: an errmsg message\n"

def test_info(capsys):
    info("an info message")
    assert capsys.readouterr().err == "INFO: an info message\n"

def test_err_exit(capsys):
    with pytest.raises(SystemExit) as se:
        err_exit(1, "blah")
    assert se.value.code == 1
    assert capsys.readouterr().err == "ERROR: blah\n"

def test_err_exit_if(capsys):
    with pytest.raises(SystemExit) as se:
        err_exit_if(True, "blah")
    assert se.value.code == 1
    assert capsys.readouterr().err == "ERROR: blah\n"

    err_exit_if(False, "blah")
    assert capsys.readouterr().err == ""

def test_verb(capsys):
    set_verbose(-1)
    verb("should print -1")
    assert capsys.readouterr().err == "should print -1\n"

    set_verbose(0)
    verb("should not print 0")
    assert capsys.readouterr().err == ""

    set_verbose(1)
    vverb(1, "should print 1")
    assert capsys.readouterr().err == "should print 1\n"

def test_vverb(capsys):
    set_verbose(0)
    vverb(1, "should not print 1")
    assert capsys.readouterr().err == ""

    set_verbose(1)
    vverb(1, "should print 1")
    assert capsys.readouterr().err == "should print 1\n"
    vverb(2, "should not print 2")
    assert capsys.readouterr().err == ""

    set_verbose(2)
    vverb(1, "should print 1")
    assert capsys.readouterr().err == "should print 1\n"
    vverb(2, "should print 2")
    assert capsys.readouterr().err == "should print 2\n"
    vverb(3, "should not print 3")
    assert capsys.readouterr().err == ""

    set_verbose(3)
    vverb(1, "should print 1")
    assert capsys.readouterr().err == "should print 1\n"
    vverb(2, "should print 2")
    assert capsys.readouterr().err == "should print 2\n"
    vverb(3, "should print 3")
    assert capsys.readouterr().err == "should print 3\n"
    vverb(4, "should not print 4")
    assert capsys.readouterr().err == ""

def test_dbgexit(capsys):
    with pytest.raises(SystemExit):
        dbgexit("blah")
    assert capsys.readouterr().err == "Exiting: blah\n"

def test_usage_msg(capsys):
    assert capsys.readouterr().err == ""

def test_dbgmsg(capsys):
    assert capsys.readouterr().err == ""

def test_dbgdump(capsys):
    assert capsys.readouterr().err == ""

def test_read_file(capsys):
    assert capsys.readouterr().err == ""

def test_read_file_lines(capsys):
    assert capsys.readouterr().err == ""

def test_write_file(capsys):
    assert capsys.readouterr().err == ""

def test_os_path_splitall():
    assert os_path_splitall(None) is None
    assert os_path_splitall("") is None
    assert os_path_splitall("/") == ["/"]
    assert os_path_splitall("/////") == ["/"]
    assert os_path_splitall("a/b/c") == ["a","b","c"]
    assert os_path_splitall("/a/b/c") == ["/","a","b","c"]
    assert os_path_splitall("../a/b/c") == ["..","a","b","c"]
    assert os_path_splitall("////a/b///c/") == ["/","a","b","c"]
    assert os_path_splitall("//a/b/../c/") == ["/","a","b","..","c"]

    assert os_path_splitall("/", support_unc=True) == ["/"]
    assert os_path_splitall("/////", support_unc=True) == ["//"]
    assert os_path_splitall("a/b/c", support_unc=True) == ["a","b","c"]
    assert os_path_splitall("/a/b/c", support_unc=True) == ["/","a","b","c"]
    assert os_path_splitall("../a/b/c", support_unc=True) == ["..","a","b","c"]
    assert os_path_splitall("////a/b///c/", support_unc=True) == ["//","a","b","c"]
    assert os_path_splitall("///a/b/../c/", support_unc=True) == ["//","a","b","..","c"]

def test_indented():
    assert indented("a","b","c", indent=":") == "a\n:b\n:c"
    assert indented("a","b","c", indent="> ") == "a\n> b\n> c"
    assert indented("a","b","c", indent="  ") == "a\n  b\n  c"
    assert indented("a","b","c", indent=":", indent_first=True) == ":a\n:b\n:c"
    assert indented("a","b","c", indent="> ", indent_first=True) == "> a\n> b\n> c"
    assert indented("a","b","c", indent="  ", indent_first=True) == "  a\n  b\n  c"

def test_isatty():
    # haven't yet thought of a good way to test this
    pass

def test_tb():
    # haven't yet thought of a good way to test this
    pass

def test_print_lines(capsys):
    print_lines(["a","b","c"])
    assert capsys.readouterr().err == "a\nb\nc\n"

