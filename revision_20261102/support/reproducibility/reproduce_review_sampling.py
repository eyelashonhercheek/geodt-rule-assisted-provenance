"""Replay the registered review sampling procedure, without using human judgments for selection."""
from pathlib import Path
import csv,json,random,math
from collections import Counter
P=Path(__file__).resolve().parent
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
full={r['record_key']:r for r in read(P/'predictions_D3_16800.csv') if r['method']=='full'}
families=['hyperspectral','xrf','laser','thin_section','grain_size']
def order(k):return (families.index(k.split(':')[0]),int(k.split(':')[1]))
rng=random.Random(2026102901)
accepted=sorted([k for k,p in full.items() if p['native_accept']],key=order)
assert len(accepted)==52
draw={k:dict(record_key=k,sampling_arm='automatic_accept_census') for k in accepted}
strata={}
for family in families:
    for state in ['strong_candidate','candidate_set','unresolved']:
        pool=sorted([k for k,p in full.items() if p['family']==family and p['state']==state and not p['native_accept']],key=order)
        selected=rng.sample(pool,2)
        strata[family+':'+state]=dict(population=len(pool),selected=selected)
        for k in selected:
            assert k not in draw
            draw[k]=dict(record_key=k,sampling_arm='nonaccepted_stratified_random')
diagnostic=[['laser:3','hyperspectral:3','xrf:14'],['laser:26','laser:81'],['grain_size:52','laser:69']]
for group in diagnostic:
    for k in group:
        if k not in draw:draw[k]=dict(record_key=k,sampling_arm='targeted_chain_extra')
rows=list(draw.values());random.Random(2026102902).shuffle(rows)
for i,r in enumerate(rows,1):r['task_id']=f'EX{i:03d}'
# Compare against the retained task identifiers only after selection is finished.
review=read(P.parent/'Table_S1_human_review89_source_evidence.csv')
assert len(rows)==len(review)==89
actual={r['record_key']:(r['task_id'],r['sampling_arm']) for r in review}
assert all(actual[r['record_key']]==(r['task_id'],r['sampling_arm']) for r in rows)
secondary=random.Random(2026102903).sample(sorted(draw,key=order),math.ceil(.2*len(rows)))
secondary=set(secondary)|{k for group in diagnostic for k in group}
result=dict(status='PASS',distinct_primary_records=89,arms=dict(Counter(r['sampling_arm'] for r in rows)),
    seeds=dict(stratified_selection=2026102901,task_order=2026102902,secondary_selection=2026102903),
    secondary_preselected_records=len(secondary),secondary_review_completed=False,strata=strata,selected_tasks=rows)
(P.parent/'review_sampling_replay.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['strata','selected_tasks']}))
