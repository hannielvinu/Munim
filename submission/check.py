import json,subprocess,sys,re,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'scripts'))
from pypdf import PdfReader
from media import probe
def main():
    checks=[]; ready=[]
    def check(name,ok): checks.append({'check':name,'pass':bool(ok)}); print(('GREEN' if ok else 'RED')+' '+name)
    test=subprocess.run([sys.executable,'-m','pytest','-q'],cwd=ROOT,capture_output=True,text=True)
    (ROOT/'outputs/SIMULATED_final_pytest.txt').write_text(test.stdout+test.stderr)
    print(test.stdout.strip()); check('Python tests',test.returncode==0)
    summary=json.loads((ROOT/'outputs/summary.json').read_text())
    check('Zero policy violations',all(m['policy_violations']==0 for m in summary['brains'].values()))
    check('Independent truthfulness 100%',all(m['truthfulness']==1 for m in summary['brains'].values()))
    check('Claim invariance 100%',json.loads((ROOT/'outputs/claim_invariance.json').read_text())['identical_pct']==100)
    paths=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
    leaks=[]
    patterns=[re.compile(r'sk-[A-Za-z0-9]{24,}'),re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
    for name in paths:
        p=ROOT/name
        if p.name.startswith('.env') and p.name!='.env.example': leaks.append(name)
        if p.is_file() and p.suffix in ('.py','.json','.yaml','.md','.txt','.ts','.tsx','.sh'):
            content=p.read_text(encoding='utf-8-sig',errors='replace')
            if any(pattern.search(content) for pattern in patterns): leaks.append(name)
    check('Tracked source secret-pattern scan',not leaks)
    pdf=PdfReader(ROOT/'submission/ARCHITECTURE_NOTE.pdf')
    check('Architecture exactly one A4 page',len(pdf.pages)==1 and abs(float(pdf.pages[0].mediabox.width)-595.276)<1 and abs(float(pdf.pages[0].mediabox.height)-841.89)<1)
    import pymupdf
    doc=pymupdf.open(ROOT/'submission/ARCHITECTURE_NOTE.pdf')
    spans=[s for p in doc for b in p.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]
    check('Architecture Arial, minimum 11pt',all('Arial' in s['font'] and s['size']>=10.99 for s in spans))
    video=probe(ROOT/'submission/demo_video.mp4'); streams=video['streams']
    check('Video <=180 seconds, H264/AAC, 1080p, <100MB',float(video['format']['duration'])<=180 and any(s.get('codec_name')=='h264' and s.get('width')==1920 and s.get('height')==1080 for s in streams) and any(s.get('codec_name')=='aac' for s in streams) and (ROOT/'submission/demo_video.mp4').stat().st_size<100_000_000)
    required=['README_SUBMISSION.md','demo_video.mp4','demo_video.srt','DEMO_SCRIPT.md','NARRATION.txt','code/Munim_source.zip','code/REPO_LINK.txt','dev_set_outputs/SIMULATED_results.json','Rezolve_Integration_Details.pdf','ARCHITECTURE_NOTE.pdf','AGENT_CARD.md','ABSTRACT_FILL.md','outputs/SIMULATED_summary.json','check.py']
    check('Offline package files present',all((ROOT/'submission'/p).is_file() for p in required))
    check('Abstract or explicit missing-abstract note',(ROOT/'submission/abstract.docx').exists() or (ROOT/'submission/ABSTRACT_NEEDED.txt').exists())
    with zipfile.ZipFile(ROOT/'submission/code/Munim_source.zip') as z:
        check('Clean source ZIP',not any('/node_modules/' in n or '/__pycache__/' in n or n.endswith('/.env') or n=='.env' for n in z.namelist()))
    e=json.loads((ROOT/'outputs/SIMULATED_e2e.json').read_text())
    check('Browser persona and responsive checks',len(e['personas'])==6 and not e['console_errors'] and not any(p['overflow'] for p in e['pages']))
    lighthouse=ROOT/'outputs/SIMULATED_lighthouse.json'
    if lighthouse.exists(): check('Lighthouse home accessibility >=95',json.loads(lighthouse.read_text(encoding='utf-8'))['categories']['accessibility']['score']>=.95)
    ready=[{'check':'Approved abstract','pass':(ROOT/'submission/abstract.docx').exists()},{'check':'Official evaluation','pass':(ROOT/'outputs/dev_set_official/OFFICIAL_evaluator_stdout.txt').exists()},{'check':'Live Rezolve evidence','pass':summary['rezolve']=='LIVE'}]
    print('\nOfficial submission readiness (separate from offline package):')
    for r in ready: print(('GREEN' if r['pass'] else 'RED')+' '+r['check'])
    result={'source':summary['source'],'offline_package_pass':all(c['pass'] for c in checks),'checks':checks,'official_ready':all(c['pass'] for c in ready),'official_requirements':ready,'secret_scan_scope':'Tracked text files and known credential patterns; not a guarantee against every possible secret'}
    (ROOT/'outputs/SIMULATED_submission_check.json').write_text(json.dumps(result,indent=2))
    return 0 if result['offline_package_pass'] else 1
if __name__=='__main__': sys.exit(main())
