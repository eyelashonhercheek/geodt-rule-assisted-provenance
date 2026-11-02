"""Read-only audit of R25.1 wording against frozen inputs and predictions.

Writes its findings into a new self-review result JSON, never into input files.
"""
from pathlib import Path
import sys,csv,json,hashlib
from collections import Counter
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from r5_engine import Engine
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
D=json.loads((P/'inputs_D3.json').read_text(encoding='utf-8'))
Q={r['record_key']:r for r in D['analytical_records']}
E=Engine(D['baseline'])
pred=read(P/'predictions_D3_16800.csv')
full={r['record_key']:r for r in pred if r['method']=='full'}
assert len(full)==1400
states=Counter(r['state'] for r in full.values())
assert dict(states)==dict(rule_supported_link=52,strong_candidate=396,candidate_set=374,unresolved=578)
retained=sum(bool(r['candidate_ids']) for r in full.values())
edges=sum(len([x for x in r['candidate_ids'].split(';') if x]) for r in full.values())
accepts=sum(bool(r['native_accept']) for r in full.values())
assert (retained,edges,accepts)==(822,7031,52)
review={r['task_id']:r for r in read(P.parent/'Table_S1_human_review89_source_evidence.csv')}
illustrated=[]
for t in ['EX048','EX049','EX021','EX028','EX084']:
    r=review[t];f=full[r['record_key']]
    assert f['candidate_ids']==r['baseline_id'] and f['state']=='strong_candidate' and not f['native_accept']
    assert r['sampling_arm']=='targeted_chain_extra' and r['judgment']=='支持对应'
    illustrated.append(dict(task_id=t,record_key=r['record_key'],target=r['baseline_id'],state=f['state'],
        pdf_physical_page=r['detail_pdf_physical_page'],directory_referenced_report_page=r['directory_points_to_printed_page'],
        within_page_block=r['within_page_block']))
blocking=read(P.parent/'diagnostics/current_0.4-r5_blocking_rows.csv')
changed=[r for r in blocking if r['candidate_set_changed']=='True']
assert len(changed)==37
entry=Counter();families=Counter()
for r in changed:
    q=Q[r['record_key']];before=E.recover(q);features=before['features']
    assert features['named_source']
    subset=[b for b in D['baseline'] if E.b[b['baseline_id']]['named_source']==features['named_source']]
    after=Engine(subset).recover(q)
    assert before['candidate_ids']==[] and before['final_status']=='unresolved'
    assert after['candidate_ids'] and after['final_status']=='candidate_set' and after['native_accept'] is None
    assert ';'.join(after['candidate_ids'])==r['candidates_after']
    assert before['trace'][0]['operator']=='candidate_entry_identifier'
    entry[after['trace'][0]['operator']]+=1;families[q['family']]+=1
assert dict(entry)==dict(candidate_entry_source_and_layer=35,candidate_entry_source=2)
assert dict(families)==dict(laser=14,thin_section=11,grain_size=12)
assert Q['laser:3']['sample_id_raw']=='长82-1'
assert Q['laser:3']['document']['detail_id']=='长 82-1'
assert D['baseline'][0]['sample_id_raw']=='长 82-1'
result=dict(status='PASS',frozen_queries=1400,states=dict(states),retained=retained,candidate_edges=edges,native_accepts=accepts,
    retrieval_coverage=retained/1400,acceptance_coverage=accepts/1400,
    figure3_cases=illustrated,blocking_changed_queries=37,blocking_changed_query_named_sources=37,
    blocking_entry_after=dict(entry),blocking_changed_families=dict(families),new_native_accepts_under_blocking=0,
    stored_string_example=dict(record='LAS002',stored=Q['laser:3']['sample_id_raw'],detail=Q['laser:3']['document']['detail_id'],baseline=D['baseline'][0]['sample_id_raw']),
    expert_judgments_changed=0,recovery_engine_changed=False)
(P.parent/'self_review_R25_1_results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
