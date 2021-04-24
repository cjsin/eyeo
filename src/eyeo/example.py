from eyeo import *

def eyeo_examples():
    """
    Example usage of some routines provided by this module.
    """
    global DEBUG
    global VERBOSE
    DEBUG = 0
    VERBOSE = 0
    vverb(1, "test 1\n")
    increment_verbose(1)
    vverb(1, "test 1\n")

    eo("A simple message")
    eo("A simple message with", "extra", "data")
    eo("A simple message with format strings {} {}", "for", "data")
    eo(["a","list"])

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
    eyeo_examples()
