"""Revision candidate engine. Rule states are not independent identity labels.

Standard-library only; source files are never modified. Report context is an
input feature, not a reference answer. Version 0.3-r4, policy locked before
any correctness experiment. Changing a policy requires a new version.
"""
from dataclasses import dataclass
from uuid import uuid5, NAMESPACE_URL
import re
import unicodedata
from copy import deepcopy

VERSION = '0.3-r4'

def append_semantic_version(registry, entity_key, version, fields):
    """Append interpretation/display fields without changing an entity key."""
    versions = registry.setdefault(entity_key, [])
    prior = [x for x in versions if x['version'] == version]
    if prior:
        if prior[0]['fields'] != fields:
            raise ValueError('semantic version already registered with different fields')
        return
    versions.append(dict(version=version, fields=deepcopy(fields)))

def clean(value):
    s = re.sub(r'\s+', '', unicodedata.normalize('NFKC', str(value or '')))
    for dash in ('‐', '‑', '–', '—', '−'):
        s = s.replace(dash, '-')
    return '' if s.upper() in {'', 'NA', 'N/A', 'NONE', 'NAN'} else s

def named_source(value):
    s = clean(value)
    if not s or s == '延河':
        return ''
    m = re.fullmatch(r'延河(\d+)号?', s)
    if m:
        return '延河' + m[1] + '号'
    return '' if re.fullmatch(r'\d+号?', s) else s

def source_number(value):
    s = clean(value)
    m = re.fullmatch(r'(?:延河)?(\d+)号?', s)
    return m[1] if m else ''

def source_compat(a, b):
    a, b = named_source(a), named_source(b)
    if not a or not b:
        return 'unavailable'
    if a == b:
        return 'equal'
    canonical = lambda s: bool(re.fullmatch(r'延河\d+号', s)) or s == '八道湾'
    return 'explicit_difference' if canonical(a) and canonical(b) else 'unresolved_alias_or_scope'

def layer_compat(a, b):
    a, b = clean(a), clean(b)
    if not a or not b:
        return 'unavailable'
    if a == b:
        return 'equal'
    x, y = re.fullmatch(r'长(\d)', a), re.fullmatch(r'长(\d)', b)
    # Only directly comparable coarse Chang labels are excluded by default.
    # Fine/coarse or T3/Chang labels need an external compatibility policy.
    return 'explicit_difference' if x and y else 'unresolved_granularity_or_system'

def code_layer_relation(code_layer, explicit_layer):
    """Literal numbering consistency only; no inferred fine/coarse hierarchy."""
    a, b = clean(code_layer), clean(explicit_layer)
    if not a or not b:
        return 'unavailable'
    if a == b:
        return 'equal'
    x, y = re.fullmatch(r'长(\d+)', a), re.fullmatch(r'长(\d+)', b)
    if x and y and len(x[1]) == len(y[1]):
        return 'literal_numbering_disagreement'
    return 'unresolved_granularity_or_system'

def lith_tokens(value):
    s = clean(value)
    # Literal shared terminology is weak support, not geological equivalence.
    return {w for w in ('粉砂岩', '砂岩', '泥岩', '灰岩', '砾岩') if w in s}

def lith_support(a, b):
    a, b = clean(a), clean(b)
    return bool(a and b and (a == b or lith_tokens(a) & lith_tokens(b)))

