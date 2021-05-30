Module eyeo
===========
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

Sub-modules
-----------
* eyeo.examples
* eyeo.eyeo_test
* eyeo.stringify
* eyeo.stringify_examples

Functions
---------

    
`dbgdump(item)`
:   Only if debugging is enabled, print an item with debugging info (code location).
    Unlike dbgmsg(), the data item will be formatted with pprint.pformat()
    
    Parameters:
        item: the item to print

    
`dbgexit(*args)`
:   Print a debug message and exit with status 1
    
    Parameters:
        args: the items to print

    
`dbgmsg(*args)`
:   Only if debugging is enabled, print items with debugging info (code location), using msg() for the printing style.
    ie use stringify if necesary.
    
    Parameters:
        args: the items to print

    
`eo(*strs, file=None, end=None, flush=None, joiner=None, starter=None, indent=None, style=None, fmt=None, quote=None, quote_if=None, nonestr=None, lf=None)`
:   example usage:
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
           lf(string, "
    "):             use this as the line separator (replaces joiner when indent mode is enabled)

    
`eocmd(*strs, **kwargs)`
:   Output a command string list in a convenient manner for viewing a command.
    ie separate with spaces, quote each item if it is empty, contains spaces, or contains the quote character.
    
    Parameters:
        kwargs (dict): see eo(). if quote_if is present, its value will be ignored.

    
`eod(tag, o)`
:   dump a data item. Prints the specified tag as an identifier, followed by the type of the data, and the data itself.
    
    Parameters:
        tag: a value to be printed before the data, like a name
        o: the object or data to print

    
`eodir(o)`
:   print the type and dir() of an object
    
    Parameters:
        o (object or data): the data to print

    
`eoind(first, *remainder, file=None, end=None, flush=None, joiner=None, starter=None, indent=None, style=None)`
:   eo indented:
    example usage:
    eoind("Some data:", a, b, c, d, indent="    ")
    eoind("Some data:", [ 1, 2, 3, 4], indent="  ")

    
`eostack()`
:   print a stack trace

    
`err(*args, **kwargs)`
:   Print an error msg (prefix with "ERROR:")
    
    Parameters:
        see msg() or eo()

    
`err_exit(exitValue, *args, **kwargs)`
:   Print an error message and then call sys.exit with the specified exit value.
    
    Parameters:
    exitValue (int): the value to pass to sys.exit()
    args:           see err()

    
`err_exit_if(condition, *args, **kwargs)`
:   Trigger err_exit if a condition is met.
    
    Parameters:
        condition: bool or truthy - if truthy, an exit will be triggered.
        args:      see err_exit()
        kwargs:    see err_exit()

    
`errmsg(*args, **kwargs)`
:   alias for err()

    
`get_debug()`
:   Return the current global debug verbosity level
    
    Returns:
        int: the debug level

    
`get_type_representer(t)`
:   Get the type representer function for a type registered earlier with register_type_representer()
    
    Parameters:
        t (type): the type to look up
    Returns:
        function: the type representer function

    
`get_verbose()`
:   Return the current global verbosity level
    
    Returns:
        int: the global verbosity level

    
`increment_debug(amount=None)`
:   Increment the global debug verbosity by 1 or by a specified amount.
    
    Parameters:
        amount (int): the amount to increment the debug verbosity level by (default 1)
    
    Returns:
        int: the new debug level

    
`increment_verbose(amount=None)`
:   Increment the global verbosity by 1 or by a specified amount.
    
    Parameters:
        amount (int): the amount to increment the verbosity level by (default 1)
    
    Returns:
        int: the new level

    
`indented(*items, indent=None, indent_first=False)`
:   Return a string containing some number of items on different lines, indented with an indent string.
    
    Parameters:
        items: an iterable
        indent: the object or text to use as the indent at the start of each line
    
    Returns:
        The text of the lines, combined with indentation

    
`info(*args, **kwargs)`
:   Print an info msg (prefix with "INFO:")
    
    Parameters:
        see msg() or eo()

    
`isatty()`
:   return true if sys.stdin is detected as being a tty

    
`msg(*args, **kwargs)`
:   msgx style printing but provide a default joiner of a single space ' '.
    See msgx() and eo().
    
    Parameters:
        args: the items to print
        kwargs: the options for eo()

    
`msgl(*args, **kwargs)`
:   msgx style using a linefeed as the item separator.
    ie print items on separate lines.
    
    Parameters:
        See msgx() and/or eo()

    
`msgx(joiner, *args, **kwargs)`
:   print some data items with a joiner string, but using stringify_value() to convert the items o strings
    see eo() for optional kwarg parameters
    
    Parameters:
        joiner: the object or string to use to join items
        args: the items to join and print
        kwargs: see eo() for additional information.

    
`os_path_splitall(path, support_unc=False)`
:   Helper for the all-around shitness of os.path, which can
    only split /a/big/long/path into (/a/big/long, path)
    and does not provide anything to give ('/a', 'big/long/path') or ('/','a','big','long',path')
    
    Parameters:
        path (str): The filesystem path
    
    Returns:
        list: a list of the path components

    
`output_add(fhandle)`
:   Set the current default output target filehandle for output routines in this module.
    This sets the output destination in a stack so that the prior output can be restored
    using the associated routine output_pop
    
    Parameters:
        fhandle (file): the new output destination
    
    Returns:
        file: the file handle that was passed in

    
`output_buffer()`
:   Create a new string buffer in the output stack and return it. The new string buffer
    will be set as the current destination for output. See output_pop() to remove it when
    you are done and restore the prior output target.
    
    Returns:
        StringIO: a StringIO object which is currently set as the output destination

    
`output_pop(print_to_upper=False)`
:   Remove the current output destination from the stack of output targets.
    If the current destination was a StringIO, its captured text and the length of that
    will be returned also, and this can be automatically printed to the new output destination
    using the print_to_upper flag.
    
    Parameters:
    
        print_to_upper (bool): If true and the current output target is a string buffer,
            then any data that was captured in it, will be printed to the new output destination
            after the pop is performed.
    
    Returns:
         None | tuple(file, int, str): None, or a tuple of the removed file, length of any popped string buffer data, and any popped string buffer data

    
`pretty(data, style=None, sort_keys=None, indent=None)`
:   pretty-print some data using some defaults which can be overridden.
    The default style is json.
    
    Parameters:
        data: the data to print
        style (str) one of 'json', 'yaml', or None to accept the default
        sort_keys (bool): print dicts in sorted order
        indent (str): the indentation to use
    
    Returns:
        str: the formatted string.

    
`print_lines(lines, file='__unspecified__')`
:   Print lines to a filehandle, unless filehandle is None.
    Like other routines, this will default to sys.stderr if no file parameter
    but unlike other routines, if file=None is passed, it will be silent
    
    Parameters:
        lines: an iterable of lines
        file: a file, or None

    
`progname()`
:   return the program name based on sys.argv[0] but with the directory path chopped off,
    and possibly the '.py' suffix chopped off (if present).
    
    Parameters:
        (none)
    
    Returns:
        str: the program name

    
`quoted(val, quote=None, quote_if=None)`
:   Provide a pseudo-intelligently quoted version of a provided value
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

    
`read_file(path)`
:   Read the specified file and return the contents
    
    Returns:
        str: the file contents, or None on error

    
`read_file_lines(path)`
:   Read a file and return the lines of text. Return None on error
    
    Parameters:
        path (str): the path of the file to read
    
    Returns:
        list[str] or None: the lines from the file, or None

    
`register_type_representer(t, func)`
:   Register a function that will act as a type representer for the specified type.
    
    Parameters:
        t: the type
        func: the function that will be used to produce a representation for values of type t

    
`reopen_to(fhandle, path, mode)`
:   close a filehandle and return a new one opened for the specified path and mode.
    example: sys.stdout = reopen_to(sys.stdout, "/tmp/log.txt", "w")
    
    Parameters:
        fhandle (file): the file handle to close (may be None)
        path (str): the new path to open
        mode (str): the file open mode, ie "r", "w"
    
    Returns:
        file: the new filehandle

    
`reopen_to_devnull(fhandle, mode)`
:   Close a filehandle and return a new one for /dev/null
    example: sys.stdout = reopen_to_devnull(sys.stdout, "w")
    
    Parameters:
        fhandle (file): the file to close (may be None)
        mode (str): the mode to use when opening /dev/null (for example "r", or "rw")
    
    Returns:
        file: the new /dev/null handle

    
`scriptname()`
:   Returns the basename of sys.argv[0]

    
`set_debug(amount=1)`
:   Set the current global debug verbosity level
    
    Parameters:
        amount (int): the new level
    
    Returns:
        int: the new level

    
`set_debug_regex(pattern)`
:   Set a regular expression that will select which debug lines should be displayed.
    
    Parameters:
        pattern (str|regex): the pattern, or None

    
`set_verbose(amount=1)`
:   Set the current global verbosity level
    
    Parameters:
        amount (int): the new level
    Returns:
        int: the new level

    
`setup_logging()`
:   Set up the global logging instance with some default configuration.

    
`tb(file=None)`
:   shortcut for traceback.print_stack() however with a default file output of sys.stderr
    
    Parameters:
        file (file): a file or None. if specified, use this file, otherwise use sys.stderr.

    
`todo(message)`
:   Print a todo message
    
    Parameters:
        message (str): the message to print

    
`usage_msg(*args)`
:   Print a program usage message including the passed in args as separate lines.
    The token %PROG% will be replaced with progname().
    The token %SCRIPT% will be replaced with scriptname().
    
    Parameters:
        args: the lines of usage data to print.

    
`verb(*args, **kwargs)`
:   Print a message if the verbosity level is higher than 0
    
    Parameters:
        args:       see msg()
        kwargs:     see msg()

    
`vverb(level, *args, **kwargs)`
:   Print a message if the verbosity level is higher than the specified level.
    
    Parameters:
        level:int   the debug level required for this message to be printed
        args:       see msg()
        kwargs:     see msg()

    
`warn(*args, **kwargs)`
:   alias for warnmsg()

    
`warnmsg(*args, **kwargs)`
:   Print a warning msg (prefix with "WARNING:")
    
    Parameters:
        see msg() or eo()

    
`write_file(path, contents)`
:   write some text contents to a file
    
    Parameters:
        path: the filesystem path
        contents: the text to write to the file
    
    Returns:
      bool:   True on success, False on failure

Classes
-------

`FakeYaml()`
:   

    ### Static methods

    `dumps(data, sort_keys=None, default_flow_style=None, indent=None, default_style=None, line_break=None)`
    :

`yaml()`
:   

    ### Static methods

    `dumps(data, sort_keys=None, default_flow_style=None, indent=None, default_style=None, line_break=None)`
    :

`GlobalLoggingInstance()`
:   A global logging instance, set up by setup_logging below

    ### Class variables

    `log`
    :

    ### Static methods

    `setup_logging()`
    :   Set up the global logging instance with some default configuration.
