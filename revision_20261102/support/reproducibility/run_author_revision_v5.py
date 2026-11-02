"""Replay unchanged R5 on D2/D3; expose retrieval, filtering and hold separately.
Run from this directory with the bundled or any standard-library Python.
The 429 relations remain a partial documentary reference, not independent truth.
"""
from pathlib import Path
import sys,json,csv,hashlib
from collections import Counter
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
from r5_engine import Config,Engine,project,with_lineage,layer_support
from common import lith_support

def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def writecsv(p,rows):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
refs=readcsv(P/'reference_429.csv'); target={r['analysis_record_key']:r['baseline_id'] for r in refs}
assert len(refs)==len(target)==429
configs={'full':Config(),'no_identifier_evidence':Config(identifier=False),'no_alias':Config(alias=False),'no_source':Config(source=False),'no_stratigraphy':Config(stratigraphy=False),'no_lithology':Config(lithology=False),'no_fallback':Config(fallback=False),'no_conflict_gate':Config(conflict_gate=False)}
methods=['raw_id','format_id','parsed_alias_id','strict_multifield']+list(configs)

def basic(q,name,base):
    f=with_lineage(project(q))
    if name=='raw_id':c={k for k,z in base.items() if f['raw_identifier'] and f['raw_identifier']==z['raw_identifier']}
    elif name=='format_id':c={k for k,z in base.items() if f['normalized_identifier'] and f['normalized_identifier']==z['normalized_identifier']}
    else:c={k for k,z in base.items() if set(f['identifier_aliases'])&set(z['identifier_aliases'])}
    if name=='strict_multifield' and not f['normalized_identifier']:c=set(base)
    stages={'entry':set(c)}
    if name=='strict_multifield':
        c={k for k in c if (not f['named_source'] or f['named_source']==base[k]['named_source']) and (f['named_source'] or not f['source_number'] or f['source_number']==base[k]['source_number'])}
        stages['after_source']=set(c)
        c={k for k in c if (not f['explicit_layer'] and not f['coded_layer'] or layer_support(f,base[k]))}
        stages['after_layer']=set(c)
        c={k for k in c if not f['lithology'] or lith_support(f['lithology'],base[k]['lithology'])}
    stages.setdefault('after_source',set(c));stages.setdefault('after_layer',set(c));stages['prehold']=set(c)
    return dict(candidate_ids=sorted(c),final_status='baseline_output',native_accept=None,documentary_hold=False,archive=[],review_reasons=[],features={'flags':[]},trace=[],stages=stages)

all_runs={};summaries=[];stage_summary=[]
for scenario,filename in [('D2','inputs_D2.json'),('D3','inputs_D3.json')]:
    D=json.loads((P/filename).read_text(encoding='utf-8'))
    assert len(D['baseline'])==100 and len(D['analytical_records'])==1400
    base={r['baseline_id']:with_lineage(project(r,baseline=True)) for r in D['baseline']}
    engines={name:Engine(D['baseline'],cfg) for name,cfg in configs.items()}
    results={}
    for q in D['analytical_records']:
        for name in methods:
            if name in engines:
                out=engines[name].recover(q)
                st={'entry':set(out['trace'][0]['after'])}
                for event in out['trace']:
                    if event['operator']=='source':st['after_source']=set(event['after'])
                    if event['operator']=='explicit_comparable_layer':st['after_layer']=set(event['after'])
                    if event['operator']=='documentary_hold':st['prehold']=set(event['before'])
                st.setdefault('after_source',set(st['entry']));st.setdefault('after_layer',set(st['after_source']));st.setdefault('prehold',set(out['candidate_ids']))
                out['stages']=st
            else:out=basic(q,name,base)
            results[name,q['record_key']]=out
    all_runs[scenario]=results
    for name in methods:
        rr=[results[name,r['analysis_record_key']] for r in refs]
        allrows=[results[name,q['record_key']] for q in D['analytical_records']]
        summaries.append(dict(scenario=scenario,input_version=D['input_version'],method=name,reference_n=429,targets_included=sum(r['baseline_id'] in out['candidate_ids'] for r,out in zip(refs,rr)),reference_candidate_edges=sum(len(out['candidate_ids']) for out in rr),matching_native_accepts=sum(out['native_accept']==r['baseline_id'] for r,out in zip(refs,rr)),all_queries=1400,all_candidate_edges=sum(len(out['candidate_ids']) for out in allrows),all_retained=sum(bool(out['candidate_ids']) for out in allrows),all_native_accepts=sum(bool(out['native_accept']) for out in allrows)))
        for scope,kk in [('all1400',[q['record_key'] for q in D['analytical_records']]),('documentary429',[r['analysis_record_key'] for r in refs])]:
            outs=[results[name,k] for k in kk]
            metrics={'scenario':scenario,'method':name,'scope':scope,'n_queries':len(kk),'independent_reference':False,'automatic_accept_policy':'native_R5' if name in engines else 'not_defined_for_baseline'}
            for st in ['entry','after_source','after_layer','prehold']:
                metrics[st+'_candidate_edges']=sum(len(o['stages'][st]) for o in outs)
                metrics[st+'_target_inclusions']=sum(target[k] in o['stages'][st] for k,o in zip(kk,outs)) if scope=='documentary429' else ''
            metrics.update(final_candidate_edges=sum(len(o['candidate_ids']) for o in outs),final_retained=sum(bool(o['candidate_ids']) for o in outs),final_target_inclusions=sum(target[k] in o['candidate_ids'] for k,o in zip(kk,outs)) if scope=='documentary429' else '',documentary_hold_queries=sum(o['documentary_hold'] for o in outs),targets_present_before_hold_then_removed=sum(target[k] in o['stages']['prehold'] and target[k] not in o['candidate_ids'] for k,o in zip(kk,outs)) if scope=='documentary429' else '',native_accepts=sum(bool(o['native_accept']) for o in outs) if name in engines else '',matching_native_accepts=sum(o['native_accept']==target[k] for k,o in zip(kk,outs)) if scope=='documentary429' and name in engines else '')
            stage_summary.append(metrics)

# Establish exact historical replay before attributing anything to the correction.
history=readcsv(P/'historical_predictions_D2.csv');assert len(history)==16800
for r in history:
    out=all_runs['D2'][r['method'],r['record_key']]
    assert out['candidate_ids']==list(filter(None,r['candidate_ids'].split(';'))),(r['method'],r['record_key'],'candidate')
    assert out['final_status']==r['state'] and (out['native_accept'] or '')==r['native_accept'],(r['method'],r['record_key'],'status')

changes=[];predictions=[];full_changes=[]
for name in methods:
    for q in D['analytical_records']:
        key=q['record_key'];a=all_runs['D2'][name,key];b=all_runs['D3'][name,key]
        predictions.append(dict(method=name,record_key=key,record_id=q['record_id'],family=q['family'],candidate_ids=';'.join(b['candidate_ids']),state=b['final_status'],native_accept=b['native_accept'] or '',documentary_hold=b['documentary_hold']))
        if (a['candidate_ids'],a['final_status'],a['native_accept'])!=(b['candidate_ids'],b['final_status'],b['native_accept']):
            row=dict(method=name,record_key=key,record_id=q['record_id'],sample_id_raw=q['sample_id_raw'],before_candidates=';'.join(a['candidate_ids']),after_candidates=';'.join(b['candidate_ids']),before_state=a['final_status'],after_state=b['final_status'],before_native=a['native_accept'] or '',after_native=b['native_accept'] or '',before_review=';'.join(a['review_reasons']),after_review=';'.join(b['review_reasons']))
            changes.append(row)
            if name=='full':full_changes.append(row)
writecsv(P/'methods_D2_D3_comparison.csv',summaries)
writecsv(P/'stage_summary_D2_D3.csv',stage_summary)
writecsv(P/'predictions_D3_16800.csv',predictions)
writecsv(P/'all_changed_outputs_D3.csv',changes)
writecsv(P/'full_changed_outputs_D3.csv',full_changes)
held=[]
for r in refs:
    out=all_runs['D3']['full',r['analysis_record_key']]
    if r['baseline_id'] not in out['candidate_ids']:
        held.append({**r,'full_hold':out['documentary_hold'],'full_state':out['final_status'],'full_candidate_ids':';'.join(out['candidate_ids']),'reason_flags':';'.join(out['features']['flags'])})
writecsv(P/'withheld_targets_D3.csv',held)
full={sc:dict(Counter(r['final_status'] for (m,k),r in all_runs[sc].items() if m=='full')) for sc in all_runs}
fullsum={r['scenario']:r for r in summaries if r['method']=='full'}
result=dict(status='PASS',historical_prediction_rows_verified=16800,D3_prediction_rows=16800,engine_version='0.4-r5 unchanged',field_correction='BS060/61 explicit layer 长6→长7',full_summary=fullsum,full_states=full,full_changed_queries=len(full_changes),all_method_changed_rows=len(changes),withheld_targets_D3=len(held),withheld_document_holds_D3=sum(r['full_hold'] for r in held),independent_accuracy_estimated=False,new_reference_links=0,reference_frozen=False)
(P/'verification_D3.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
