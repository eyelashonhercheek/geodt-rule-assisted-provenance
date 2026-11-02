"""Regenerate the Table S1 report-type companion from unchanged review judgments.

Run from any directory. Outputs default to a new review_type_summary directory;
--output-dir selects a separate destination. Source tables are read-only.
"""
from pathlib import Path
import argparse,csv,json

HERE=Path(__file__).resolve().parent
TYPES={'hyperspectral':'Hyperspectral','xrf':'XRF','laser':'Laser',
       'thin_section':'Thin-section','grain_size':'Grain-size'}

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:
        return list(csv.DictReader(stream))

def summarize(support):
    review=read(support/'Table_S1_human_review89_source_evidence.csv')
    predictions=read(support/'reproducibility/predictions_D3_16800.csv')
    full={r['record_key']:r for r in predictions if r['method']=='full'}
    assert len(full)==1400
    assert len(review)==len({r['record_key'] for r in review})==89
    result=[]
    for key,label in TYPES.items():
        rows=[r for r in review if r['record_key'].split(':',1)[0]==key]
        supported=[r for r in rows if r['judgment']=='支持对应']
        unknown=[r for r in rows if r['judgment']=='资料不足']
        census=[r for r in rows if r['sampling_arm']=='automatic_accept_census']
        positives_included=sum(r['baseline_id'] in full[r['record_key']]['candidate_ids'].split(';') for r in supported)
        native=[r for r in full.values() if r['record_key'].startswith(key+':') and r['native_accept']]
        assert len(census)==len(native)
        assert all(r['judgment']=='支持对应' and r['baseline_id']==full[r['record_key']]['native_accept'] for r in census)
        assert len(supported)+len(unknown)==len(rows)
        result.append(dict(report_type=label,reviewed_records=len(rows),supported_targets=len(supported),
            insufficient_evidence=len(unknown),accepted_link_census=len(census),accepted_targets_supported=len(census),
            supported_targets_in_final_candidates=positives_included,
            stratified_random_records=sum(r['sampling_arm']=='nonaccepted_stratified_random' for r in rows),
            diagnostic_records=sum(r['sampling_arm']=='targeted_chain_extra' for r in rows)))
    expected=[(7,3,0),(7,4,0),(13,9,3),(11,7,5),(51,48,44)]
    assert [(r['reviewed_records'],r['supported_targets'],r['accepted_link_census']) for r in result]==expected
    totals={k:sum(r[k] for r in result) for k in result[0] if k!='report_type'}
    assert totals==dict(reviewed_records=89,supported_targets=71,insufficient_evidence=18,
        accepted_link_census=52,accepted_targets_supported=52,supported_targets_in_final_candidates=69,
        stratified_random_records=30,diagnostic_records=7)
    return result,totals

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--support-dir',type=Path,default=HERE.parent)
    parser.add_argument('--output-dir',type=Path,default=Path('review_type_summary'))
    args=parser.parse_args();rows,totals=summarize(args.support_dir)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    with (args.output_dir/'Table_S1_review_by_report_type.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    report=dict(totals=totals,report_types=rows,scope='Existing single-reviewer judgments; no new review decisions',
        zero_accept_types='No accepted-link precision denominator for hyperspectral or XRF in this run')
    (args.output_dir/'review_by_report_type.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
