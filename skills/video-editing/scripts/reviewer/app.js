'use strict';
const $ = id => document.getElementById(id);
const video = $('video');
let selection = null, pending = null, transcriptEntries = [], active = null, generation = 0;

function stamp(seconds) {
  const t = Math.max(0, Math.floor(seconds)), h = Math.floor(t / 3600);
  const m = Math.floor(t % 3600 / 60), s = String(t % 60).padStart(2, '0');
  return h ? `${h}:${String(m).padStart(2, '0')}:${s}` : `${m}:${s}`;
}
function route(path, draft, time) {
  const u = new URL(path ? '/review' : '/', location.origin);
  if (path) u.searchParams.set('path', path);
  if (draft) u.searchParams.set('draft', draft);
  if (time !== undefined) u.searchParams.set('t', Number(time.toFixed(3)));
  return u;
}
function endpoint(name, path, draft) {
  const u = new URL(name, location.origin);
  if (path) u.searchParams.set('path', path);
  if (draft) u.searchParams.set('draft', draft);
  return u;
}
async function api(url) {
  const r = await fetch(url);
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || 'Unable to load review');
  return data;
}
function notices(messages) {
  $('warnings').replaceChildren(...messages.map(text => {const p = document.createElement('p'); p.textContent = text; return p;}));
}
function navLink(node, url) {
  node.href = url;
  node.onclick = e => {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
    e.preventDefault(); navigate(url);
  };
}
function item(url, title, detail) {
  const a = document.createElement('a'); a.className = 'item';
  const h = document.createElement('strong'); h.textContent = title;
  const p = document.createElement('p'); p.textContent = detail;
  a.append(h, p); navLink(a, url); $('items').append(a);
}
function stopVideo() {
  pending = null; video.pause(); video.removeAttribute('src'); video.load();
  transcriptEntries = []; active = null;
}
async function navigate(url) {history.pushState(null, '', url); await load();}

async function load() {
  const run = ++generation;
  stopVideo(); selection = null;
  $('review').hidden = true; $('overview').hidden = false;
  $('draft-label').hidden = true; $('project-link').hidden = true;
  $('items').replaceChildren(); notices([]); $('title').textContent = 'Local video review';
  const params = new URL(location.href).searchParams;
  const path = params.get('path'), draft = params.get('draft');
  try {
    if (!path) {
      $('context').textContent = 'Selected local projects. Nothing is uploaded.';
      const data = await api('/api/projects'); if (run !== generation) return;
      for (const p of data.projects) item(route(p.path), p.title, p.path);
      if (!data.projects.length) notices(['No projects found. Start the server with --project or --root.']);
      return;
    }
    const overview = await api(endpoint('/api/project', path)); if (run !== generation) return;
    $('title').textContent = overview.title; $('context').textContent = overview.path;
    $('project-link').hidden = false; navLink($('project-link'), route(path));
    if (!draft) {
      for (const d of overview.drafts) item(route(path, d.id), d.title,
        d.playable ? `Rendered video${d.duration != null ? ' · ' + stamp(d.duration) : ''}` : d.warnings.join(' '));
      if (!overview.drafts.length) notices(['No drafts found. Add drafts/<id>/video.mp4, final.mp4, or a project review.json.']);
      return;
    }
    const data = await api(endpoint('/api/review', path, draft)); if (run !== generation) return;
    selection = {path, draft}; $('title').textContent = data.title; document.title = data.title + ' — local review';
    const select = $('draft-select'); select.replaceChildren();
    for (const d of overview.drafts) {const option = document.createElement('option'); option.value = d.id; option.textContent = d.title; select.append(option);}
    select.value = draft; $('draft-label').hidden = false;
    notices(data.warnings);
    if (!data.video_available) {notices([...data.warnings, 'Select a rendered draft. An edit plan alone cannot play yet.']); return;}
    $('overview').hidden = true; $('review').hidden = false;
    $('status').textContent = 'Loading video…';
    $('chapters').replaceChildren(); $('transcript').replaceChildren(); $('search').value = '';
    for (const c of data.chapters) timedLink(c.time, c.title, $('chapters'));
    $('chapter-panel').hidden = !data.chapters.length;
    transcriptEntries = data.paragraphs.map(p => ({...p, node: timedLink(p.start,
      (p.speaker != null ? `[${p.speaker}] ` : '') + p.text, $('transcript'))}));
    $('transcript-panel').hidden = !transcriptEntries.length;
    $('review').classList.toggle('no-transcript', !transcriptEntries.length);
    if (!data.chapters.length || !transcriptEntries.length) notices([...data.warnings,
      ...(!data.chapters.length ? ['No chapters supplied; playback is still available.'] : []),
      ...(!transcriptEntries.length ? ['No timed transcript supplied; playback is still available.'] : [])]);
    const t = Number(params.get('t') || 0);
    const valid = Number.isFinite(t) && t >= 0;
    if (!valid) notices([...data.warnings, 'Invalid timestamp; starting at zero.']);
    pending = {time: valid ? t : 0, play: valid && params.has('t')};
    video.src = endpoint('/media', path, draft).href; video.load();
  } catch (error) {
    if (run !== generation) return;
    notices([error.message]); $('context').textContent = 'Choose a permitted project/draft or inspect its review.json.';
  }
}
function timedLink(time, text, parent) {
  const a = document.createElement('a'); a.className = 'entry'; a.href = route(selection.path, selection.draft, time);
  const t = document.createElement('span'); t.className = 'time'; t.textContent = stamp(time);
  a.append(t, document.createTextNode(text));
  a.onclick = e => {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button) return;
    e.preventDefault(); jump(time, true);
  };
  parent.append(a); return a;
}
async function jump(time, play) {
  if (!selection || !Number.isFinite(time) || time < 0) return;
  if (video.readyState < 1) {pending = {time, play}; return;}
  time = Math.min(time, video.duration);
  video.currentTime = time;
  history.replaceState(null, '', route(selection.path, selection.draft, time));
  $('status').textContent = `At ${stamp(time)}`;
  if (play) {
    try {await video.play();}
    catch { $('status').textContent = `Ready at ${stamp(time)} — press Play (browser autoplay restriction).`; }
  }
}
video.addEventListener('loadedmetadata', () => {const request = pending; pending = null; if (request) jump(request.time, request.play);});
video.addEventListener('error', () => {if (selection && video.getAttribute('src')) $('status').textContent = 'Video could not load. Check format/browser codec support and server status.';});
video.addEventListener('timeupdate', () => {
  const p = transcriptEntries.find(p => p.start <= video.currentTime && video.currentTime < p.end);
  if (p !== active) {active?.node.classList.remove('active'); p?.node.classList.add('active'); active = p;}
});
$('back').onclick = () => jump(Math.max(0, video.currentTime - 10), true);
$('forward').onclick = () => jump(video.currentTime + 10, true);
function go() {
  const input = $('seek').value.trim(), nums = input.split(':').map(Number);
  if (!input || nums.length > 3 || nums.some(n => !Number.isFinite(n) || n < 0) || nums.slice(1).some(n => n >= 60)) {
    $('status').textContent = 'Use seconds, M:SS, or H:MM:SS'; return;
  }
  jump(nums.reduce((total, n) => total * 60 + n, 0), true);
}
$('go').onclick = go; $('seek').onkeydown = e => {if (e.key === 'Enter') go();};
$('draft-select').onchange = e => navigate(route(selection.path, e.target.value));
$('search').oninput = e => {
  const query = e.target.value.toLocaleLowerCase();
  for (const p of transcriptEntries) p.node.hidden = !p.text.toLocaleLowerCase().includes(query);
};
$('copy').onclick = async () => {
  if (!selection) return;
  const url = route(selection.path, selection.draft, video.currentTime).href;
  history.replaceState(null, '', url);
  try {await navigator.clipboard.writeText(url); $('status').textContent = 'Timestamp link copied';}
  catch {$('status').textContent = url;}
};
window.addEventListener('popstate', load);
load();
