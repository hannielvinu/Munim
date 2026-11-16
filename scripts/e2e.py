import json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
    dest=ROOT/'outputs/screenshots'; dest.mkdir(parents=True,exist_ok=True)
    report={'source':'SIMULATED','personas':[],'pages':[],'console_errors':[],'overflow':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
        page.on('pageerror',lambda e:report['console_errors'].append(str(e)))
        page.on('console',lambda e:report['console_errors'].append(e.text) if e.type=='error' else None)
        page.goto('http://127.0.0.1:8000'); page.get_by_role('heading',name='The negotiation desk.').wait_for()
        for persona in ['cooperative','hard bargainer','manipulator','prompt-injector','bundle seeker','confused']:
            page.get_by_label('Buyer persona').select_option(persona)
            page.get_by_role('button',name='New negotiation').click()
            page.get_by_role('button',name='Next buyer turn').wait_for()
            for turn in range(10):
                button=page.get_by_role('button',name='Next buyer turn')
                if button.is_disabled(): break
                with page.expect_response(lambda r:'/turn' in r.url and r.request.method=='POST') as info: button.click()
                response=info.value.json()
                if persona=='manipulator' and turn==1:
                    page.wait_for_timeout(250)
                    page.evaluate('window.scrollTo(0,0)')
                    page.locator('.messages').evaluate('(e)=>e.scrollTop=e.scrollHeight')
                    page.screenshot(path=str(dest/'SIMULATED_live_active_1440.png'),full_page=True)
                if response['response']['closed']: break
            assert response['response']['closed'],persona
            report['personas'].append({'persona':persona,'terminal':response['response']['move']['kind'],'turns':response['response']['round']})
        for width,height in [(1440,900),(390,844),(360,800)]:
            page.set_viewport_size({'width':width,'height':height})
            for path in ['/','/replay','/results','/shop','/khata']:
                page.goto('http://127.0.0.1:8000'+path); page.wait_for_load_state('networkidle')
                page.screenshot(path=str(dest/f"SIMULATED_{path.strip('/') or 'live'}_{width}.png"),full_page=True)
                overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth')
                assert not overflow,(path,width)
                report['pages'].append({'path':path,'width':width,'overflow':overflow})
        assert not report['console_errors'],report['console_errors']
        browser.close()
    (ROOT/'outputs/SIMULATED_e2e.json').write_text(json.dumps(report,indent=2))
    print('PASS: 6 persona negotiations; 15 responsive page checks; 0 overflow; 0 console errors')
if __name__=='__main__': main()

