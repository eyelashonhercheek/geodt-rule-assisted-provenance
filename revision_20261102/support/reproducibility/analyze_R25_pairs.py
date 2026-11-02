"""Paired analysis of frozen D3 predictions. No policy, label or input edits."""
from pathlib import Path
import ast,csv,json,hashlib
from collections import Counter
from r5_engine import Engine,project,with_lineage,layer_support
from common import lith_support
P=Path(__file__).resolve().parent
def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sourcefiles=[P/'inputs_D3.json',P/'predictions_D3_16800.csv',P/'reference_429.csv',P.parent/'Table_S1_human_review89_source_evidence.csv',P/'r5_engine.py',P/'common.py']
hashes={p.name:sha(p) for p in sourcefiles}
D=json.loads((P/'inputs_D3.json').read_text(encoding='utf-8'))
queries={r['record_key']:r for r in D['analytical_records']}
baseline={r['baseline_id']:r for r in D['baseline']}
frozen={(r['method'],r['record_key']):r for r in readcsv(P/'predictions_D3_16800.csv')}
assert len(queries)==1400 and len(baseline)==100 and len(frozen)==16800
tree=ast.parse((P/'run_author_revision_v5.py').read_text(encoding='utf-8'))
fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='basic')
env=dict(project=project,with_lineage=with_lineage,layer_support=layer_support,lith_support=lith_support)
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<registered basic function>','exec'),env)
basic=env['basic'];B={k:with_lineage(project(v,baseline=True)) for k,v in baseline.items()}
engine=Engine(D['baseline']);full={}
for key,q in queries.items():
    a=engine.recover(q);b=basic(q,'strict_multifield',B)
    for method,o in [('full',a),('strict_multifield',b)]:
        reg=frozen[method,key]
        assert o['candidate_ids']==list(filter(None,reg['candidate_ids'].split(';'))),(method,key)
        if method=='full':
            assert o['final_status']==reg['state'] and (o['native_accept'] or '')==reg['native_accept'],key
    full[key]=a
def included(method,key,target):return target in frozen[method,key]['candidate_ids'].split(';')
refs=[dict(key=r['analysis_record_key'],target=r['baseline_id']) for r in readcsv(P/'reference_429.csv')]
review=readcsv(P.parent/'Table_S1_human_review89_source_evidence.csv')
positive=[dict(key=r['record_key'],target=r['baseline_id'],task=r['task_id'],evidence_class=r['evidence_class']) for r in review if r['judgment']=='支持对应']
assert len(refs)==429 and len(positive)==71 and len(review)==89
summary=[];cases=[]
for scope,rows in [('documentary429',refs),('human_reviewed_positive71',positive)]:
    count=Counter()
    for row in rows:
        k=row['key'];t=row['target'];a=included('full',k,t);b=included('strict_multifield',k,t)
        group='both' if a and b else 'full_only' if a else 'strict_only' if b else 'neither';count[group]+=1
        if group in ['full_only','strict_only']:
            o=full[k];q=queries[k];f=o['features'];z=B[t]
            if o['documentary_hold']:mechanism='documentary_hold'
            elif o['fallback_applied']:mechanism='weak_lithology_fallback'
            elif not(set(f['identifier_aliases'])&set(z['identifier_aliases'])):mechanism='contextual_candidate_entry'
            elif not layer_support(f,z):mechanism='unresolved_stratigraphic_comparability'
            else:mechanism='inspect_trace'
            cases.append(dict(scope=scope,**row,group=group,mechanism=mechanism,record_id=q['record_id'],raw_identifier=q['sample_id_raw'],baseline_identifier=baseline[t]['sample_id_raw'],baseline_source=baseline[t]['outcrop_raw'],full_candidates=o['candidate_ids'],full_state=o['final_status'],native_accept=o['native_accept'],fallback_applied=o['fallback_applied'],documentary_hold=o['documentary_hold'],trace=o['trace'],query_document=q.get('document',{})))
    summary.append(dict(scope=scope,n=len(rows),**{x:count[x] for x in ['both','full_only','strict_only','neither']}))
assert summary==[dict(scope='documentary429',n=429,both=383,full_only=13,strict_only=33,neither=0),dict(scope='human_reviewed_positive71',n=71,both=68,full_only=1,strict_only=2,neither=0)]
mechanisms=Counter(r['mechanism'] for r in cases if r['scope']=='documentary429' and r['group']=='full_only')
assert dict(mechanisms)==dict(weak_lithology_fallback=11,unresolved_stratigraphic_comparability=2)
case76=next(r for r in cases if r.get('task')=='EX076')
assert case76['mechanism']=='contextual_candidate_entry' and len(case76['full_candidates'])==7 and case76['native_accept'] is None
assert {r['task'] for r in cases if r['scope']=='human_reviewed_positive71' and r['group']=='strict_only'}=={'EX033','EX056'}
for p in sourcefiles:assert sha(p)==hashes[p.name]
result=dict(status='PASS',input_hashes=hashes,replayed_full_and_strict_queries=1400,paired_summary=summary,documentary_full_only_mechanisms=dict(mechanisms),new_reference_labels=0,expert_judgments_changed=0,engine_changed=False,input_changed=False)
(P.parent/'paired_retention_R25.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(P.parent/'paired_case_ledger_R25.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
