"""
compact string dumper for objects intended to 'kind of' show the object, ie show enough of it to show what it is, however prevent gigantic dumps of text
"""

def is_obj(x):
    try:
        getattr(x, '__dict__')
        return True
    except:
        return False

def stringify_value(v, maxDepth=None, maxItems=-1, maxStrlen=-1, callingDepth=0, recursionMap=None):
    (_, result) = stringify(v, maxDepth, maxItems, maxStrlen, callingDepth, recursionMap)
    return result

def stringify(v, maxDepth=None, maxItems=-1, maxStrlen=-1, callingDepth=0, recursionMap=None):
    if v is None:
        return ( 1, "(None)" )
    if recursionMap is None:
        recursionMap = {}

    t = type(v)
    r = t.__name__

    if len(r) > 0:
        if t not in [ int, float, str, bool, type(None) ]:
            if id(v) in recursionMap:
                return (1, "(recursion)")
            recursionMap[id(v)] = 1

    if t in [list, tuple]:
        return stringify_array(v, maxDepth, maxItems, maxStrlen, callingDepth, recursionMap)
    elif t in [dict] or 'AttrDict' in str(t):
        return stringify_hash(v, maxDepth, maxItems, maxStrlen, callingDepth, recursionMap)
    elif 'Gtk' in r or 'Gdk' in r or 'Glib' in r:
        return (1,"(Gtk-object)")
    elif isinstance(v, str):
        return (1, v)
    elif is_obj(v):
        d = dict(v.__dict__)
        (depth, result) = stringify(d, maxDepth, maxItems, maxStrlen, callingDepth, recursionMap)
        return (depth, r + result)
    elif callable(v):
        return (1,"(callable)")
    else:
        return (1, str(v))

def stringify_array(v,
                    maxDepth=None,
                    maxItems=-1,
                    maxStrlen=-1,
                    callingDepth=0,
                    recursionMap=None):
    if not v:
        return (0, "[]" )

    if recursionMap is None:
        recursionMap = {}

    count = len(v)

    result = None

    if maxDepth == 0:
        result = f"[({count} items)]"

        if maxItems >= 0:
            return (0, result)

    if maxDepth is not None:
        maxDepth -= 1

    max_inner_depth = 0
    out = []

    for item in v:
        (depth, child) = stringify(item, maxDepth, maxItems, maxStrlen, callingDepth + 1, recursionMap)

        if depth > max_inner_depth:
            max_inner_depth = depth

        out.append(child)

    if maxItems >= 0:
        more = len(out) - maxItems
        if maxItems >= 0 and more > 0:
            out = out[0:maxItems] + [f"...(+{more} items)"]

    if result is None:
        result = ",".join(out)

    if maxStrlen >= 3 and len(result) > maxStrlen:
        result = result[0:maxStrlen-3] + "..."

    result = "[" + result + "]"
    return (max_inner_depth + 1, result)

def stringify_hash(
        d,
        maxDepth=None,
        maxItems=-1,
        maxStrlen=-1,
        callingDepth=0,
        recursionMap=None):

    if not d:
        return (0, "{}")

    if recursionMap is None:
        recursionMap = {}

    keys = d.keys()
    nkeys = len(keys)
    ordered = sorted(keys)
    result = None

    if maxDepth == 0:
        result = "{(" + str(nkeys) + " items)}"

        if maxItems >= 0:
            return (0, result)

    if maxDepth is not None:
        maxDepth -= 1

    out = []
    max_inner_depth = 0

    for k in ordered:
        v = d[k]
        (depth, child) = stringify(v, maxDepth, maxItems, maxStrlen, callingDepth + 1, recursionMap)

        if depth > max_inner_depth:
            max_inner_depth = depth
        out.append(f"{k}={child}")

    if len(out) > maxItems:
        more = len(out) - maxItems
        out = out[0:maxItems] + [f"...(+{more} items)"]

    if result is None:
        result = "{" + ",".join(out) + "}"

    return (max_inner_depth + 1, result)


def dump(item):
    return stringify(item, 3, 0)
