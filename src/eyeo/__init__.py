import os
import re
import sys
import inspect
import traceback
import logging
import yaml
import json

from io import StringIO
from pprint import pformat

from eyeo.stringify import stringify, stringify_value

typerepresenters = {}

class GlobalLoggingInstance:
    # A global logging instance, set up by setup_logging below
    log = None

    @classmethod
    def setup_logging(cls):
        # logging setup
        log = logging.getLogger(progname())
        log.setLevel(logging.INFO)
        ch = logging.StreamHandler(sys.stderr)
        ch.setLevel(logging.INFO)
        #ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        ch.setFormatter(logging.Formatter('%(message)s'))
        log.addHandler(ch)
        GlobalLoggingInstance.log = log

def setup_logging():
    GlobalLoggingInstance.setup_logging()

def register_type_representer(t, func):
    typerepresenters[t] = func

def get_type_representer(t):
    return typerepresenters.get(t)

def todo(message):
    eo("TODO:" + message)


def _init_level(name, defaultval=0):
    if name not in os.environ:
        return 0
    else:
        val = os.environ.get(name, '')
        if not val:
            return defaultval
        elif val.isdigit():
            return int(val)
        elif val.lower() in [ 'y', 'yes', 'on', 'true', 't' ]:
            return 1
        else:
            return 0

VERBOSE = _init_level('VERBOSE', 0)
DEBUG = _init_level('DEBUG', 0)
DEBUG_REGEX = os.environ.get('DEBUG_REGEX', None)

def set_debug_regex(pattern):
    global DEBUG_REGEX
    if pattern is None or pattern == '':
        DEBUG_REGEX = None
    else:
        DEBUG_REGEX = re.compile(pattern)

def increment_debug(amount=None):
    global DEBUG
    if amount is None:
        amount = 1
    DEBUG += amount

def progname():
    prog = scriptname()
    if prog.endswith('.py'):
        prog = prog[0:-3]
    return prog

def scriptname():
    return os.path.basename(sys.argv[0])

def increment_verbose(amount=None):
    global VERBOSE
    if amount is None:
        amount = 1
    VERBOSE += amount

def get_verbose():
    return VERBOSE

def set_verbose(amount=1):
    global VERBOSE
    VERBOSE = amount

def get_debug():
    return DEBUG

def set_debug(amount=1):
    global DEBUG
    DEBUG = amount


# used by output_add, output_pop and 'eo'
output_stack = []
output_handle = None

def output_add(fhandle):
    global output_stack, output_handle
    output_stack.append(fhandle)
    output_handle = fhandle
    return fhandle

def output_buffer():
    """ Create a new string buffer in the stack and return it """
    return output_add(StringIO())

def output_pop(print_to_upper=False):
    global output_stack, output_handle
    if not output_stack:
        return None

    len_value = None
    data_value = None
    popped = output_stack.pop()
    ret = output_handle
    if ret != popped:
        print("ERROR: output stack got out of sync with expected output handle", file=sys.stderr)

    if output_stack:
        output_handle = output_stack[-1]
    else:
        output_handle = None

    if isinstance(ret, StringIO):
        ret.seek(0)
        data_value = ret.read()
        #print(f"Read '{data_value}' from popped buffer", file=sys.stderr)
        len_value = len(data_value)
    if print_to_upper:
        if data_value:
            #print(f"Printing buffered data '{data_value}'", file=sys.stderr)
            eo(data_value)
        else:
            print(f"Popped handle is of type ({type(ret)}), cannot print_to_upper", file=sys.stderr)
            #pass
    ret.flush()

    return (ret, len_value, data_value)

def reopen_to(fhandle, path, mode):
    """ close and reopen a filehandle """
    newhandle = open(path, mode)
    fhandle.flush()
    fhandle.close()
    return newhandle

def eoind(first, *remainder, file=None, end=None, flush=None, joiner=None, starter=None, indent=None, style=None):
    """
    eo indented:
    example usage:
    eoind("Some data:", a, b, c, d, indent="    ")
    eoind("Some data:", [ 1, 2, 3, 4], indent="  ")
    """
    if indent is None:
        indent = "    "

    remainder = list(remainder)
    if isinstance(first, str):
        eo(first)
    else:
        remainder = first + remainder

    # allow a single arg to be passed as a list
    if len(remainder) == 1 and isinstance(remainder[0], list):
        remainder = remainder[0]
    if joiner is None:
        joiner = "\n" if end is None else end
    eo(*remainder, file=file, end=end, flush=flush, joiner=joiner, starter=starter, indent=indent, style=style)

def quoted(val, quote=None, quote_if=None):
    if quote is None:
        return val
    elif quote_if is None or quote_if == "":
        return val

    needs_quoting = False
    conditions = quote_if.split(",")
    if "e" in conditions and val == "":
        return quote + quote

    contains_quote = quote in val
    if "a" in conditions:
        needs_quoting = True
    else:
        if "q" in conditions and contains_quote:
            needs_quoting = True
        elif "s" in conditions:
            needs_quoting = " " in val or "\t" in val or "\n" in val
    if needs_quoting:
        if contains_quote:
            val = val.replace(quote, "\\" + quote)
        val = quote + val + quote
    return val

def eocmd(*strs, **kwargs):
    kwargs['quote_if'] = 'e,s,q'
    if 'quote' not in kwargs:
        kwargs['quote'] = "'"
    eo(*strs, **kwargs)


def pretty(data, style=None, sort_keys=None, indent=None):
    if indent is None:
        indent = 4
    if style is None:
        style = 'json'
    if sort_keys is None:
        sort_keys = True
    if style == 'yaml':
        return yaml.dump(data, sort_keys=sort_keys, default_flow_style=False, indent=indent, default_style=None, line_break="\n")
    else:
        return json.dumps(data, sort_keys=sort_keys, separators=(", ", " : "), indent=indent)

def eo(*strs, file=None, end=None, flush=None, joiner=None, starter=None, indent=None, style=None, fmt=None, quote=None, nonestr=None, quote_if=None, lf=None):
    """
    Parameters:
       file(filehandle, sys.stderr): output file or None (defaults to stderr)
       end(string, ""):              print this at the end of the items
       flush(bool, False):           perform a flush on the output after
       joiner(string, ""):           use this string to join each item
       starter(string, ""):          use this string at the start when indenting items
       indent(string,"    "):        print this and a linefeed between each item
       style(string,"str"):          one of s,str, r,repr, stringify, j,json, y,yaml
       fmt(string, ""):              use this format string for each item (uses 'idx' and 'val' to allow numbered lines or items)
       quote(string, "'"):           use this character for quoting
       quote_if(string, "e,s,q"):    specify when to wrap in quotes (e=empty,s=contains spaces, q=contains the quote character, a=always)
       lf(string, "\n"):             use this as the line separator (replaces joiner when indent mode is enabled)

    example usage:
    # basic usage, will write to stderr
    eo("abc def")
    # fstring usage, will write to stderr
    eo(f"{abc} {def}")
    # print all arguments, separated by a joiner(defaults to a space)
    eo("abc", def)
    # print comma separated
    eo("a","b","c","d", joiner=",")
    # write without line ending
    eo("no line ending", end="")
    # write to specific file
    eo("write to stdout", file=sys.stdout)
    # print indented lines
    eo([1,2,3,4], indent="    ")
    eo(["a","b","c","d"], fmt="{idx:02d}. {val}")
    eo("a","b","c","d", fmt="{idx:02d}. {val}")
    eo("a","b c d","", quote_if="always")
    eo("a","b c d","", quote_if="empty,space")
    """

    if nonestr is None:
        nonestr = "(None)"
    if lf is None:
        lf = "\n"

    if style is None:
        style = 'str'
    if quote_if is None:
        quote_if = 'empty,space,quote'

    global output_stack, output_handle

    if joiner is None:
        joiner = " "

    prefix = "" if starter is None else starter

    if indent is not None:
        joiner = lf
        if fmt is None:
            fmt = indent + "{val}"
        else:
            fmt = indent + fmt

    def format_val(x, idx=None):
        if x is None:
            return x if nonestr is None else nonestr
        t = type(x)
        if t in typerepresenters:
            rep = typerepresenters[t]
            if callable(rep):
                x = rep(x)
            else:
                x = rep

        ret = x
        if fmt:
            ret = fmt.format(idx=idx, val=x)
        else:
            if style in [ "s", "str" ]:
                ret = str(x)
            elif style in [ "r", "repr" ]:
                ret = repr(x)
            elif style in [ "stringify" ]:
                ret = stringify(x)
            elif style in [ "j", "json" ]:
                ret = pretty(x, style='json')
            elif style in [ "y", "yaml" ]:
                ret = pretty(x, style='yaml')
            else:
                ret = str(x)
        if quote:
            ret = quoted(ret, quote=quote, quote_if=quote_if)
        return ret

    if len(strs) == 1 and isinstance(strs[0], list):
        strs = strs[0]

    if fmt:
        strs = [ format_val(v, idx=i) for i, v in enumerate(strs) ]
    else:
        strs = [ format_val(v) for v in strs ]

    line = prefix + joiner.join(strs)
    if file is None:
        file = output_handle if output_handle else sys.stderr

    print(line , file=file, end=end)

    if flush:
        file.flush()

def eod(tag, o):
    """ dump a data item """
    eo(f"{tag} (type {type(o)})", { 'data': o } )

def eodir(o):
    eo(f"index of object of type: {type(o)}:")
    eo("    " + "\n    ".join(sorted(dir(o))))

def eostack():
    # pylint: disable=protected-access
    f = sys._getframe().f_back.f_back
    eo("".join(traceback.format_stack(f=f)))
    eo("")

def msgx(joiner, *args, **kwargs):
    items = [ 'None' if x is None else stringify_value(x, 3, 6, 400) for x in args]
    kwargs['joiner'] = joiner
    eo(items, **kwargs)

def warn(*args, **kwargs):
    warnmsg(args, **kwargs)

def msg(*args, **kwargs):
    msgx(" ", *args, **kwargs)

def msgl(*args, **kwargs):
    msgx("\n", *args, **kwargs)

def err(*args, **kwargs):
    msg("ERROR:", *args, **kwargs)

def errmsg(*args, **kwargs):
    err(*args, **kwargs)

def info(*args, **kwargs):
    msg("INFO:", *args, **kwargs)

def warnmsg(*args, **kwargs):
    msg("WARNING:", *args, **kwargs)

def err_exit(exitValue, *args, **kwargs):
    err(*args, **kwargs)
    sys.exit(exitValue)

def err_exit_if(condition, *args, **kwargs):
    if condition:
        err_exit(1, *args, **kwargs)

def verb(*args, **kwargs):
    global VERBOSE
    if VERBOSE:
        msg(*args, **kwargs)

def vverb(level, *args, **kwargs):
    global VERBOSE
    if VERBOSE >= level:
        msg(*args, **kwargs)

def dbgexit(*args):
    msg("Exiting:", *args)
    #confess("Debugexit")
    sys.exit(1)

def usage_msg(*args):
    script = scriptname()
    prog = progname()
    def munge(line):
        line = line.replace("%PROG%", prog)
        line = line.replace("%SCRIPT%", script)
        return line

    lines = [munge(line) for line in args ]
    msgx("\n", *lines)

def dbgmsg(*args):
    global DEBUG
    if DEBUG:
        caller = inspect.stack()[1]
        func = caller.function
        line = caller.lineno
        filename = os.path.basename(caller.filename)
        prog = progname()
        text = f"{prog}:{filename}.{func}:{line}:" + " ".join([str(x) for x in args])
        global DEBUG_REGEX
        if DEBUG_REGEX is not None:
            if re.match(DEBUG_REGEX, text):
                return
        msg(text)

def dbgdump(item):
    global DEBUG
    if DEBUG:
        caller = inspect.stack()[1]
        func = caller.function
        line = caller.lineno
        filename = os.path.basename(caller.filename)
        prog = progname()
        eo(f"{prog}:{filename}.{func}:{line}:" + pformat(item))


def read_file(path):
    try:
        with open(path, 'r'):
            return path.read()
    except:
        if VERBOSE:
            traceback.print_exc()
        else:
            eo(f"Failed reading file: {path}")
        return False

def read_file_lines(path):
    try:
        with open(path, 'r'):
            return path.readlines()
    except:
        if VERBOSE:
            traceback.print_exc()
        else:
            eo(f"Failed reading file: {path}")
        return False

def write_file(path, contents):
    try:
        with open(path, 'w') as f:
            print(contents, file=f)
            return True
    except:
        if VERBOSE:
            traceback.print_exc()
        else:
            eo(f"Failed writing file: {path}")
        return False


def os_path_splitall(path):
    """
    helper for the all-around shitness of os.path, which can
    only split /a/big/long/path into (/a/big/long, path)
    and does not provide anything to give ('/a', 'big/long/path') or ('/','a','big','long',path')
    """
    split = os.path.split(path)
    if split[0] == "" and split[1] == "":
        return []
    elif split[1] == "":
        return os_path_splitall(split[0])
    else:
        return os_path_splitall(split[0]) + [split[1]]

def indented(*items, indent=None):
    if not items:
        return ""
    if indent is None:
        indent = "    "
    ind = "\n" + indent
    return ind.join(items)

def isatty():
    return sys.stdin.isatty()


def tb(file=None):
    if file is None:
        file = sys.stderr
    traceback.print_stack(file=file)


def print_lines(lines, file='__unspecified__'):
    """
    Print lines to a filehandle, unless filehandle is None.
    Like other routines, this will default to sys.stderr if no file parameter
    but unlike other routines, if file=None is passed, it will be silent
    """
    if file == '__unspecified__':
        file = sys.stderr
    elif file is None:
        return
    for line in lines:
        print(line, file=file)


def test():
    global DEBUG
    global VERBOSE
    DEBUG = 0
    VERBOSE = 0
    vverb(1, "test 1\n")
    increment_verbose(1)
    vverb(1, "test 1\n")

    _sio = output_buffer()
    eo("printed to buffer")
    (_buf, buflen, _bufdata) = output_pop(print_to_upper=True)
    eo("buffered length was ", buflen)

    eo("abc def")
    abc = "ABC"
    def_ = "DEF"
    # fstring usage, will write to stderr
    eo(f"{abc} {def_}")
    # print all arguments, separated by a joiner(defaults to a space)
    eo("abc", def_)
    # print comma separated
    eo("a","b","c","d", joiner=",")
    # write without line ending
    eo("no line ending", end="")
    eo("another line")
    # write to specific file
    eo("write to stdout", file=sys.stdout)
    # print indented lines
    eo([1,2,3,4], indent="    ")
    eo(["a","b","c","d"], fmt="{idx:02d}. {val}\n")
    eo("a","b","c","d", fmt="{idx:02d}. {val}\n")
    eo("a","b c d","", quote_if="always")
    eo("a","b c d","", quote_if="empty,space")
    eo("print array with a None value", [ None, 1, 2, 3, "a" ])
    eo("print with a None value", "a", 1, None, "d")



if __name__ == "__main__":
    test()

