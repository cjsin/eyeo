Module eyeo
===========
# A module for simplifying regular basic output printing in common situations

For example, this:

    print("Some things: {} and data {}".format(1, {"a": 123}), file=sys.stderr)
    for x in ["a","b","c"]:
        print("    "+x, file=sys.stderr)

Can become:

    eo("Some things: {} and daa {}, 1, {"a": 123})
    eo("a","b","c", indent="    ")

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
