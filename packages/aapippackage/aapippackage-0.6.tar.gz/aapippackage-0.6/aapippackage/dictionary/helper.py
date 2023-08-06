import json
from collections import Sequence
from itertools import chain, count
import itertools
try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

"""
    Given a list, possibly nested to any level, return it flattened.
"""
def flatten(lis):
    new_lis = []
    for item in lis:
        if type(item) == type([]):
            new_lis.extend(flatten(item))
        else:
            new_lis.append(item)
    return new_lis


def nested_item(depth, value):
    if depth <= 1:
        return [value]
    else:
        return [nested_item(depth - 1, value)]


def findvalueinlistdict(dictkeyname, listofrandomdict):
    for dictitem in listofrandomdict:
        try:
            return dictitem[dictkeyname]
        except:
            pass
    return None

def find_values_json(id, jsonobj):
    results = []
    def _decode_dict(a_dict):
        try:
            results.append(a_dict[id])
        except KeyError:
            pass
        return a_dict
    json.loads(json.dumps(jsonobj), object_hook=_decode_dict)  # return value ignored
    return results


def find_values(id, json_repr):
    results = []
    def _decode_dict(a_dict):
        try:
            results.append(a_dict[id])
        except KeyError:
            pass
        return a_dict
    json.loads(json_repr, object_hook=_decode_dict)  # return value ignored
    return results


def depth(seq):
    for level in count():
        if not seq:
            return level
        seq = list(chain.from_iterable(s for s in seq if isinstance(s, Sequence)))


def convertlistdicttosingelist(items):
    finallist = list()
    for item in items:
        if type(item) is list:
            for thing in item:
                if type(thing) is dict:
                    finallist.append(thing)
        elif type(item) is dict:
            finallist.append(item)
    return finallist


def convertlistdicttoordereddict(items):
    finaldict = OrderedDict()
    for item in items:
        if type(item) is list:
            for thing in item:
                if type(thing) is dict:
                    finaldict.update(thing)
        elif type(item) is dict:
            finaldict.update(item)
    return finaldict