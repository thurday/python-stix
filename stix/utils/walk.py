# Copyright (c) 2015, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

# stdlib
import itertools

# external
from cybox.common import ObjectProperties

# internal
from . import is_entity, is_entitylist, attr_name


def _is_skippable(varname, owner):
    if varname in ("_parent", "_fields") and isinstance(owner, ObjectProperties):
        return True

    if varname in ("__input_namespaces__", "__input_schemalocations__"):
        return True

    return False


def _iter_vars(obj):
    instance_vars = getattr(obj, "__dict__", {}).iteritems()
    typed_fields  = getattr(obj, "_fields", {}).iteritems()
    return itertools.chain(instance_vars, typed_fields)


def iterwalk(obj):
    def yield_and_walk(item):
        if not is_entity(item):
            return

        yield item
        for descendant in iterwalk(item):
            yield descendant

    for varname, varobj in _iter_vars(obj):
        if _is_skippable(varname, obj):
            continue

        if isinstance(varobj, (list, tuple)):
            for item in varobj:
                for descendant in yield_and_walk(item):
                    yield descendant

            continue

        for descendant in yield_and_walk(varobj):
            yield descendant


def iterpath(obj, path=None):
    def yield_and_descend(name, item):
        yield (path, attr_name(name), item)

        if item is None:
            return

        for path_info in iterpath(item, path):
            yield path_info

    if path is None:
        path = []

    path.append(obj)

    for varname, varobj in _iter_vars(obj):
        if _is_skippable(varname, obj):
            continue

        if varname == "_inner" and is_entitylist(obj):
            for item in varobj:
                for path_info in iterpath(item, path):
                    yield path_info
        elif isinstance(varobj, (list, tuple)):
            for item in varobj:
                for path_info in yield_and_descend(varname, item):
                    yield path_info

        else:
            for path_info in yield_and_descend(varname, varobj):
                yield path_info

    path.pop()

