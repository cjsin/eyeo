# pylint: disable=missing-function-docstring,unused-wildcard-import,line-too-long,trailing-newlines,missing-module-docstring,wildcard-import,invalid-name
# pylint: disable=too-many-lines
"""

# A module for simplifying regular basic output printing in common situations

For example, these simple types of printing:

    print("Some things: {} and data {}".format(1, {"a": 123}), file=sys.stderr)
    eo("Some things: {} and data {}, 1, {"a": 123})

    for x in ["a","b","c"]:
        print("    "+x, file=sys.stderr)
    eo("a","b","c", indent="    ")

    print("data=" + str(data), file=sys.stderr)
    eo("data=", data)

    print(", ".join("{02d}={}".format(idx,val) for idx,val in enumerate(items)))
    eo(items, joiner=", ", fmt="{idx:02d}. {val}")

## Output stack

The output stack provides the ability to temporarily make the routines print to
a different destination, or capture the output to a string.

For example:

    eo("This prints to stderr")
    with open("file.txt") as f:
        output_add(f)
        eo("This prints to f")
        strbuf = output_buffer()

        # output from the output functions within this module will be printed to strbuf
        call_some_routine()
        output_pop()
        eo("This prints to f again")
    output_pop()
    eo("This prints to stderr again")
"""

import os
import re
import sys
import inspect
import traceback
import logging
import json

from io import StringIO
from pprint import pformat

from eyeo.stringify import stringify, stringify_value

typerepresenters = {}

try:
    # pylint: disable=import-error
    # pylint: disable=bare-except
    import yaml
except:
    class FakeYaml:
        # pylint: disable=too-few-public-methods
        """ fake yaml class to substitute for missing (optional) yaml module """
        @classmethod
        def dumps(cls, data, sort_keys=None, default_flow_style=None, indent=None, default_style=None, line_break=None):
            # pylint: disable=unused-argument,too-many-arguments
            msg("Warning - no yaml support - falling back to json format")
            return json.dumps(data, sort_keys=sort_keys)

    yaml = FakeYaml

class GlobalLoggingInstance:
    # pylint: disable=too-few-public-methods
    """
    A global logging instance, set up by setup_logging below
    """
    log = None

    @classmethod
    def setup_logging(cls):
        """
        Set up the global logging instance with some default configuration.
        """
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
    """
    Set up the global logging instance with some default configuration.
    """
    GlobalLoggingInstance.setup_logging()

def register_type_representer(t, func):
    """
    Register a function that will act as a type representer for the specified type.

    Parameters:
        t: the type
        func: the function that will be used to produce a representation for values of type t
    """
    typerepresenters[t] = func

def get_type_representer(t):
    """
    Get the type representer function for a type registered earlier with register_type_representer()

    Parameters:
        t (type): the type to look up
    Returns:
        function: the type representer function
    """
    return typerepresenters.get(t)

def todo(message):
    """
    Print a todo message

    Parameters:
        message (str): the message to print
    """
    eo("TODO: " + message)


def _init_level(name, defaultval=0):
    """
    Determine a default verbosity or debug level from the environment values.
    Treats y,yes,on,true,t (upper or lower case) as 1,
    and n,no,off,false,f (upper or lower case) as 0,
    otherwise will expect an int in string format.

    Parameters:
        name (str): the name of the environment variable to check
        defaultval (int): the value to return if the environment variable is not found.

    Returns:
        int:  the level found in the environment, or the defaultval
    """
    if name not in os.environ:
        return defaultval

    val = os.environ.get(name, '')
    if val in [ None, ""]:
        return defaultval
    if val.isdigit():
        return int(val)
    if val.lower() in [ 'y', 'yes', 'on', 'true', 't' ]:
        return 1
    if val.lower() in [ 'n', 'no', 'off', 'false', 'f' ]:
        return 0
    return defaultval

class Globals:
    """ Scoping class for globals """
    # pylint: disable=too-few-public-methods
    VERBOSE = 0
    DEBUG = 0
    DEBUG_REGEX = None
    # used by output_add, output_pop and 'eo'
    output_stack = []
    output_handle = None

Globals.VERBOSE = _init_level('VERBOSE', 0)
Globals.DEBUG = _init_level('DEBUG', 0)
Globals.DEBUG_REGEX = os.environ.get('DEBUG_REGEX', None)

globals()['VERBOSE'] = Globals.VERBOSE
globals()['DEBUG'] = Globals.DEBUG
globals()['DEBUG_REGEX'] = Globals.DEBUG_REGEX

def set_debug_regex(pattern):
    """
    Set a regular expression that will select which debug lines should be displayed.

    Parameters:
        pattern (str|regex): the pattern, or None
    """
    if pattern is None or pattern == '':
        Globals.DEBUG_REGEX = None
    else:
        Globals.DEBUG_REGEX = re.compile(pattern)

def increment_debug(amount=None):
    """
    Increment the global debug verbosity by 1 or by a specified amount.

    Parameters:
        amount (int): the amount to increment the debug verbosity level by (default 1)

    Returns:
        int: the new debug level
    """
    if amount is None:
        amount = 1
    Globals.DEBUG += amount
    return Globals.DEBUG

def progname():
    """
    return the program name based on sys.argv[0] but with the directory path chopped off,
    and possibly the '.py' suffix chopped off (if present).

    Parameters:
        (none)

    Returns:
        str: the program name
    """
    prog = scriptname()
    if prog.endswith('.py'):
        prog = prog[0:-3]
    return prog

def scriptname():
    """
    Returns the basename of sys.argv[0]
    """
    return os.path.basename(sys.argv[0])

def increment_verbose(amount=None):
    """
    Increment the global verbosity by 1 or by a specified amount.

    Parameters:
        amount (int): the amount to increment the verbosity level by (default 1)

    Returns:
        int: the new level
    """
    if amount is None:
        amount = 1
    Globals.VERBOSE += amount
    return Globals.VERBOSE

def get_verbose():
    """
    Return the current global verbosity level

    Returns:
        int: the global verbosity level
    """
    return Globals.VERBOSE

def set_verbose(amount=1):
    """
    Set the current global verbosity level

    Parameters:
        amount (int): the new level
    Returns:
        int: the new level
    """
    Globals.VERBOSE = amount
    return Globals.VERBOSE

def get_debug():
    """
    Return the current global debug verbosity level

    Returns:
        int: the debug level
    """
    return Globals.DEBUG

def set_debug(amount=1):
    """
    Set the current global debug verbosity level

    Parameters:
        amount (int): the new level

    Returns:
        int: the new level
    """
    Globals.DEBUG = amount
    return Globals.DEBUG

def output_add(fhandle):
    """
    Set the current default output target filehandle for output routines in this module.
    This sets the output destination in a stack so that the prior output can be restored
    using the associated routine output_pop

    Parameters:
        fhandle (file): the new output destination

    Returns:
        file: the file handle that was passed in
    """
    Globals.output_stack.append(fhandle)
    Globals.output_handle = fhandle
    return fhandle

def output_buffer():
    """
    Create a new string buffer in the output stack and return it. The new string buffer
    will be set as the current destination for output. See output_pop() to remove it when
    you are done and restore the prior output target.

    Returns:
        StringIO: a StringIO object which is currently set as the output destination
    """
    return output_add(StringIO())

def output_pop(print_to_upper=False):
    """
    Remove the current output destination from the stack of output targets.
    If the current destination was a StringIO, its captured text and the length of that
    will be returned also, and this can be automatically printed to the new output destination
    using the print_to_upper flag.

    Parameters:

        print_to_upper (bool): If true and the current output target is a string buffer,
            then any data that was captured in it, will be printed to the new output destination
            after the pop is performed.

    Returns:
         None | tuple(file, int, str): None, or a tuple of the removed file, length of any popped string buffer data, and any popped string buffer data
    """
    if not Globals.output_stack:
        print(" output_pop is returning None because there is no output stack", file=sys.stderr)
        return None

    len_value = None
    data_value = None
    popped = Globals.output_stack.pop()
    ret = Globals.output_handle
    if ret != popped:
        print("ERROR: output stack got out of sync with expected output handle", file=sys.stderr)

    if Globals.output_stack:
        Globals.output_handle = Globals.output_stack[-1]
    else:
        Globals.output_handle = None

    if isinstance(ret, StringIO):
        ret.seek(0)
        data_value = ret.read()
        len_value = len(data_value)
    if print_to_upper:
        if data_value:
            eo(data_value, end="")
        else:
            #print(f"Popped handle is of type ({type(ret)}), cannot print_to_upper", file=sys.stderr)
            pass

    ret.flush()
    #print(f" output_pop is returning ret={ret}, len_value={len_value}, data_value={data_value}", file=sys.stderr)
    return (ret, len_value, data_value)

def reopen_to(fhandle, path, mode, encoding=None):
    """
    close a filehandle and return a new one opened for the specified path and mode.
    example: sys.stdout = reopen_to(sys.stdout, "/tmp/log.txt", "w")

    Parameters:
        fhandle (file): the file handle to close (may be None)
        path (str): the new path to open
        mode (str): the file open mode, ie "r", "w"

    Returns:
        file: the new filehandle
    """
    # pylint: disable=consider-using-with
    if encoding is None:
        encoding = "utf-8"
    newhandle = open(path, mode, encoding=encoding)
    if fhandle:
        fhandle.flush()
        fhandle.close()
    return newhandle

def reopen_to_devnull(fhandle, mode):
    """
    Close a filehandle and return a new one for /dev/null
    example: sys.stdout = reopen_to_devnull(sys.stdout, "w")

    Parameters:
        fhandle (file): the file to close (may be None)
        mode (str): the mode to use when opening /dev/null (for example "r", or "rw")

    Returns:
        file: the new /dev/null handle
    """
    return reopen_to(fhandle, "/dev/null", mode)

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
    """
    Provide a pseudo-intelligently quoted version of a provided value
    - ie avoid quoting in some situations (such as empty strings or strings with no whitespace)
    and escape the quote character if it is present in the string.

    Parameters:

        quote (str): a specific quote character that is desired. None represents no quoting.
        quote_if: None or "" or a comma separated string of behaviour modifiers ("e", "a", "q", "s")
              e means quote even the empty string
              a means always quote
              s means quote if whitespace is present
              q means quote if it contains the quote character already.

    Returns:
        str: the quoed string
    """
    if quote is None:
        return val

    if quote_if is None or quote_if == "":
        return val

    needs_quoting = False
    conditions = quote_if.split(",")
    conditions = [q[0] for q in conditions if q]
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
    """
    Output a command string list in a convenient manner for viewing a command.
    ie separate with spaces, quote each item if it is empty, contains spaces, or contains the quote character.

    Parameters:
        kwargs (dict): see eo(). if quote_if is present, its value will be ignored.
    """
    kwargs['quote_if'] = 'e,s,q'
    if 'quote' not in kwargs:
        kwargs['quote'] = "'"
    eo(*strs, **kwargs)


def pretty(data, style=None, sort_keys=None, indent=None):
    """
    pretty-print some data using some defaults which can be overridden.
    The default style is json.

    Parameters:
        data: the data to print
        style (str) one of 'json', 'yaml', or None to accept the default
        sort_keys (bool): print dicts in sorted order
        indent (str): the indentation to use

    Returns:
        str: the formatted string.
    """
    if indent is None:
        indent = 4
    if style is None:
        style = 'json'
    if sort_keys is None:
        sort_keys = True
    if style == 'yaml':
        return yaml.dump(data, sort_keys=sort_keys, default_flow_style=False, indent=indent, default_style=None, line_break="\n")
    return json.dumps(data, sort_keys=sort_keys, separators=(", ", " : "), indent=indent)

def eo(*args, file=None, end=None, flush=None,
            joiner=None, starter=None, indent=None,
            style=None, fmt=None, quote=None, quote_if=None,
            nonestr=None, lf=None, _debug=None):
    # pylint: disable=too-many-locals
    """
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
       nonestr(string,"")            replace None with this string in some situations
       lf(string, "\n"):             use this as the line separator (replaces joiner when indent mode is enabled)

    """

    # pylint: disable=too-many-statements,too-many-branches

    args = list(args)
    strs = []

    # Support this style:
    #    eo("a format {} with {}", "string", "data")
    # as long as no other contradictory options were passed
    # pylint: disable=too-many-boolean-expressions
    if (fmt is None
        and args
        and args[0]
        and isinstance(args[0], str)
        and "{}" in args[0]
        and args[0].count("{}") == len(args) -1
        and indent is None and joiner is None and style is None):
        fmt = args.pop(0)
        if file is None:
            file = Globals.output_handle if Globals.output_handle else sys.stderr
        print(fmt.format(*args) , file=file, end=end)
        if flush:
            file.flush()
        return

    if nonestr is None:
        nonestr = "(None)"
    if lf is None:
        lf = os.linesep

    if style is None:
        style = 'str'

    #if _debug:
    #    print(f"quote={quote}, quote_if={quote_if}")

    if quote_if is not None and quote is None:
        quote = "'"
    #if _debug:
    #    print(f"quote={quote}, quote_if={quote_if}")
    if quote_if is None:
        quote_if = 'empty,space,quote'
    if _debug:
        print(f"quote={quote}, quote_if={quote_if}")

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
        #if _debug:
        #    print("Formatting x")
        if quote:
            orig = ret
            ret = quoted(ret, quote=quote, quote_if=quote_if)
            if _debug:
                print(f"ret={ret} for quoted(\"{orig}\",quote=\"{quote}\", quote_if=\"{quote_if}\"")
        elif _debug:# and quote_if:
            print("NOT using quoted(), quote=" + str(quote) + " and quote_if=" + str(quote_if), file=sys.stderr)
        return ret

    if len(args) == 1 and isinstance(args[0], list):
        args = args[0]

    if fmt:
        strs = [ format_val(v, idx=i) for i, v in enumerate(args) ]
    else:
        strs = [ format_val(v) for v in args ]

    line = prefix + joiner.join(strs)
    if file is None:
        file = Globals.output_handle if Globals.output_handle else sys.stderr

    print(line , file=file, end=end)

    if flush:
        file.flush()

def eod(tag, o):
    """
    dump a data item. Prints the specified tag as an identifier, followed by the type of the data, and the data itself.

    Parameters:
        tag: a value to be printed before the data, like a name
        o: the object or data to print
    """
    eo(f"{tag} (type {type(o)})", { 'data': o } )

def eodir(o):
    """
    print the type and dir() of an object

    Parameters:
        o (object or data): the data to print
    """
    eo(f"index of object of type: {type(o)}:")
    eo("    " + "\n    ".join(sorted(dir(o))))

def eohelp(x):
    eo(f"Object of type {type(x)}")
    eo("")
    help(x)

def stacktrace(goback=0):
    # pylint: disable=protected-access
    f = sys._getframe()
    f = f.f_back
    while goback:
        f = f.f_back
        goback -= 1
    return "".join(traceback.format_stack(f=f))

def tb(file=None):
    """
    shortcut for traceback.print_stack() however with a default file output of sys.stderr

    Parameters:
        file (file): a file or None. if specified, use this file, otherwise use sys.stderr.
    """
    if file is None:
        file = sys.stderr
    traceback.print_stack(file=file)

def current_line_number(frames=1):
    try:
        raise Exception()
    except:
        frame = sys.exc_info()[2].tb_frame
        while frames:
            frame = frame.f_back
            frames -= 1
        return frame.f_lineno

class LINE:
    def __repr__(self):
        return str(current_line_number(frames=2))
    def __call__(self, *args, **kwds):
        return current_line_number(frames=2)

__LINE__ = LINE()
__line__ = __LINE__

def eostack():
    """
    print a stack trace
    """
    # pylint: disable=protected-access
    eo(stacktrace(2))
    eo("")

def msgx(joiner, *args, **kwargs):
    """
    print some data items with a joiner string, but using stringify_value() to convert the items o strings
    see eo() for optional kwarg parameters

    Parameters:
        joiner: the object or string to use to join items
        args: the items to join and print
        kwargs: see eo() for additional information.
    """
    items = [ 'None' if x is None else stringify_value(x, 3, 6, 400) for x in args]
    kwargs['joiner'] = joiner
    eo(items, **kwargs)

def msg(*args, **kwargs):
    """
    msgx style printing but provide a default joiner of a single space ' '.
    See msgx() and eo().

    Parameters:
        args: the items to print
        kwargs: the options for eo()
    """
    msgx(" ", *args, **kwargs)

def warnmsg(*args, **kwargs):
    """
    Print a warning msg (prefix with "WARNING:")

    Parameters:
        see msg() or eo()
    """
    msg("WARNING:", *args, **kwargs)

def infomsg(*args, **kwargs):
    """
    Print an info msg (prefix with "INFO:")

    Parameters:
        see msg() or eo()
    """
    msg("INFO:", *args, **kwargs)

def warn(*args, **kwargs):
    """
    alias for warnmsg()
    """
    warnmsg(*args, **kwargs)

def msgl(*args, **kwargs):
    """
    msgx style using a linefeed as the item separator.
    ie print items on separate lines.

    Parameters:
        See msgx() and/or eo()
    """
    msgx("\n", *args, **kwargs)

def err(*args, **kwargs):
    """
    Print an error msg (prefix with "ERROR:")

    Parameters:
        see msg() or eo()
    """
    msg("ERROR:", *args, **kwargs)

def errmsg(*args, **kwargs):
    """
    alias for err()
    """
    err(*args, **kwargs)

def info(*args, **kwargs):
    """
    Print an info msg (prefix with "INFO:")

    Parameters:
        see msg() or eo()
    """
    msg("INFO:", *args, **kwargs)


def err_exit(exitValue, *args, **kwargs):
    """
    Print an error message and then call sys.exit with the specified exit value.

    Parameters:
    exitValue (int): the value to pass to sys.exit()
    args:           see err()
    """
    err(*args, **kwargs)
    sys.exit(exitValue)

def err_exit_if(condition, *args, **kwargs):
    """
    Trigger err_exit if a condition is met.

    Parameters:
        condition: bool or truthy - if truthy, an exit will be triggered.
        args:      see err_exit()
        kwargs:    see err_exit()
    """
    if condition:
        err_exit(1, *args, **kwargs)

def verb(*args, **kwargs):
    """
    Print a message if the verbosity level is higher than 0

    Parameters:
        args:       see msg()
        kwargs:     see msg()
    """
    if Globals.VERBOSE:
        msg(*args, **kwargs)

def vverb(level, *args, **kwargs):
    """
    Print a message if the verbosity level is higher than the specified level.

    Parameters:
        level:int   the debug level required for this message to be printed
        args:       see msg()
        kwargs:     see msg()
    """
    if Globals.VERBOSE >= level:
        msg(*args, **kwargs)

def verbmsg(*args, **kwargs):
    vverb(1, *args, **kwargs)

def dbgexit(*args):
    """
    Print a debug message and exit with status 1

    Parameters:
        args: the items to print
    """
    msg("Exiting:", *args)
    #confess("Debugexit")
    sys.exit(1)

def usage_msg(*args):
    """
    Print a program usage message including the passed in args as separate lines.
    The token %PROG% will be replaced with progname().
    The token %SCRIPT% will be replaced with scriptname().

    Parameters:
        args: the lines of usage data to print.

    """
    script = scriptname()
    prog = progname()
    def munge(line):
        line = line.replace("%PROG%", prog)
        line = line.replace("%SCRIPT%", script)
        return line

    lines = [munge(line) for line in args ]
    msgx("\n", *lines)

def dbgmsg(*args):
    """
    Only if debugging is enabled, print items with debugging info (code location), using msg() for the printing style.
    ie use stringify if necesary.

    Parameters:
        args: the items to print
    """
    if Globals.DEBUG:
        caller = inspect.stack()[1]
        func = caller.function
        line = caller.lineno
        filename = os.path.basename(caller.filename)
        prog = progname()
        text = f"{prog}:{filename}.{func}:{line}:" + " ".join([str(x) for x in args])
        if Globals.DEBUG_REGEX is not None:
            if not re.match(Globals.DEBUG_REGEX, text):
                return
        msg(text)

def dbgdump(item):
    """
    Only if debugging is enabled, print an item with debugging info (code location).
    Unlike dbgmsg(), the data item will be formatted with pprint.pformat()

    Parameters:
        item: the item to print
    """
    if Globals.DEBUG:
        caller = inspect.stack()[1]
        func = caller.function
        line = caller.lineno
        filename = os.path.basename(caller.filename)
        prog = progname()
        eo(f"{prog}:{filename}.{func}:{line}:" + pformat(item))


def read_file(path):
    """
    Read the specified file and return the contents

    Returns:
        str: the file contents, or None on error
    """
    try:
        # pylint: disable=bare-except
        # pylint: disable=unspecified-encoding
        with open(path, 'r') as f:
            return f.read()
    except:
        if Globals.VERBOSE:
            traceback.print_exc()
        else:
            eo(f"Failed reading file: {path}")
        return None

def read_file_lines(path):
    """
    Read a file and return the lines of text. Return None on error

    Parameters:
        path (str): the path of the file to read

    Returns:
        list[str] or None: the lines from the file, or None
    """
    try:
        # pylint: disable=bare-except
        # pylint: disable=unspecified-encoding
        with open(path, 'r') as f:
            return f.readlines()
    except:
        if Globals.VERBOSE:
            traceback.print_exc()
        else:
            eo(f"Failed reading file: {path}")
        return None

def write_file(path, contents):
    """
    write some text contents to a file

    Parameters:
        path: the filesystem path
        contents: the text to write to the file

    Returns:
      bool:   True on success, False on failure
    """
    try:
        # pylint: disable=bare-except
        with open(path, 'w', encoding='utf-8') as f:
            print(contents, file=f)
            return True
    except:
        if Globals.VERBOSE:
            traceback.print_exc()
        else:
            eo(f"Failed writing file: {path}")
        return False

def os_path_splitall(path, support_unc=False):
    # pylint: disable=too-many-return-statements
    """
    Helper for the all-around shitness of os.path, which can
    only split /a/big/long/path into (/a/big/long, path)
    and does not provide anything to give ('/a', 'big/long/path') or ('/','a','big','long',path')

    Parameters:
        path (str): The filesystem path

    Returns:
        list: a list of the path components
    """

    if path is None:
        return None

    if path == "":
        return None

    if len(path) > 1 and re.match(r'^[/]{2,}$', path):
        if support_unc:
            return ['//']
        return ['/']

    # if not support_unc:
    #     # os.path.normpath leaves '//' (does not normalise it)
    #     # when it is at the start
    #     while path.startswith("//"):
    #         path = path[1:]

    #npath = os.path.normpath(path)
    #if npath != path:
    #    msg(f"path='{path}' normalised to '{npath}'")
    #path = npath
    if path == '/':
        return ['/']

    split = os.path.split(path)
    if split[0] == "" and split[1] == "":
        return []

    if split[1] == "":
        msg(f"0='{split[0]}', 1='{split[1]}'")
        return os_path_splitall(split[0], support_unc=support_unc)

    if split[0] == "":
        return [split[1]]

    return os_path_splitall(split[0], support_unc=support_unc) + [split[1]]

def indented(*items, indent=None, indent_first=False):
    """
    Return a string containing some number of items on different lines, indented with an indent string.

    Parameters:
        items: an iterable
        indent: the object or text to use as the indent at the start of each line

    Returns:
        The text of the lines, combined with indentation
    """

    if not items:
        return ""
    if indent is None:
        indent = "    "
    else:
        indent = str(indent)
    ind = "\n" + indent
    prefix = indent if indent_first else ""
    return prefix + ind.join(str(i) for i in items)

def isatty():
    """
    return true if sys.stdin is detected as being a tty
    """
    return sys.stdin.isatty()

def print_lines(lines, file='__unspecified__'):
    """
    Print lines to a filehandle, unless filehandle is None.
    Like other routines, this will default to sys.stderr if no file parameter
    but unlike other routines, if file=None is passed, it will be silent

    Parameters:
        lines: an iterable of lines
        file: a file, or None
    """
    if file == '__unspecified__':
        file = sys.stderr
    elif file is None:
        return
    for line in lines:
        print(line, file=file)

