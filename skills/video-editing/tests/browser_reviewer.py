#!/usr/bin/env python3
"""Optional hands-on browser QA. No search, accounts, uploads or real browser profile.
uv run --no-project --with playwright python tests/browser_reviewer.py \
  --browser-executable /path/to/chrome [--project /path/to/real-project] --output-dir /tmp/qa
Without --browser-executable, install Playwright Chromium in your test environment.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/reviewer'))
from model import Library
from serve import make_server


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--browser-executable')
    ap.add_argument('--project', action='append', default=[])
    ap.add_argument('--output-dir', required=True)
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    output = Path(a.output_dir).resolve(); output.mkdir(parents=True, exist_ok=True)
    checks = []
    def passed(name):
        checks.append(name); print('PASS:', name, flush=True)
    with tempfile.TemporaryDirectory(prefix='video-review-qa-') as tmp:
        base = Path(tmp).resolve()
        fixture = base / 'Synthetic review'; draft = fixture / 'drafts/001'; draft.mkdir(parents=True)
        subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','testsrc2=s=320x180:r=25:d=8',
                        '-f','lavfi','-i','sine=frequency=440:duration=8','-c:v','libx264','-pix_fmt','yuv420p',
                        '-c:a','aac','-movflags','+faststart',str(draft/'video.mp4')],check=True)
        title = '<img src=x onerror=alert(1)> Synthetic review'
        (draft/'review.json').write_text(json.dumps({'title':title, 'transcript':'transcript-timed.json',
              'chapters':[{'time':0,'title':'Opening'},{'time':3,'title':'Middle'}]}))
        (draft/'transcript-timed.json').write_text(json.dumps({'words':[
            {'word':'hello','start':1,'end':1.5,'speaker':'A'},
            {'word':'test','start':1.5,'end':2,'speaker':'A'},
            {'word':'second','start':4,'end':4.5,'speaker':'B'}]}))
        plain = fixture/'drafts/002'; plain.mkdir(); (plain/'video.mp4').symlink_to(draft/'video.mp4')
        pending = fixture/'drafts/003'; pending.mkdir()
        lib = Library(projects=[fixture, *a.project]); server = make_server(lib,0)
        thread = threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        root = f'http://127.0.0.1:{server.server_port}'
        def review(project,draft='001',t=None):
            q = {'path':str(project),'draft':draft}
            if t is not None:q['t']=t
            return root+'/review?'+urlencode(q)
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True, executable_path=a.browser_executable or None)
                context = browser.new_context(viewport={'width':1440,'height':1000})
                page = context.new_page(); errors = []
                def wait(expression, arg=None, timeout=10000):
                    # Direct DevTools evaluation polls without relaxing app CSP.
                    fn = expression if arg is not None else '() => Boolean(' + expression + ')'
                    deadline = time.monotonic() + timeout / 1000
                    while time.monotonic() < deadline:
                        if page.evaluate(fn, arg): return
                        time.sleep(.05)
                    raise AssertionError('Browser condition timed out: ' + expression)
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(root)
                page.get_by_role('link',name='Synthetic review',exact=False).first.click()
                page.wait_for_url('**/review?path=*')
                page.get_by_role('link',name=title,exact=False).click()
                wait('document.querySelector("video").readyState >= 1')
                assert page.locator('h1').inner_text()==title
                assert page.locator('h1 img').count()==0
                passed('Project/draft navigation and untrusted title displayed as text')
                page.locator('#chapters a').filter(has_text='Middle').click()
                wait('!document.querySelector("video").paused && document.querySelector("video").currentTime >= 3')
                assert page.locator('video').evaluate('(v)=>v.currentTime')<4.5
                passed('Chapter click seeks and plays rendered media')
                page.locator('video').evaluate('(v)=>v.pause()')
                page.locator('#transcript a').filter(has_text='hello test').click()
                wait('document.querySelector("video").currentTime >= 1 && document.querySelector("video").currentTime < 2.5')
                passed('Transcript paragraph click seeks to the selected video clock')
                page.locator('video').evaluate('(v)=>v.pause()')
                page.locator('#search').fill('second')
                assert page.locator('#transcript a:visible').count()==1
                page.locator('#search').fill('')
                page.locator('#seek').fill('0:05'); page.get_by_role('button',name='Go',exact=True).click()
                wait('document.querySelector("video").currentTime >= 5')
                passed('Transcript search and timestamp input')
                # Stub clipboard only; verify button builds an actual stable route.
                page.evaluate('Object.defineProperty(navigator,"clipboard",{value:{writeText:async(t)=>{window.copied=t}},configurable:true})')
                page.get_by_role('button',name='Copy link here').click()
                wait('typeof window.copied === "string"')
                assert 'draft=001' in page.evaluate('window.copied') and '&t=' in page.evaluate('window.copied')
                passed('Copy-link button emits a token-free timestamp URL')
                page.locator('#draft-select').select_option('002')
                wait('document.querySelector("video").readyState >= 1 && document.querySelector("#transcript-panel").hidden')
                assert page.locator('#chapter-panel').is_hidden()
                assert 'No timed transcript' in page.locator('#warnings').inner_text()
                passed('Video-only draft remains playable without chapters/transcript')
                page.locator('#draft-select').select_option('003')
                page.get_by_text('Select a rendered draft.',exact=False).wait_for()
                passed('Unrendered edit/draft shows clear unavailable state')
                page.goto(review(fixture,t=4))
                wait('document.querySelector("video").readyState >= 2 && document.querySelector("video").currentTime >= 4')
                passed('Direct timestamp link restores seek position on a fresh load')
                page.set_viewport_size({'width':390,'height':844})
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2')
                passed('Narrow-screen layout fits the viewport')
                page.set_viewport_size({'width':1440,'height':1000})
                for i, project in enumerate(a.project):
                    path=Path(project).resolve()
                    data=lib.overview(str(path)); playable=next(d for d in data['drafts'] if d['playable'])
                    page.goto(review(path,playable['id'],3370.12 if playable.get('duration',0) and playable['duration']>3371 else 1))
                    wait('document.querySelector("video").readyState >= 2',timeout=30000)
                    target=3370.12 if playable.get('duration',0) and playable['duration']>3371 else 1
                    wait('(t)=>Math.abs(document.querySelector("video").currentTime-t)<2',arg=target)
                    page.locator('video').evaluate('(v)=>v.pause()')
                    assert page.locator('#transcript a').count()>0
                    page.locator('#chapters a').first.click()
                    wait('!document.querySelector("video").paused')
                    wait('document.querySelector("video").currentTime > 0.2')
                    page.locator('video').evaluate('(v)=>v.pause()')
                    awaitable = page.locator('#transcript a').nth(1)
                    awaitable.click()
                    wait('!document.querySelector("video").paused')
                    page.locator('video').evaluate('(v)=>v.pause()')
                    page.screenshot(path=str(output/f'actual-{i}.png'),full_page=True)
                    passed('Actual project: metadata, long-range seek, chapter/paragraph playback and screenshot')
                assert not errors, errors
                passed('No JavaScript page errors')
                browser.close()
        finally:
            server.shutdown();server.server_close()
    (output/'result.json').write_text(json.dumps({'passed':checks,'count':len(checks),'browser':'isolated headless Chromium'},indent=2))
    print('All browser checks passed.',flush=True)


if __name__=='__main__':main()
