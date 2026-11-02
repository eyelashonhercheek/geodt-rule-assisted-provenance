"""Recompute the R21 human-review comparison using only public files and Python stdlib.

Place in support/reproducibility/ and run: python reproduce_review89.py
No returned/private workbook, Office application or specialist package is required.
"""
from pathlib import Path
import csv,json,math
P=Path(__file__).resolve().parent
S=P.parent
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
review=read(S/'Table_S1_human_review89_source_evidence.csv')
prediction_rows=read(P/'predictions_D3_16800.csv')
pred={(r['method'],r['record_key']):r for r in prediction_rows}
assert len(review)==len({r['record_key'] for r in review})==89
assert len(pred)==len(prediction_rows)==16800
methods=list(dict.fromkeys(r['method'] for r in prediction_rows))
positive=[r for r in review if r['judgment']=='支持对应']
assert len(positive)==71
assert sum(r['judgment']=='资料不足' for r in review)==18
computed=[]
for method in methods:
    for arm in ['all_reviewed_positive','automatic_accept_census','nonaccepted_stratified_random','targeted_chain_extra']:
        q=positive if arm=='all_reviewed_positive' else [r for r in positive if r['sampling_arm']==arm]
        included=edges=native=0
        for r in q:
            p=pred[method,r['record_key']]
            candidates=set(filter(None,p['candidate_ids'].split(';')))
            included+=r['baseline_id'] in candidates
            edges+=len(candidates)
            native+=p['native_accept']==r['baseline_id']
        computed.append(dict(method=method,positive_scope=arm,positive_queries=len(q),targets_included=included,
            candidate_edges=edges,inclusion_rate=included/len(q),
            target_matching_native_accepts=None if method in methods[:4] else native))
expected=read(S/'Table_S2_human_review89_method_comparison.csv')
assert len(expected)==len(computed)==48
for a,b in zip(computed,expected):
    for key,value in a.items():
        if value is None:assert b[key]=='',(key,b[key])
        elif isinstance(value,float):assert math.isclose(value,float(b[key]),rel_tol=1e-12),(key,value,b[key])
        else:assert str(value)==b[key],(key,value,b[key])
census=[r for r in review if r['sampling_arm']=='automatic_accept_census']
assert len(census)==52
assert all(r['baseline_id']==pred['full',r['record_key']]['native_accept'] for r in census)
misses=[r['task_id'] for r in positive if r['baseline_id'] not in pred['full',r['record_key']]['candidate_ids'].split(';')]
assert set(misses)=={'EX033','EX056'}
result=dict(reviewed_records=89,current_accepts_reviewed=52,accepted_targets_supported=52,
    unsupported_accepts_observed=0,unconfirmed=18,positive_targets=71,full_targets_included=69,
    withheld_reviewed_positive_tasks=misses,configuration_scope_rows_verified=48,
    independent_physical_reference_frozen=False,method_comparisons=computed)
(S/'review89_recomputed_metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='method_comparisons'},ensure_ascii=False))
