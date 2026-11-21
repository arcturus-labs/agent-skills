"""Read-only project discovery and a small playback contract, not an edit renderer."""
from __future__ import annotations
import json
import math
from pathlib import Path
import re

VIDEO_TYPES = {'.mp4': 'video/mp4', '.m4v': 'video/mp4', '.webm': 'video/webm',
               '.mov': 'video/quicktime', '.ogv': 'video/ogg', '.ogg': 'video/ogg'}
DRAFT_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}\Z')


class ReviewError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def inside(path, root):
    return path == root or root in path.parents


def time_value(value):
    if isinstance(value, bool):
        raise ReviewError('A time must be nonnegative seconds or H:MM:SS')
    try:
        pieces = str(value).split(':')
        nums = [float(x) for x in pieces]
    except (ValueError, TypeError):
        raise ReviewError('Invalid time') from None
    if not 1 <= len(nums) <= 3 or any(not math.isfinite(n) or n < 0 for n in nums):
        raise ReviewError('Invalid time')
    if len(nums) > 1 and any(n >= 60 for n in nums[1:]):
        raise ReviewError('Invalid minutes/seconds')
    out = 0
    for n in nums:
        out = out * 60 + n
    return out


def read_json(path):
    if path.name == 'raw-response.json':
        raise ReviewError('Use a normalized timed transcript, not raw-response.json')
    if path.stat().st_size > 16 * 1024 * 1024:
        raise ReviewError('Metadata exceeds 16 MiB; provide a smaller normalized sidecar')
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (ValueError, UnicodeError):
        raise ReviewError(f'Invalid JSON in {path.name}') from None


class Library:
    def __init__(self, projects=(), roots=(), media_roots=()):
        self.projects = tuple(Path(p).expanduser().resolve(strict=True) for p in projects)
        self.roots = tuple(Path(p).expanduser().resolve(strict=True) for p in roots)
        self.media_roots = tuple(Path(p).expanduser().resolve(strict=True) for p in media_roots)
        if not self.projects and not self.roots:
            raise ReviewError('Select at least one --project or --root')
        if any(not p.is_dir() for p in self.projects + self.roots + self.media_roots):
            raise ReviewError('Configured roots/projects must be directories')

    def project(self, value):
        if not value:
            raise ReviewError('Choose a project directory using path=')
        path = Path(value).expanduser()
        if not path.is_absolute():
            raise ReviewError('path= must identify an absolute project directory')
        path = path.resolve()
        if path not in self.projects and not any(inside(path, root) for root in self.roots):
            raise ReviewError('Project is outside the selected directories', 403)
        if not path.is_dir():
            raise ReviewError('Project directory not found', 404)
        return path

    def local(self, project, directory, value, media=False):
        if not isinstance(value, str) or not value.strip():
            raise ReviewError('Sidecar paths must be nonempty strings')
        path = (directory / value).resolve()
        allowed = inside(path, project) or (media and any(inside(path, r) for r in self.media_roots))
        if not allowed:
            raise ReviewError('Referenced file is outside the selected project/media roots', 403)
        if not path.is_file():
            raise ReviewError(f'Referenced file not found: {Path(value).name}', 404)
        if media and path.suffix.lower() not in VIDEO_TYPES:
            raise ReviewError('Only browser-playable video file types are served')
        return path

    def list_projects(self):
        paths = set(self.projects)
        for root in self.roots:
            if any((root / n).exists() for n in ('PROJECT.md', 'review.json', 'drafts', 'final.mp4', 'video.mp4')):
                paths.add(root)
            for p in sorted(root.iterdir())[:1000]:
                if p.name.startswith('.') or not p.is_dir() or not inside(p.resolve(), root):
                    continue
                if any((p / n).exists() for n in ('PROJECT.md', 'review.json', 'drafts', 'final.mp4', 'video.mp4')):
                    paths.add(p.resolve())
        return [{'path': str(p), 'title': p.name} for p in sorted(paths)]

    def selection(self, project, draft):
        if draft == 'final':
            return project, 'final.review.json', 'final.mp4'
        if draft == 'project':
            return project, 'review.json', 'video.mp4'
        if not DRAFT_ID.fullmatch(draft) or draft in ('.', '..'):
            raise ReviewError('Invalid draft identifier')
        directory = (project / 'drafts' / draft).resolve()
        if not inside(directory, project) or not directory.is_dir():
            raise ReviewError('Draft directory not found', 404)
        return directory, 'review.json', 'video.mp4'

    def overview(self, value):
        project = self.project(value)
        ids = []
        drafts = project / 'drafts'
        if drafts.is_dir() and inside(drafts.resolve(), project):
            ids += [p.name for p in sorted(drafts.iterdir(), reverse=True)
                    if p.is_dir() and DRAFT_ID.fullmatch(p.name) and not p.name.startswith('.') and p.name not in ('project', 'final')][:256]
        if (project / 'final.mp4').is_file() or (project / 'final.review.json').is_file():
            ids.insert(0, 'final')
        if (project / 'video.mp4').is_file() or (project / 'review.json').is_file():
            ids.append('project')
        items = []
        for draft in ids:
            try:
                data, video = self.review(str(project), draft, with_transcript=False)
                items.append({'id': draft, 'title': data['title'], 'playable': video is not None,
                              'warnings': data['warnings'], 'duration': data.get('duration')})
            except (ReviewError, OSError) as exc:
                items.append({'id': draft, 'title': draft, 'playable': False, 'warnings': [str(exc)]})
        return {'path': str(project), 'title': project.name, 'drafts': items}

    def review(self, value, draft, with_transcript=True):
        project = self.project(value)
        directory, manifest_name, default_video = self.selection(project, draft)
        warnings = []
        config = {}
        manifest = directory / manifest_name
        if manifest.exists():
            config = read_json(self.local(project, directory, manifest_name))
            if not isinstance(config, dict) or config.get('version', 1) != 1:
                raise ReviewError('review.json must be a version-1 object')
        title = config.get('title', f'{project.name} — {draft}')
        if not isinstance(title, str):
            raise ReviewError('Review title must be text')
        video = None
        name = config.get('video', default_video)
        if name is not None:
            try:
                video = self.local(project, directory, name, media=True)
            except ReviewError as exc:
                # Invalid explicit paths are not silently replaced by another video.
                if 'video' in config:
                    raise
                warnings.append(str(exc))
        if video is None:
            warnings.append('No rendered video. Source-assembly previews are not implemented.')
        edit = {}
        if (directory / 'edit.json').exists():
            try:
                edit = read_json(self.local(project, directory, 'edit.json'))
                if not isinstance(edit, dict):
                    raise ReviewError('edit.json must be an object')
            except ReviewError as exc:
                warnings.append(str(exc)); edit = {}
        chapters = []
        chapter_input = config.get('chapters')
        if 'chapters' not in config:
            if (directory / 'chapters.json').exists():
                chapter_input = 'chapters.json'
            else:
                sequence = edit.get('sequence', [])
                if not isinstance(sequence, list):
                    warnings.append('No usable output-timed edit sequence; supply chapters explicitly')
                    sequence = []
                chapter_input = [{'time': e['output_start'], 'title': e.get('intent') or e.get('card') or 'Section'}
                                 for e in sequence if isinstance(e, dict) and 'output_start' in e]
        try:
            if isinstance(chapter_input, str):
                chapter_input = read_json(self.local(project, directory, chapter_input))
            if isinstance(chapter_input, dict):
                chapter_input = chapter_input.get('chapters')
            if chapter_input is not None:
                if not isinstance(chapter_input, list):
                    raise ReviewError('Chapters must be a list or a JSON sidecar')
                for c in chapter_input:
                    if not isinstance(c, dict) or not isinstance(c.get('title'), str):
                        raise ReviewError('Each chapter needs time and title')
                    chapters.append({'time': time_value(c['time']), 'title': c['title']})
                chapters.sort(key=lambda c: c['time'])
        except (ReviewError, KeyError) as exc:
            warnings.append('Chapters unavailable: ' + str(exc)); chapters = []
        transcript_name = config.get('transcript')
        if 'transcript' not in config:
            transcript_name = next((n for n in ('transcript-timed.json', 'transcript.json') if (directory / n).is_file()), None) if draft not in ('project', 'final') else None
        paragraphs = []
        if transcript_name and with_transcript:
            try:
                raw = read_json(self.local(project, directory, transcript_name))
                paragraphs = read_transcript(raw)
            except (ReviewError, KeyError, TypeError) as exc:
                warnings.append('Transcript unavailable: ' + str(exc))
        duration = config.get('duration', edit.get('duration'))
        if duration is not None:
            duration = time_value(duration)
        return {'path': str(project), 'draft': draft, 'title': title, 'duration': duration,
                'video_available': video is not None, 'chapters': chapters, 'paragraphs': paragraphs,
                'warnings': warnings, 'clock': 'selected video seconds; no source-clock remapping'}, video


def read_transcript(raw):
    if not isinstance(raw, dict):
        raise ReviewError('Expected normalized words, segments, or paragraphs object')
    if 'words' in raw:
        words = raw['words']
        if not isinstance(words, list):
            raise ReviewError('words must be an array')
        paragraphs, bucket = [], []
        def flush():
            if bucket:
                paragraphs.append({'start': bucket[0]['start'], 'end': max(w['end'] for w in bucket),
                                   'text': ' '.join(w['word'] for w in bucket), 'speaker': bucket[0].get('speaker')})
        previous = -1
        for w in words:
            if not isinstance(w, dict) or not isinstance(w.get('word'), str):
                raise ReviewError('Use normalized word/start/end entries')
            s, e = time_value(w['start']), time_value(w['end'])
            if s < previous or e < s:
                raise ReviewError('Word times must be ordered and end after start')
            previous = s
            item = {**w, 'start': s, 'end': e}
            if bucket and (w.get('speaker') != bucket[0].get('speaker') or s - bucket[0]['start'] >= 8 or s - bucket[-1]['end'] > 2):
                flush(); bucket = []
            bucket.append(item)
        flush()
        for card in raw.get('cards', []):
            paragraphs.append({'start': time_value(card['output_start']), 'end': time_value(card['output_end']),
                               'text': '[Silent card] ' + str(card.get('card', '')), 'speaker': None})
    else:
        entries = raw.get('paragraphs', raw.get('segments'))
        if not isinstance(entries, list):
            raise ReviewError('No supported timed transcript data')
        paragraphs = []
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get('text'), str):
                raise ReviewError('Paragraphs need start, end, and text')
            paragraphs.append({'start': time_value(entry['start']), 'end': time_value(entry['end']),
                               'text': entry['text'], 'speaker': entry.get('speaker')})
    if any(p['end'] < p['start'] for p in paragraphs):
        raise ReviewError('Transcript end precedes start')
    return sorted(paragraphs, key=lambda p: p['start'])
