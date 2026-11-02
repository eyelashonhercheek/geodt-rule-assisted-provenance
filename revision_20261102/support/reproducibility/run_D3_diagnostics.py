"""Check the unchanged 0.4-r5 engine on the D3 inputs.
Read-only with respect to R19; writes only a new pre-submission review directory.
"""
from pathlib import Path
import sys,csv,json,itertools
P=Path(__file__).resolve().parent
OUT=P.parent/'diagnostics'
OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(P))
from r5_engine import Engine,Config,project,with_lineage,VERSION
from common import source_compat,layer_compat,lith_support,named_source
D=json.loads((P/'inputs_D3.json').read_text(encoding='utf-8'))
engine=Engine(D['baseline']);base=engine.b
orders=list(itertools.permutations(['source','layer','lithology']))
order_rows=[];blocking=[]
for q in D['analytical_records']:
    r=engine.recover(q);f=r['features']
    initial=set(r['trace'][0]['after'])
    def source(c):
        if f['named_source']:return {k for k in c if source_compat(f['named_source'],base[k]['named_source'])!='explicit_difference'}
        if f['source_number']:
            preferred={k for k in c if f['source_number']==base[k]['source_number']}
            return preferred or c
        return c
    def layer(c):return {k for k in c if layer_compat(f['explicit_layer'],base[k]['explicit_layer'])!='explicit_difference'}
    def lithology(c):
        if not f['lithology']:return c
        supported={k for k in c if lith_support(f['lithology'],base[k]['lithology'])}
        return supported or c
    ops=dict(source=source,layer=layer,lithology=lithology)
    for order in orders:
        c=set(initial)
        for op in order:c=ops[op](c)
        if r['documentary_hold']:c=set()
        if order==('source','layer','lithology'):assert sorted(c)==r['candidate_ids'],q['record_key']
        order_rows.append(dict(record_key=q['record_key'],order='>'.join(order),candidate_count=len(c),different_from_default=sorted(c)!=r['candidate_ids'],candidates=';'.join(sorted(c))))
    # Same early exact named-source block policy as the old R3 diagnostic:
    # no named source or empty block falls back to the complete baseline.
    subset=[b for b in D['baseline'] if base[b['baseline_id']]['named_source']==f['named_source']] if f['named_source'] else D['baseline']
    if not subset:subset=D['baseline']
    blocked=Engine(subset).recover(q)
    blocking.append(dict(record_key=q['record_key'],pool_before=len(D['baseline']),pool_after=len(subset),candidate_set_changed=blocked['candidate_ids']!=r['candidate_ids'],state_changed=blocked['final_status']!=r['final_status'],candidates_before=';'.join(r['candidate_ids']),candidates_after=';'.join(blocked['candidate_ids'])))
def save(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summaries=[]
for order in orders:
    name='>'.join(order);rows=[x for x in order_rows if x['order']==name]
    summaries.append(dict(order=name,n=len(rows),changed_queries=sum(x['different_from_default'] for x in rows),candidate_edges=sum(x['candidate_count'] for x in rows)))
save('current_0.4-r5_order_summary.csv',summaries)
save('current_0.4-r5_order_rows.csv',order_rows)
save('current_0.4-r5_blocking_rows.csv',blocking)
result=dict(engine_version=VERSION,queries=1400,default_replay_matches_current_engine=True,orders=summaries,blocking=dict(pool_checks_before=sum(x['pool_before'] for x in blocking),pool_checks_after=sum(x['pool_after'] for x in blocking),candidate_set_changed=sum(x['candidate_set_changed'] for x in blocking),state_changed=sum(x['state_changed'] for x in blocking)),scope='Candidate-filter permutations with entry and documentary hold fixed; exact named-source early blocking with empty-block fallback; development diagnostic, not independent accuracy validation. D3 inputs; original sources and R19 are not modified.')
(OUT/'current_diagnostic_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result))
