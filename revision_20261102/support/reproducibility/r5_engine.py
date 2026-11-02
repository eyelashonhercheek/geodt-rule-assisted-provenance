"""R5 evidence-lineage implementation; candidates never become truth labels.

0.4-r5 was designed after R3/R4 controls were exposed. All replay is development.
"""
from dataclasses import dataclass
import re
from copy import deepcopy
from common import clean, named_source, source_number, source_compat, layer_compat, code_layer_relation, lith_support

VERSION='0.4-r5'
@dataclass(frozen=True)
class Config:
    identifier: bool=True
    alias: bool=True
    source: bool=True
    stratigraphy: bool=True
    lithology: bool=True
    fallback: bool=True
    conflict_gate: bool=True

def identifier_parts(value,family,alias=True):
    code=clean(value);aliases=[code] if code else [];derived='';rule='';prefix=''
    m=re.fullmatch(r'(?:([0-9]+)-)?(长([0-9]+)-[0-9]+(?:-[0-9]+)*)',code)
    if m:
        derived='长'+m[3];rule='USER_CHANG_ID_LAYER_20261021';prefix=m[1] or ''
        if m[1] and alias:aliases.append(m[2])
    m=re.fullmatch(r'([0-9]+)-C([0-9]+)-([0-9]+(?:-[0-9]+)*)',code)
    if m and family=='hyperspectral' and alias:
        aliases.append('长'+m[2]+'-'+m[3]);derived='长'+m[2];prefix=m[1];rule='SCOPED_C_TO_CHANG_HYPOTHESIS'
    return dict(normalized=code,aliases=list(dict.fromkeys(aliases)),coded_layer=derived,coded_layer_rule=rule,prefix_number=prefix)

def observed_explicit_layer(row):
    d=row.get('document',{})
    return clean(d.get('detail_layer')) or clean(row.get('strat_unit_norm')) or clean(row.get('strat_unit_raw'))

def project(row,cfg=Config(),baseline=False):
    """Only this projected object is made available to matchers.

    Removing identifier removes every ID-derived channel; removing stratigraphy
    removes both explicit and coded layers, but does not rewrite whole IDs.
    """
    d=row.get('document',{})
    raw=str(row.get('sample_id_raw') or '') if cfg.identifier else ''
    norm=(clean(row.get('sample_id_norm')) or clean(row.get('sample_id_raw'))) if cfg.identifier else ''
    parts=identifier_parts(norm,row.get('family','baseline'),cfg.alias) if cfg.identifier else identifier_parts('','')
    explicit=observed_explicit_layer(row) if cfg.stratigraphy else ''
    coded=parts['coded_layer'] if cfg.stratigraphy and cfg.identifier else ''
    if cfg.identifier and cfg.alias and cfg.stratigraphy and re.fullmatch(r'[0-9]+',norm) and re.fullmatch(r'长[0-9]+',explicit):
        parts['aliases'].append(explicit+'-'+norm)
    source_fields=[]
    if cfg.source:
        vals=[row.get('outcrop_raw')] if baseline else [d.get('detail_source'),d.get('catalogue_source')]
        source_fields=list(dict.fromkeys(clean(x) for x in vals if clean(x)))
    named=list(dict.fromkeys(named_source(x) for x in source_fields if named_source(x)))
    number=next((source_number(x) for x in source_fields if source_number(x)),'')
    if not number and cfg.source and cfg.identifier:number=parts['prefix_number']
    flags=[];review=[]
    if cfg.source and d.get('source_disagreement'):flags.append('document_source_disagreement')
    if cfg.identifier and d.get('identifier_disagreement'):flags.append('document_identifier_disagreement')
    for i,a in enumerate(named):
        for b in named[i+1:]:
            relation=source_compat(a,b)
            if relation=='explicit_difference':flags.append('document_comparable_source_disagreement')
            elif relation!='equal':review.append('source_naming_scope_unresolved')
    if cfg.source and cfg.identifier and parts['prefix_number'] and source_fields:
        observed_numbers={source_number(x) for x in source_fields if source_number(x)}
        if observed_numbers and parts['prefix_number'] not in observed_numbers:flags.append('prefix_observed_source_disagreement')
    if cfg.stratigraphy and explicit and coded:
        relation=code_layer_relation(coded,explicit)
        if relation=='literal_numbering_disagreement':flags.append('coded_explicit_layer_disagreement')
        elif relation!='equal':review.append('coded_explicit_layer_granularity_unresolved')
    return dict(raw_identifier=raw,normalized_identifier=norm,identifier_aliases=parts['aliases'],
                explicit_layer=explicit,coded_layer=coded,
                layer_evidence=[dict(value=explicit,origin='explicit_report_field',depends_on=['stratigraphy'])] if explicit else [],
                coded_layer_rule=parts['coded_layer_rule'] if coded else '',
                source_fields=source_fields,named_source=named[0] if named else '',source_number=number,
                source_number_origin='explicit_source_field' if any(source_number(x) for x in source_fields) else 'identifier_prefix' if number else '',
                lithology=clean(row.get('lithology_norm') or row.get('lithology_raw')) if cfg.lithology else '',
                flags=sorted(set(flags)),review=sorted(set(review)),inferred_locator=bool(d.get('inferred_locator')))

def with_lineage(features):
    f=deepcopy(features)
    if f['coded_layer']:f['layer_evidence'].append(dict(value=f['coded_layer'],origin=f['coded_layer_rule'],depends_on=['identifier','stratigraphy'],independent_of_identifier=False))
    return f

def layer_support(a,b):
    va={a['explicit_layer'],a['coded_layer']}-{''};vb={b['explicit_layer'],b['coded_layer']}-{''}
    return bool(va & vb)

def label_hypothesis(features):
    """A display grouping only, never a physical entity or reference label."""
    return dict(source_label=features['named_source'] or (('numeric:'+features['source_number']) if features['source_number'] else 'UNKNOWN_SOURCE'),
                sample_label=features['identifier_aliases'][-1] if features['identifier_aliases'] else 'UNKNOWN_SAMPLE',
                physical_identity_confirmed=False)

class Engine:
    def __init__(self,baseline,config=Config()):
        self.cfg=config
        self.b={r['baseline_id']:with_lineage(project(r,config,True)) for r in baseline}
        if len(self.b)!=len(baseline):raise ValueError('duplicate baseline technical keys')
    def recover(self,row):
        cfg=self.cfg;f=with_lineage(project(row,cfg));b=self.b;trace=[];archive=set();review=list(f['review'])
        def log(op,before,after):trace.append(dict(operator=op,before=sorted(before),after=sorted(after)))
        ids={k for k,z in b.items() if set(f['identifier_aliases']) & set(z['identifier_aliases'])} if cfg.identifier else set()
        src={k for k,z in b.items() if f['named_source'] and f['named_source']==z['named_source']} if cfg.source else set()
        if cfg.source and not f['named_source'] and f['source_number']:
            src={k for k,z in b.items() if f['source_number']==z['source_number']}
        layers={k for k,z in b.items() if layer_support(f,z)} if cfg.stratigraphy else set()
        fallback=False
        if ids:c=set(ids);entry='identifier'
        elif src and layers:
            c=src&layers;entry='source_and_layer'
            if not c and cfg.fallback:c=set(src);fallback=True
        elif src:c=set(src);entry='source'
        else:c=set(layers);entry='layer' if layers else 'none'
        log('candidate_entry_'+entry,[],c)
        if cfg.source:
            previous=set(c)
            rejected={k for k in c if f['named_source'] and source_compat(f['named_source'],b[k]['named_source'])=='explicit_difference'}
            if cfg.conflict_gate:c-=rejected;archive|=rejected
            if not f['named_source'] and f['source_number'] and c:
                preferred={k for k in c if f['source_number']==b[k]['source_number']}
                if preferred:c=preferred
                else:review.append('numeric_source_not_supported')
            log('source',previous,c)
        if cfg.stratigraphy:
            previous=set(c)
            # Hard exclusions compare explicit report fields, not recoded copies.
            rejected={k for k in c if layer_compat(f['explicit_layer'],b[k]['explicit_layer'])=='explicit_difference'}
            if cfg.conflict_gate:c-=rejected;archive|=rejected
            log('explicit_comparable_layer',previous,c)
            # Layer support is logged with dependency; never counted as a new ID-independent vote.
            supported_layers={k for k in c if layer_support(f,b[k])}
            log('layer_support_observation',c,c)
            trace[-1].update(applied_as_filter=False,supported_candidate_ids=sorted(supported_layers),identifier_derived_support_is_independent=False)
        preweak=len(c)
        if cfg.lithology and f['lithology'] and c:
            previous=set(c);supported={k for k in c if lith_support(f['lithology'],b[k]['lithology'])}
            if supported:c=supported
            elif cfg.fallback:fallback=True
            else:c=set()
            log('weak_lithology',previous,c)
        hold=cfg.conflict_gate and bool(f['flags'])
        if hold:archive|=c;log('documentary_hold',c,[]);c=set()
        if any(b[k]['flags'] for k in c):review.append('candidate_baseline_internal_disagreement')
        # Explicit fine/coarse unresolved relations remain unknown despite matching ID-derived layers.
        uncertain_layer=cfg.stratigraphy and any(layer_compat(f['explicit_layer'],b[k]['explicit_layer'])=='unresolved_granularity_or_system' for k in c)
        if uncertain_layer:review.append('cross_record_explicit_layer_granularity_unresolved')
        exact=cfg.identifier and bool(c) and all(f['normalized_identifier']==b[k]['normalized_identifier'] for k in c)
        exactsource=cfg.source and bool(f['named_source']) and bool(c) and all(f['named_source']==b[k]['named_source'] for k in c)
        native=bool(len(c)==1 and exact and exactsource and preweak==1 and not f['inferred_locator'] and not review and not f['flags'])
        status='unresolved' if not c else 'candidate_set' if len(c)>1 else 'rule_supported_link' if native else 'strong_candidate'
        return dict(record_key=row['record_key'],version=VERSION,features=f,candidate_ids=sorted(c),candidate_count=len(c),
                    final_status=status,native_accept=next(iter(c)) if native else None,documentary_hold=hold,
                    fallback_applied=fallback,review_reasons=sorted(set(review)),archive=sorted(archive),trace=trace,
                    independent_physical_reference='unknown',label_hypothesis=label_hypothesis(f))
