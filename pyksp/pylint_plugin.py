# Copyright (c) 2016, 2018 Claudiu Popa <pcmanticore@gmail.com>
# Copyright (c) 2018 Bryce Guinta <bryce.paul.guinta@gmail.com>
"""Astroid hooks for understanding functools library module."""
from functools import partial

import astroid  # type: ignore
from astroid import MANAGER

LRU_CACHE = "functools.lru_cache"


def register(linter):  # type: ignore
    pass


def _vrs_inference(node, context=None):  # type: ignore
    indicies = list()
    for idx, anno in enumerate(node.args.kwonlyargs_annotations):
        attr = anno.value
        if attr.attrname != 'Loc':
            continue
        module = attr.expr.inferred()[0]
        if module.name != 'pyksp.service_types':
            continue
        indicies.append(idx)
    for idx in reversed(indicies):
        del node.args.kwonlyargs[idx]
        del node.args.kwonlyargs_annotations[idx]
    return (node, )


# MANAGER.register_transform(astroid.FunctionDef, _transform_lru_cache,
#                            _looks_like_lru_cache)


def _looks_like_service_types_member(node, member):  # type: ignore
    """Check if the given Call node is a functools.partial call"""
    if not node.decorators:
        return
    if not isinstance(node.decorators.nodes[0], astroid.Attribute):
        return
    attr = node.decorators.nodes[0]
    if attr.attrname == 'vrs':
        module = attr.expr.inferred()[0]
        return module.name == 'pyksp.service_types'
    return False


_looks_like_partial = partial(_looks_like_service_types_member, member="vrs")

MANAGER.register_transform(astroid.FunctionDef,
                           astroid.inference_tip(_vrs_inference),
                           _looks_like_partial)
