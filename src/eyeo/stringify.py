# pylint: disable=missing-function-docstring,unused-wildcard-import,line-too-long,trailing-newlines,missing-module-docstring,wildcard-import,invalid-name

"""
compact string dumper for objects intended to 'kind of' show the object, ie show enough of it to show what it is,
however prevent gigantic dumps of text through depth limits and string ellipsis
"""

def is_obj(x):
    """
    A quick (but maybe not perfect) check for object types

    Returns:
      bool: True if the object has __dict__ attribute, otherwise False
    """
    try:
        # pylint: disable=bare-except
        getattr(x, '__dict__')
        return True
    except:
        return False

def stringify_value(v, maxDepth=None, maxItems=-1, maxStrlen=-1):
    """
    Use stringify() to convert a value to a string, and return the string representation.

    Parameters:
        see stringify()
    Returns:
        the string representation of the object
    """
    (_, result) = stringify(v, maxDepth, maxItems, maxStrlen)
    return result

def stringify(v, maxDepth=None, maxItems=-1, maxStrlen=-1):
    """
    Convert a dict to a string representation.

    Parameters:
        d(dict) : the data dict to convert
        maxDepth (int|None):   if > 0, then ellipsise structures deeper than this
        maxItems (int|-1):     if > 0, then ellipsise lists longer than this or dicts with more than this many items
        maxStrlen (int|-1):    if > 0, then ellipsise strings longer than this

    Returns:
        tuple(depth:int, str): the depth (explored) of the structure and the string representation of the data
    """
    return _stringify(v, maxDepth=maxDepth, maxItems=maxItems, maxStrlen=maxStrlen)

def _stringify(v, maxDepth=None, maxItems=-1, maxStrlen=-1, callingDepth=0, recursionMap=None):
    """
    Private implementation of stringify()

    Parameters:
        callingDepth (int|-1): keeps track of the current level of recursion, to implement maxDepth
        recursionMap (dict):   keeps track of already-printed objects to short-circuit infinite recursion.
        (others): see stringify_hash()

    Returns:
        tuple(depth:int, str): the depth (explored) of the structure and the string representation of the data
    """
    # pylint: disable=too-many-return-statements,too-many-arguments
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
        return _stringify_array(v, maxDepth, maxItems, maxStrlen, callingDepth, recursionMap)
    if t in [dict] or 'AttrDict' in str(t):
        return _stringify_hash(v, maxDepth, maxItems, maxStrlen, callingDepth, recursionMap)
    if 'Gtk' in r or 'Gdk' in r or 'Glib' in r:
        return (1,"(Gtk-object)")
    if isinstance(v, str):
        return (1, v)
    if is_obj(v):
        d = dict(v.__dict__)
        (depth, result) = _stringify(d, maxDepth, maxItems, maxStrlen, callingDepth, recursionMap)
        return (depth, r + result)
    if callable(v):
        return (1,"(callable)")
    return (1, str(v))

def stringify_array(v,
                    maxDepth=None,
                    maxItems=-1,
                    maxStrlen=-1):
    """
    Convert a dict to a string representation.

    Parameters:
        d(dict) : the data dict to convert
        maxDepth (int|None):   if > 0, then ellipsise structures deeper than this
        maxItems (int|-1):     if > 0, then ellipsise lists longer than this or dicts with more than this many items
        maxStrlen (int|-1):    if > 0, then ellipsise strings longer than this

    Returns:
        tuple(depth:int, str): the depth (explored) of the structure and the string representation of the data
    """
    return _stringify_array(v, maxDepth=maxDepth, maxItems=maxItems, maxStrlen=maxStrlen)

def _stringify_array(v,
                    maxDepth=None,
                    maxItems=-1,
                    maxStrlen=-1,
                    callingDepth=0,
                    recursionMap=None):
    # pylint: disable=too-many-arguments
    """
    Private implementation of stringify_array()

    Parameters:
        callingDepth (int|-1): keeps track of the current level of recursion, to implement maxDepth
        recursionMap (dict):   keeps track of already-printed objects to short-circuit infinite recursion.
        (others): see stringify_hash()

    Returns:
        tuple(depth:int, str): the depth (explored) of the structure and the string representation of the data
    """
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
        (depth, child) = _stringify(item, maxDepth, maxItems, maxStrlen, callingDepth + 1, recursionMap)

        if depth > max_inner_depth:
            max_inner_depth = depth

        out.append(child)

    if maxItems >= 0:
        more = len(out) - maxItems
        if maxItems >= 0 and more > 0:
            out = out[0:maxItems] + [f"...(+{more} items)"]

    if result is None:
        result = ",".join(out)

    if 3 <= maxStrlen < len(result):
        result = result[0:maxStrlen-3] + "..."

    result = "[" + result + "]"
    return (max_inner_depth + 1, result)



def stringify_hash(d, maxDepth=None, maxItems=-1, maxStrlen=-1):
    """
    Convert a dict to a string representation.

    Parameters:
        d(dict) : the data dict to convert
        maxDepth (int|None):   if > 0, then ellipsise structures deeper than this
        maxItems (int|-1):     if > 0, then ellipsise lists longer than this or dicts with more than this many items
        maxStrlen (int|-1):    if > 0, then ellipsise strings longer than this

    Returns:
        tuple(depth:int, str): the depth (explored) of the structure and the string representation of the data
    """
    return _stringify_hash(d, maxDepth=maxDepth, maxItems=maxItems, maxStrlen=maxStrlen)


def _stringify_hash(
        d,
        maxDepth=None,
        maxItems=-1,
        maxStrlen=-1,
        callingDepth=0,
        recursionMap=None):
    # pylint: disable=too-many-arguments,too-many-locals
    """
    Private implementation for stringify_hash(), with extra parameters for internal use only.

    Parameters:
        callingDepth (int|-1): keeps track of the current level of recursion, to implement maxDepth
        recursionMap (dict):   keeps track of already-printed objects to short-circuit infinite recursion.
        (others): see stringify_hash()

    Returns:
        tuple(depth:int, str): the depth (explored) of the structure and the string representation of the data
    """
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
        (depth, child) = _stringify(v, maxDepth, maxItems, maxStrlen, callingDepth + 1, recursionMap)

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
    """
    Use stringify_value() to dump an item, with some defaults.

    Parameters:
        item: the data to convert to string
    """
    return stringify_value(item, 3, 0)
