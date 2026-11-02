"""Replay recovered 2026-04-16 direct-link predicate; never alter source files.

The output is a new replay, not the missing historical linkage_results.xlsx.
Recovered helper function bodies are selected by AST, without executing original
top-level report generation, file writes, or shell commands.
"""
from pathlib import Path
import ast, sys, re, json, csv, hashlib, collections, argparse
import pandas as pd
import numpy as np
import openpyxl

BASE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--pdf-root',type=Path,default=BASE.parent.parent/'原始报告')
parser.add_argument('--table-root',type=Path,default=BASE/'input_tables')
parser.add_argument('--out-dir',type=Path,default=Path.cwd()/'historical_replay_output')
parser.add_argument('--dependency-root',type=Path)
args=parser.parse_args()
if args.dependency_root:sys.path.insert(0,str(args.dependency_root))
import fitz

KEY=BASE/'function_sources'
DOWNLOAD=args.pdf_root.resolve()
TABLES=args.table_root.resolve()
OUT=args.out_dir.resolve();OUT.mkdir(parents=True,exist_ok=True)

def load_functions(message_id):
    p=next(KEY.glob('*_'+message_id+'.txt'))
    tree=ast.parse(p.read_text(encoding='utf-8'))
    funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
    exec(compile(ast.Module(body=funcs,type_ignores=[]),str(p),'exec'),globals())

dash_chars='\u2010\u2011\u2012\u2013\u2014\u2212\uFE63\uFF0D‐‑‒–—−﹣－'
dash_re=re.compile(f'[{re.escape(dash_chars)}]')
load_functions('892b0914-05e3-4b88-9530-77fda449f249')
load_functions('95934130-2474-4d0a-9e00-f18f01ccfd07')
load_functions('9f9fb86c-8889-4bab-b105-b74a4c74354c')
load_functions('09684dba-e2bd-40d2-b998-cb2890f442b6')
load_functions('88c2e109-c467-425e-a6ba-5f3f05a2f80e')

def read_table(name,key,prefix):
    p=TABLES/name
    w=openpyxl.load_workbook(p,read_only=True,data_only=True)
    rows=list(w.worksheets[0].values)
    header=next(r for r in rows if r[0]==key)
    return [dict(zip(header,r),_excel_row=i+1,_sheet=w.worksheets[0].title) for i,r in enumerate(rows) if str(r[0] or '').startswith(prefix)]

baseline=read_table('baseline_samples.xlsx','baseline_id','BS')
for b in baseline:
    for k in list(b):b[k]=to_str(b[k])
    b['section_norm_std']=norm_section(b['section_norm'])

files={
    'laser':'5.激光测试与分析.pdf',
    'thin':'岩石薄片分析-200_compressed.pdf',
    'grain':'岩石粒度分析-200.pdf',
}
source_manifest=[]
rows=[]
laser_pat=re.compile(r'报告编号：(?P<report_no>\S+).*?样品编号\s*(?P<sample_id>.*?)\s*扫描面状况.*?样品岩性\s*(?P<lith>.*?)\s*仪器型号.*?采样剖面\s*(?P<outcrop>.*?)\s*激光波段.*?采样层位\s*(?P<strat>.*?)\s*扫描距离.*?平均强度I\s*(?P<intensity>-?\d+(?:\.\d+)?)\s*平均振幅A\s*(?P<amp>-?\d+(?:\.\d+)?)',re.S)
thin_full=read_table('analysis_records_thin_section_full.xlsx','record_id','TPA')

for group,filename in files.items():
    p=DOWNLOAD/filename
    doc=fitz.open(p)
    source_manifest.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pdf_pages':len(doc)})
    seq=0
    start={'laser':13,'thin':7,'grain':6}[group]
    for page_index in range(start,len(doc)):
        page=doc[page_index]
        printed=page_index-start+1
        parsed=[]
        if group=='laser':
            parsed=[dict(m.groupdict(),block=j+1) for j,m in enumerate(laser_pat.finditer(page.get_text('text')))]
        elif group=='thin':
            d=parse_thin_page(page)
            if not d:raise ValueError(f'Thin parser failed at PDF physical {page_index+1}')
            parsed=[dict(d,block=1)]
        else:
            parsed=[dict(parse_grain_page(page),block=1)]
        for d in parsed:
            seq+=1
            raw_source=clean_text(d['outcrop'])
            source_basis='PDF正文'
            if group=='thin' and pd.isna(raw_source):
                # Same recovered fallback policy: directory source when detail is blank.
                # The full workbook preserves that directory entry. Direct-list entries
                # using this fallback are separately counted for disclosure.
                raw_source=clean_text(thin_full[seq-1]['section_raw'])
                if pd.isna(raw_source) or str(raw_source)=='NA':raw_source=clean_text(thin_full[seq-1]['outcrop_raw'])
                source_basis='目录转录表回退（现存full表）'
            if not pd.isna(raw_source) and re.fullmatch(r'\d+',str(raw_source).replace(' ','')):
                outcrop='延河';section=str(raw_source).replace(' ','')
            elif isinstance(raw_source,str) and raw_source.replace(' ','').startswith('延河'):
                _,outcrop,_,section=parse_yanhe_section_from_outcrop(raw_source.replace(' ',''))
            else:
                outcrop=normalize_outcrop(raw_source)
                section=np.nan
            rid={'laser':'LAS','thin':'THS','grain':'GRN'}[group]+f'{seq:03d}'
            curr={'laser':f'LAS{seq:03d}','thin':f'TPA{seq:03d}','grain':f'GRAIN_{seq:04d}'}[group]
            sample=to_str(normalize_sample_id(d['sample_id']))
            outcrop=to_str(outcrop);section=norm_section(to_str(section))
            ids=[b for b in baseline if b['sample_id_norm']==sample] if sample else []
            candidates=[b for b in ids if (not outcrop or b['outcrop_norm']==outcrop) and (not section or b['section_norm_std']==section)]
            rows.append({'source_group':group,'historical_record_id':rid,'current_record_id':curr,'sample_id_raw':to_str(clean_text(d['sample_id'])),'sample_id_norm':sample,'outcrop_raw':to_str(raw_source),'outcrop_norm':outcrop,'section_norm_std':section,'pdf_file':filename,'pdf_physical_page':page_index+1,'report_printed_page':printed,'page_block':d['block'],'source_field_basis':source_basis,'exact_id_candidate_count':len(ids),'after_source_candidate_count':len(candidates),'matched_baseline_id':candidates[0]['baseline_id'] if len(candidates)==1 else '', 'id_candidates':';'.join(b['baseline_id'] for b in ids),'source_candidates':';'.join(b['baseline_id'] for b in candidates),'direct_linkable':len(candidates)==1,'recovery_status':'计算可复现：历史代码重放，非当年输出文件原件'})
    print(group,'parsed records',seq)

def save(name,data):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)

accepted=[r for r in rows if r['direct_linkable']]
save('direct_links_261_replayed.csv',accepted)
save('direct_rule_trace_800.csv',rows)
counts=dict(collections.Counter(r['source_group'] for r in accepted))
summary={'total_parsed':len(rows),'direct_replay_count':len(accepted),'counts_by_type':counts,'historical_logged_counts':{'laser':94,'thin':80,'grain':87},'historical_output_binary_recovered':False,'historical_input_byte_hashes_available':False,'fallback_sources_in_accepted':sum('回退' in r['source_field_basis'] for r in accepted),'pdf_library':fitz.VersionBind,'source_manifest':source_manifest}
(OUT/'direct_replay_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
