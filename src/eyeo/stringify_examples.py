#!/bin/env python3
# pylint: disable=missing-function-docstring,unused-wildcard-import,line-too-long,trailing-newlines,missing-module-docstring,wildcard-import,invalid-name

from eyeo.stringify import *
from eyeo import msg

class XXX:
    """ test data tagged with a name to help identify the test """
    # pylint: disable=too-few-public-methods
    def __init__(self, name, datadict):
        self.name = name
        self.data = datadict

def stringify_test(item, maxDepth=None, maxItems=-1, maxStrlen=-1):
    msg(item.name)
    msg("  maxDepth  ", maxDepth)
    msg("  maxItems  ", maxItems)
    msg("  maxStrlen ", maxStrlen)
    result = stringify( item, maxDepth, maxItems, maxStrlen)
    depth, strval = result
    msg("  result depth ",  depth)
    msg("  result strval ", strval)
    return [depth, strval]

def test_stringify_examples():
    assert stringify_test(XXX("hash",              {})) \
                          == [2,"XXX{data={},...(+3 items)}"]
    assert stringify_test(XXX("hash",              {'a': 1})) \
                          == [3,"XXX{data={...(+2 items)},...(+3 items)}"]
    assert stringify_test(XXX("hash",              {'a': 1, 'b': 2})) \
                          == [3,"XXX{data={a=1,...(+3 items)},...(+3 items)}"]
    assert stringify_test(XXX("hash (max 2 items)",{'a': 1, 'b': 2, 'c': 3, 'd': 4}), -1, 2) \
                          == [3,"XXX{data={a=1,b=2,...(+2 items)},name=hash (max 2 items)}"]
    assert stringify_test(XXX("array",      [] )) \
                          == [2,"XXX{data=[],...(+3 items)}"]
    assert stringify_test(XXX("array",      [ 1, 2, 3 ])) \
                          == [3,"XXX{data=[1,2,3],...(+3 items)}"]
    assert stringify_test(XXX("2-level",    {'a': 1, 'arr': ['1','2','3']})) \
                          == [4,"XXX{data={a=1,...(+3 items)},...(+3 items)}"]
    assert stringify_test(XXX("x-level",    {'a': 1, 'children': [ XXX("blah", {'x': 2, 'y': 3} )]})) \
                          == [6,"XXX{data={a=1,...(+3 items)},...(+3 items)}"]
    assert stringify_test(XXX("maxdepth 3", {'a': 1, 'children': [ XXX("blah", {'x': 2, 'y': 3} )]}), 3) \
                          == [6,"XXX{data={a=1,...(+3 items)},...(+3 items)}"]
    assert stringify_test(XXX("maxdepth 2", {'a': 1, 'children': [ XXX("blah", {'x': 2, 'y': 3} )]}), 2) \
                          == [6,"XXX{data={a=1,...(+3 items)},...(+3 items)}"]
    assert stringify_test(XXX("maxdepth 1", {'a': 1, 'children': [ XXX("blah", {'x': 2, 'y': 3} )]}), 1) \
                          == [6,"XXX{data={(2 items)},...(+3 items)}"]
    assert stringify_test(XXX("all items",  {'a': 1, 'children': [ XXX("blah", {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})]}), -1) \
                          == [6,"XXX{data={a=1,...(+3 items)},...(+3 items)}"]
    assert stringify_test(XXX("max 4 items",{'a': 1, 'children': [ XXX("blah", {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})], 'b': '2', 'c': '3', 'd': '4'}), -1, 4) \
                          == [6,"XXX{data={a=1,b=2,c=3,children=[XXX{data={a=1,b=2,c=3,d=4,...(+1 items)},name=blah}],...(+1 items)},name=max 4 items}"]

    obj = XXX("blah", { 'a': 1, 'children' : [ XXX("child", { 'x' : 2, 'y': 3 }) ] })
    obj_result = list(stringify(obj, 1))
    assert obj_result == [6,"XXX{data={(2 items)},...(+3 items)}"]

    assert stringify_test(XXX("long string",{ 'short': "abcdef", 'long': "123456789abcdef"}), -1, -1, 8) \
                          == [3,"XXX{data={long=123456789abcdef,...(+3 items)},...(+3 items)}"]

    #sys.exit(0)

if __name__ == "__main__":
    test_stringify_examples()
