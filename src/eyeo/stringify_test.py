import sys

from eyeo.stringify import *
from eyeo import msg

class TestObj:
    def __init__(self, name, datadict):
        self.name = name
        self.data = datadict

def stringify_test(item, maxDepth=None, maxItems=-1, maxStrlen=-1):
    msg(item.name)
    msg("  maxDepth  ", maxDepth)
    msg("  maxItems  ", maxItems)
    msg("  maxStrlen ", maxStrlen)
    msg("  result    ", stringify( item, maxDepth, maxItems, maxStrlen))

def tests():
    stringify_test(TestObj("hash",              {}))
    stringify_test(TestObj("hash",              {'a': 1}))
    stringify_test(TestObj("hash",              {'a': 1, 'b': 2}))
    stringify_test(TestObj("hash (max 2 items)",{'a': 1, 'b': 2, 'c': 3, 'd': 4}), -1, 2)
    stringify_test(TestObj("array",      [] ))
    stringify_test(TestObj("array",      [ 1, 2, 3 ]))
    stringify_test(TestObj("2-level",    {'a': 1, 'arr': ['1','2','3']}))
    stringify_test(TestObj("x-level",    {'a': 1, 'children': [ TestObj("blah", {'x': 2, 'y': 3} )]}))
    stringify_test(TestObj("maxdepth 3", {'a': 1, 'children': [ TestObj("blah", {'x': 2, 'y': 3} )]}), 3)
    stringify_test(TestObj("maxdepth 2", {'a': 1, 'children': [ TestObj("blah", {'x': 2, 'y': 3} )]}), 2)
    stringify_test(TestObj("maxdepth 1", {'a': 1, 'children': [ TestObj("blah", {'x': 2, 'y': 3} )]}), 1)
    stringify_test(TestObj("all items",  {'a': 1, 'children': [ TestObj("blah", {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})]}), -1)
    stringify_test(TestObj("max 4 items",{'a': 1, 'children': [ TestObj("blah", {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5})], 'b': '2', 'c': '3', 'd': '4'}), -1, 4)

    obj = TestObj("blah", { 'a': 1, 'children' : [ TestObj("child", { 'x' : 2, 'y': 3 }) ] })
    msg("object", stringify(obj, 1))

    stringify_test(TestObj("long string",{ 'short': "abcdef", 'long': "123456789abcdef"}), -1, -1, 8)

    sys.exit(1)

if __name__ == "__main__":
    tests()
