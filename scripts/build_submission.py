import json,shutil,sys,os
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer
ROOT=Path(__file__).resolve().parents[1]; S=ROOT/'submission'
def build():
    S.mkdir(exist_ok=True)
    summary=json.loads((ROOT/'outputs/summary.json').read_text()); inv=json.loads((ROOT/'outputs/claim_invariance.json').read_text()); b=summary['selected_brain']; m=summary['brains'][b]
    font=Path(os.getenv('ARIAL_FONT','C:/Windows/Fonts/arial.ttf'))
    if not font.exists(): raise SystemExit('Set ARIAL_FONT to a licensed Arial TTF path for the required architecture typography.')
    pdfmetrics.registerFont(TTFont('Arial',str(font)))
    c=canvas.Canvas(str(S/'ARCHITECTURE_NOTE.pdf'),pagesize=A4)
    w,h=A4; c.setFillColorRGB(.984,.969,.941); c.rect(0,0,w,h,fill=1,stroke=0)
    def text(x,y,t,size=11,color='#1B2433'):
        c.setFillColor(color); c.setFont('Arial',size); c.drawString(x,y,t)
    text(42,h-48,'MUNIM / ARCHITECTURE NOTE',20)
    text(42,h-73,summary['source']+' | '+summary['mode']+' | '+summary['rezolve']+' Rezolve',11,'#815016')
    text(42,h-94,'HyperNova - TM-394CDC172A3',11)
    text(42,h-130,'Cheap talk is free. Commitments are priced.',15,'#2F3E9E')
    labels=['Buyer','Firewall','Brain','Gate','Voice','Verify']
    x=42; y=h-189; bw=75
    for i,label in enumerate(labels):
        c.setFillColor('#edf0f9'); c.setStrokeColor('#d3d8e7'); c.roundRect(x,y,bw,33,5,fill=1,stroke=1)
        text(x+8,y+11,label)
        if i<5: text(x+bw+2,y+11,'>',11)
        x+=85
    paragraphs=[
    ('Guarded delivery','Agent.respond is the only seller output path. Gate.check_offer validates every line, quantity, total and acceptance. Failures end safely; a failed verifier blocks sending entirely.'),
    ('Zero violations by construction - scope','Store.floor_price ceilings both constraints: markup on cost and discount from list. Duplicate lines, unknown items, invalid stock and inconsistent totals are rejected. This argument assumes the documented stand-in policy and trusted catalogue, not an unknown official contract.'),
    ('Capabilities and code','munim/rezolve.py: Rezolve.lookup serves indexed catalogue and policy records, with logged local fallback. Rezolve.verify checks price and stock claims against tool evidence before delivery.'),
    ('Live boundary','munim/adapters/rezolve_adapter.py: LiveClient.call handles documented configurable payloads, timeouts, retries and request credits. Paths remain TODO. All delivered provider evidence is MOCK.'),
    ('Strategy and replay','The ladder changes price only for changed commitments. The baseline concedes over time. The measured default is '+b+'. Both ignore pressure; replay compares saved structured moves after deleting it.'),
    ('Saved measurements',f"{summary['total_negotiations']} simulated negotiations; {m['deal_rate']*100:.1f}% deals; {m['margin_kept']*100:.2f}% margin kept; {m['policy_violations']} violations; {m['truthfulness']*100:.0f}% truthful messages; {inv['identical_pct']:.0f}% identical replay turns. Offline model tokens and cost: {m['tokens']} / INR {m['rupees_per_negotiation']}."),
    ('Evidence and limitations','Sources: outputs/summary.json and outputs/claim_invariance.json. Official public development scoring and actual Rezolve use remain unverified. The independent checker is separate from mock verification.')]
    yy=y-28
    style=ParagraphStyle('body',fontName='Arial',fontSize=11,leading=15,textColor='#1B2433')
    for title,body in paragraphs:
        text(42,yy,title,11,'#2F3E9E'); yy-=10
        p=Paragraph(escape(body),style); _,ph=p.wrap(w-84,1000); p.drawOn(c,42,yy-ph); yy-=ph+22
    assert yy>25,yy
    c.save()
    styles=ParagraphStyle('normal',fontName='Arial',fontSize=11,leading=16,spaceAfter=10)
    heading=ParagraphStyle('heading',parent=styles,fontSize=16,leading=21,textColor='#2F3E9E',spaceBefore=12)
    flow=[]
    for block in (ROOT/'docs/REZOLVE_INTEGRATION.md').read_text(encoding='utf-8').split('\n\n'):
        lines=block.splitlines()
        if lines and lines[0].startswith('#'):
            flow.append(Paragraph(escape(lines.pop(0).lstrip('# ')),heading))
        if lines:
            flow.append(Paragraph(escape('\n'.join(lines)).replace('\n','<br/>'),styles))
    SimpleDocTemplate(str(S/'Rezolve_Integration_Details.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42).build(flow)
    if not (S/'abstract.docx').exists():
        (S/'ABSTRACT_NEEDED.txt').write_text('Place the human-approved abstract (maximum 500 words) at submission/abstract.docx. No abstract was invented. Use ABSTRACT_FILL.md only with explicit SIMULATED and MOCK labels. Official results and real Rezolve usage are not yet measured.\n')
    (S/'AGENT_CARD.md').write_text('# Munim agent card\n\nSIMULATED catalogue, offline buyers, MOCK Rezolve.\n\nCan negotiate price within policy, quantity and bundle tiers. Cannot negotiate below floor, unavailable stock, hidden fees or facts outside the catalogue. Pressure is recorded and excluded from pricing. The ladder rewards changed commitments; the selected baseline is explicitly time-based. Seller speech never includes private cost/floor/buffer. This is a local demonstration, not a payment or inventory reservation system.\n')
    values=[('N',summary['total_negotiations'],'total_negotiations'),('deals closed %',round(m['deal_rate']*100,2),f'brains.{b}.deal_rate × 100'),('margin kept %',round(m['margin_kept']*100,2),f'brains.{b}.margin_kept × 100'),('policy violations',m['policy_violations'],f'brains.{b}.policy_violations'),('claims verified %',m['truthfulness']*100,f'brains.{b}.truthfulness × 100 (independent message check; not live TraceWare)'),('claim-invariant offers %',inv['identical_pct'],'claim_invariance.json: identical_pct'),('rupees per negotiation',m['rupees_per_negotiation'],f'brains.{b}.rupees_per_negotiation')]
    (S/'ABSTRACT_FILL.md').write_text('# Measured SIMULATED values only\n\nN is both brains combined; percentage metrics below are the selected '+b+' brain with '+str(m['n'])+' cases.\n\n'+ '\n'.join(f'- {name}: {value}; outputs/summary.json: {key}' if 'claim_invariance' not in key else f'- {name}: {value}; outputs/{key}' for name,value,key in values)+'\n\nOfficial public-development score: NOT MEASURED. Live Rezolve claims verified: NOT MEASURED. LLM buyer performance and live LLM rupees: NOT MEASURED. Remove any sentence claiming these until real evidence is saved. Do not describe the deadline baseline as commitment-only pricing. Approved abstract is human-supplied.\n')
    (S/'dev_set_outputs').mkdir(exist_ok=True)
    for p in (ROOT/'outputs/dev_set').glob('*'): shutil.copy2(p,S/'dev_set_outputs'/p.name)
    if (ROOT/'outputs/dev_set_official').exists(): shutil.copytree(ROOT/'outputs/dev_set_official',S/'dev_set_outputs/official',dirs_exist_ok=True)
    (S/'dev_set_outputs/README.md').write_text('# Development outputs\nSIMULATED_* files use our stand-in evaluator and buyers, not the official public development set. An official/ folder is included only after the real evaluator runs.\n')
    (S/'outputs').mkdir(exist_ok=True)
    for name in ['summary.json','claim_invariance.json']:
        shutil.copy2(ROOT/'outputs'/name,S/'outputs'/('SIMULATED_'+name if summary['source']=='SIMULATED' else name))
    for name in ['SIMULATED_submission_check.json','SIMULATED_e2e.json','SIMULATED_video_check.json','SIMULATED_final_pytest.txt']:
        if (ROOT/'outputs'/name).exists(): shutil.copy2(ROOT/'outputs'/name,S/'outputs'/name)
    records=json.loads((ROOT/f"outputs/{summary['source']}_transcripts.json").read_text())
    for persona in sorted({r['persona'] for r in records}):
        r=next(r for r in records if r['persona']==persona and r['brain']==b)
        (S/'outputs'/f"{summary['source']}_sample_{persona.replace(' ','_')}.json").write_text(json.dumps(r,indent=2))
    (S/'code').mkdir(exist_ok=True); (S/'code/REPO_LINK.txt').write_text('https://github.com/hannielvinu/Munim\n')
    (S/'README_SUBMISSION.md').write_text('# Munim | HyperNova | TM-394CDC172A3\n\nSIMULATED offline demonstration, MOCK Rezolve. Not yet an official-ready submission.\n\n- abstract.docx: human-approved abstract; ABSTRACT_NEEDED.txt documents absence.\n- demo_video.mp4 / demo_video.srt / DEMO_SCRIPT.md / NARRATION.txt: real-UI narrated demo, captions and reproducible script.\n- code/Munim_source.zip and REPO_LINK.txt: clean source and repository.\n- dev_set_outputs/: labelled stand-in development evaluation, plus official results when supplied.\n- outputs/: arena summary, invariance proof and one sample per persona.\n- Rezolve_Integration_Details.pdf: honest capability status and live checklist.\n- ARCHITECTURE_NOTE.pdf: one A4 page, Arial at least 11pt.\n- AGENT_CARD.md / ABSTRACT_FILL.md: negotiation scope and traceable numbers.\n- check.py: reproducible artifact/test checks; official readiness is separately reported.\n\nRun scripts/package_submission.sh for the upload archive. The Team Leader must supply the approved abstract, official evaluator evidence, and real Rezolve validation before portal submission. Google Drive upload is a human step; no Drive account is connected.\n')
    print('Built two PDFs, measured-value notes, sample transcripts and submission folder map.')
    paths=sorted(p.relative_to(S).as_posix() for p in S.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='MANIFEST.txt')
    (S/'MANIFEST.txt').write_text('\n'.join(paths+['MANIFEST.txt'])+'\n',encoding='utf-8')
if __name__=='__main__': build()
