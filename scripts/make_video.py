import asyncio,json,math,time,wave,hashlib,sys
from pathlib import Path
import numpy as np
import edge_tts
from playwright.sync_api import sync_playwright
from media import ROOT,ff,probe,FFMPEG
S=ROOT/'submission'; A=ROOT/'outputs/audio'; V=ROOT/'outputs/raw_video'
for p in (S,A,V): p.mkdir(parents=True,exist_ok=True)
summary=json.loads((ROOT/'outputs/summary.json').read_text()); m=summary['brains'][summary['selected_brain']]
inv=json.loads((ROOT/'outputs/claim_invariance.json').read_text())
def words(n):
    ones=['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen']
    tens=['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']
    n=int(n)
    if n<20:return ones[n]
    if n<100:return tens[n//10]+(' '+ones[n%10] if n%10 else '')
    return ones[n//100]+' hundred'+(' and '+words(n%100) if n%100 else '')
sections=[
(0,25,'An illustrative scene',[
'Imagine a small shop, and a buyer that never gets tired of bargaining.',
'It claims another shop is cheaper, invents a tiny budget, and asks for an exception.',
'This is an illustrative scene, not a customer testimonial.',
'Meet Munim, a digital khata that helps a shopkeeper hold fair boundaries.',
'Everything you will see uses simulated shop data and offline buyers.']),
(25,50,'Cheap talk is free. Commitments are priced.',[
'Our idea is simple. Cheap talk is free. Commitments are priced.',
'The firewall separates facts, commitments, and pressure before pricing begins.',
'The ladder rewards a larger basket, rather than a louder argument.',
'Every offer passes the policy gate, a controlled voice, and a claim check.',
'The seller never shares its private costs or policy floor.']),
(50,85,'Live manipulator • commitment ladder',[
'Here is the actual running application, using the commitment ladder.',
'The buyer starts with an item and quantity, and Munim quotes the catalogue price.',
'Now comes a fake competitor quote, followed by a fake budget.',
'The firewall marks both as pressure. The offer stays exactly the same.',
'A one rupee counter fails the policy check. It cannot become a seller offer.',
'When the buyer commits to more units, a quantity tier becomes available.',
'That is a real change in the basket, and a reason for a different price.']),
(85,115,'Replay • delete the pressure',[
'Now remove the pressure and replay the saved conversations.',
'On the left is the original buyer message. On the right, only the clean commitment remains.',
'We compare the actual structured offers, turn by turn, for both pricing brains.',
'In this saved simulated run, '+words(inv['identical_pct'])+' percent are identical.',
'This is evidence about these transcripts, not a promise about every possible message.',
'The comparison is reproducible from the repository.']),
(115,135,'Commerce verification • MOCK',[
'The evidence panel shows price lookups, stock checks, and policy checks.',
'Today, verification and knowledge retrieval run locally in mock mode.',
'We do not claim that these are real Rezolve calls.',
'The live adapter requires documented endpoints and credentials, and blocks messages when verification fails.']),
(135,160,'Measured results • SIMULATED',[
'The arena ran '+words(summary['total_negotiations'])+' negotiations, split between the ladder and baseline.',
'The measured winner was the deadline baseline, with '+words(round(m['deal_rate']*100))+' percent of deals closed.',
'It retained about '+words(round(m['margin_kept']*100))+' percent of list gross margin.',
'Both strategies recorded zero policy violations and fully truthful checked messages.',
'Offline model tokens and model cost were zero. These are simulated results, not official challenge scores.']),
(160,174,'HyperNova • TM-394CDC172A3',[
'Munim makes the reasoning visible, and the evidence replayable.',
'Next, connect the official kit and validate the real Rezolve integration.',
'We are team HyperNova.',
'Fair prices. Firm boundaries.'])
]
def stamp(seconds):
    ms=round(seconds*1000); return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
async def speech():
    for si,(_,_,_,sentences) in enumerate(sections):
        for j,sentence in enumerate(sentences):
            path=A/f'{si}_{j}_{hashlib.sha1(sentence.encode()).hexdigest()[:8]}.mp3'
            if not path.exists(): await asyncio.wait_for(edge_tts.Communicate(sentence,'en-IN-NeerjaNeural',rate='-5%').save(str(path)),timeout=40)
            yield si,j,sentence,path
def audio():
    files={}
    async def collect():
        async for si,j,sentence,path in speech(): files[(si,j)]=path
    try: asyncio.run(collect()); voice='en-IN-NeerjaNeural'
    except Exception as e:
        voice='NONE — captioned silent fallback'; (S/'NARRATION_FALLBACK.txt').write_text('Neural TTS unavailable: '+type(e).__name__+'. Follow scripts/make_voice_local.md.')
    cues=[]; parts=[]; rate=48000
    for si,(start,end,title,sentences) in enumerate(sections):
        lengths=[]; raw=[]
        if voice.startswith('NONE'):
            durations=[(end-start)/len(sentences)]*len(sentences)
            data=np.zeros(round((end-start)*rate),dtype=np.float32)
        else:
            for j,sentence in enumerate(sentences):
                wav=A/f'{si}_{j}.wav'
                ff(['-i',files[(si,j)],'-ar',rate,'-ac',1,'-c:a','pcm_s16le',wav])
                with wave.open(str(wav),'rb') as w: samples=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
                raw.extend([samples,np.zeros(round(.3*rate),dtype=np.float32)]); lengths.append(len(samples)/rate+.3)
            joined=np.concatenate(raw); path=A/f'section{si}_raw.wav'
            writewav(path,joined,rate)
            # Fit the narration to its planned section without inserting long empty gaps.
            tempo=(len(joined)/rate)/(end-start)
            ff(['-i',path,'-af',f'atempo={tempo},loudnorm=I=-16:TP=-1.5:LRA=11','-ar',rate,'-ac',1,'-c:a','pcm_s16le',A/f'section{si}.wav'])
            with wave.open(str(A/f'section{si}.wav'),'rb') as w: data=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
            target=round((end-start)*rate); data=np.pad(data,(0,max(0,target-len(data))))[:target]
            durations=[x/tempo for x in lengths]
        cursor=start
        for sentence,duration in zip(sentences,durations):
            # Split long sentence captions into readable short lines/cues.
            tokens=sentence.split(); chunks=[' '.join(tokens[k:k+12]) for k in range(0,len(tokens),12)]
            for chunk in chunks:
                d=duration/len(chunks); cues.append((cursor,min(end,cursor+d),chunk)); cursor+=d
        parts.append(data)
    full=np.concatenate(parts)
    if not voice.startswith('NONE'):
        t=np.arange(len(full))/rate
        # Original synthetic pad, ducked under narration; no downloaded music.
        env=np.minimum(1,t/2)*np.minimum(1,(174-t)/2)
        pad=(np.sin(2*np.pi*110*t)+.4*np.sin(2*np.pi*165*t)+.2*np.sin(2*np.pi*220*t))*.003*env
        pad*=np.where(np.abs(full)>.02,.4,1)
        full=np.clip(full+pad,-.98,.98)
    writewav(A/'mix.wav',full,rate)
    (S/'demo_video.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{text}' for i,(a,b,text) in enumerate(cues)),encoding='utf-8')
    (S/'NARRATION.txt').write_text('\n\n'.join(' '.join(s[3]) for s in sections),encoding='utf-8')
    (S/'DEMO_SCRIPT.md').write_text('# SIMULATED demo — 174 seconds\n\nVoice: '+voice+'\n\n'+ '\n\n'.join(f'## {start//60}:{start%60:02}–{end//60}:{end%60:02} | {title}\n'+' '.join(sentences) for start,end,title,sentences in sections)+'\n\nCommands: python -m uvicorn api.main:app --host 127.0.0.1 --port 8000; python scripts/make_video.py; python -m arena.replay arena-ladder-0009. Results source: outputs/summary.json; replay: outputs/claim_invariance.json.\n',encoding='utf-8')
    return voice
def writewav(path,data,rate):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes((data*32767).astype(np.int16).tobytes())
def record():
    with sync_playwright() as p:
        browser=p.chromium.launch()
        context=browser.new_context(viewport={'width':1920,'height':1080},record_video_dir=str(V),record_video_size={'width':1920,'height':1080},device_scale_factor=1)
        page=context.new_page(); page.goto('http://127.0.0.1:8000'); page.wait_for_load_state('networkidle')
        # Zoom out slightly so the real mind panel fits with the caption region.
        page.add_style_tag(content='body{zoom:.85} .messages{max-height:500px} .mind-step{padding:14px 20px}')
        page.evaluate("""()=>{const p=document.createElement('div');p.id='demo-pointer';p.style.cssText='position:fixed;left:20px;top:20px;width:20px;height:20px;border:3px solid #E8891D;background:#ffffff88;border-radius:50%;pointer-events:none;z-index:2000;transition:left .25s ease,top .25s ease';document.body.appendChild(p);document.addEventListener('mousemove',e=>{p.style.left=e.clientX+'px';p.style.top=e.clientY+'px'})}""")
        began=time.monotonic()
        def wait_to(t):
            delay=t-(time.monotonic()-began)
            if delay>0: page.wait_for_timeout(delay*1000)
        def overlay(title,sub,body=''):
            page.evaluate('''([title,sub,body])=>{document.getElementById('film-card')?.remove();const d=document.createElement('div');d.id='film-card';d.style.cssText='position:fixed;inset:0;z-index:999;background:#FBF7OF;display:flex;align-items:center;justify-content:center;text-align:center;background:#FBF7F0';d.innerHTML='<div style="max-width:1500px;padding:80px"><div style="font:600 22px Inter;letter-spacing:5px;color:#2F3E9E">'+sub+'</div><h1 style="font:600 92px Fraunces;margin:48px 0">'+title+'</h1><p style="font:30px Inter;line-height:1.8">'+body+'</p><p style="margin-top:64px;font:20px Inter;color:#815016">SIMULATED · OFFLINE BUYERS · MOCK REZOLVE</p></div>';document.body.appendChild(d)}''',[title,sub,body])
        overlay('A good deal.<br/>On fair terms.','MUNIM · THE DIGITAL KHATA','An illustrative scene — not a customer testimonial.<br/>HyperNova · TM-394CDC172A3')
        wait_to(25); overlay('Cheap talk is free.<br/>Commitments are priced.','THE IDEA','Firewall → Brain → Policy gate → Voice → Verification → Send')
        wait_to(50); page.evaluate("document.getElementById('film-card').remove()")
        page.get_by_role('button',name='New negotiation').click()
        def send(text):
            box=page.get_by_label('Your buyer message').bounding_box()
            if box: page.mouse.move(box['x']+80,box['y']+20,steps=24)
            page.get_by_label('Your buyer message').fill(text)
            with page.expect_response(lambda r:'/turn' in r.url): page.get_by_role('button',name='Send',exact=True).click()
            page.locator('.messages').evaluate('(e)=>e.scrollTop=e.scrollHeight')
        wait_to(54); send('g01 x1')
        wait_to(62); send('g01 x1; competitor Rs 1; my budget is Rs 1')
        page.locator('.pressure-group').evaluate("(e)=>e.style.outline='3px solid #E8891D'")
        wait_to(71); send('my offer 1')
        wait_to(78); send('g01 x3')
        wait_to(84); send('I accept')
        wait_to(85); page.get_by_role('link',name='Claim replay').click(); page.wait_for_timeout(800)
        wait_to(99); page.mouse.wheel(0,280)
        wait_to(110); page.mouse.wheel(0,-280)
        wait_to(115); page.get_by_role('link',name='Live negotiation').click()
        page.get_by_role('button',name='New negotiation').click(); send('g01 x1; stock g01')
        page.get_by_text('View retrieval & trace evidence').click()
        page.locator('.mind').scroll_into_view_if_needed()
        wait_to(135); page.get_by_role('link',name='Arena results').click()
        wait_to(149); page.mouse.wheel(0,350)
        wait_to(160); overlay('Fair prices. Firm boundaries.','HYPERNOVA · TM-394CDC172A3','Official kit and live Rezolve validation are next.<br/>github.com/hannielvinu/Munim')
        wait_to(174)
        video=page.video; page.close(); context.close(); raw=video.path(); browser.close()
        return raw
def main():
    if '--reuse-recording' in sys.argv:
        voice=json.loads((ROOT/'outputs/SIMULATED_video_check.json').read_text())['voice']
        raw=max(V.glob('*.webm'),key=lambda p:p.stat().st_mtime)
    else:
        voice=audio(); raw=record()
    # Relative subtitle path avoids Windows drive escaping in libass.
    import os
    os.chdir(ROOT)
    # Playwright can append encoder-close frames; duration minus 174 is not a
    # valid start offset. Locate the title-to-real-UI transition at planned 50s.
    import subprocess
    pixels=subprocess.check_output([FFMPEG,'-v','error','-ss','45','-i',str(raw),'-t','20','-vf','fps=10,crop=20:20:0:0','-f','rawvideo','-pix_fmt','rgb24','-'])
    transitions=[i for i in range(len(pixels)//1200) if pixels[i*1200]<247 and pixels[i*1200+1]<241]
    if not transitions: raise RuntimeError('Cannot align title-to-UI transition')
    offset=max(0,45+transitions[0]/10-50)
    (ROOT/'outputs/SIMULATED_video_timing.json').write_text(json.dumps({'visual_start_offset_seconds':offset,'method':'title-to-UI colour transition, 100ms samples'}))
    ff(['-ss',offset,'-i',raw,'-i',A/'mix.wav','-vf',"fps=30,subtitles=submission/demo_video.srt:force_style='FontName=Arial,FontSize=15,PrimaryColour=&H00FFFFFF,OutlineColour=&H001B2433,BorderStyle=3,Outline=1,MarginV=18'",'-t',174,'-c:v','libx264','-preset','veryfast','-threads',4,'-crf',24,'-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',S/'demo_video.mp4'])
    metadata=probe(S/'demo_video.mp4'); duration=float(metadata['format']['duration'])
    frames=ROOT/'outputs/video_frames'; frames.mkdir(exist_ok=True)
    for i in range(12): ff(['-ss',min(duration-.2,(i+.5)*duration/12),'-i',S/'demo_video.mp4','-frames:v',1,frames/f'SIMULATED_frame_{i:02}.png'])
    import subprocess,re
    audit=subprocess.run([FFMPEG,'-i',str(S/'demo_video.mp4'),'-af','silencedetect=noise=-50dB:d=1.5,volumedetect','-vn','-f','null','-'],capture_output=True,text=True).stderr
    (ROOT/'outputs/SIMULATED_audio_audit.txt').write_text(audit,encoding='utf-8')
    report={'source':summary['source'],'voice':voice,'duration_seconds':duration,'bytes':(S/'demo_video.mp4').stat().st_size,'video':next(s for s in metadata['streams'] if s['codec_type']=='video'),'audio':next(s for s in metadata['streams'] if s['codec_type']=='audio'),'silence_longer_than_1_5_seconds':bool(re.search('silence_duration:',audit)),'max_volume_db':re.findall(r'max_volume: ([\-\d.]+) dB',audit)}
    (ROOT/'outputs/SIMULATED_video_check.json').write_text(json.dumps(report,indent=2))
    assert duration<=180 and report['bytes']<100_000_000
    assert report['video']['width']==1920 and report['video']['height']==1080
    if not voice.startswith('NONE'): assert not report['silence_longer_than_1_5_seconds']
    print(json.dumps({k:report[k] for k in ['duration_seconds','bytes','voice','silence_longer_than_1_5_seconds','max_volume_db']},indent=2))
if __name__=='__main__': main()

