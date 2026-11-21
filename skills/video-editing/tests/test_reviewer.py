"""Offline contracts, discovery, streaming and path isolation. No desktop or API calls."""
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib import request, error, parse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts' / 'reviewer'))
from model import Library, ReviewError, read_transcript, time_value
from serve import make_server, byte_range


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


class ReviewerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.collection = self.base / 'collection'
        self.project = self.collection / "a project's space"
        self.draft = self.project / 'drafts/001'; self.draft.mkdir(parents=True)
        self.video = self.draft / 'video.mp4'; self.video.write_bytes(bytes(range(256)) * 8)
        self.other = self.base / 'outside'; self.other.mkdir()
        self.lib = Library(roots=[self.collection])

    def test_discovery_and_optional_data(self):
        projects = self.lib.list_projects()
        self.assertEqual(projects[0]['path'], str(self.project))
        data, video = self.lib.review(str(self.project), '001')
        self.assertEqual(video, self.video)
        self.assertEqual(data['paragraphs'], []); self.assertEqual(data['chapters'], [])
        self.assertTrue(data['video_available'])
        (self.project / 'drafts/002').mkdir()
        overview = self.lib.overview(str(self.project))
        self.assertEqual([d['id'] for d in overview['drafts']], ['002', '001'])
        self.assertFalse(overview['drafts'][0]['playable'])

    def test_manifest_words_cards_and_chapters(self):
        save(self.draft / 'words.json', {'words': [
            {'word': 'hello', 'start': 1, 'end': 2, 'speaker': 'A'},
            {'word': 'world', 'start': 2, 'end': 3, 'speaker': 'A'}],
            'cards': [{'output_start': 0, 'output_end': 1, 'card': 'opening'}]})
        save(self.draft / 'review.json', {'version': 1, 'title': '<script>not executable</script>',
             'video': 'video.mp4', 'transcript': 'words.json', 'chapters': [{'time': '0:01', 'title': 'Start'}]})
        data, _ = self.lib.review(str(self.project), '001')
        self.assertEqual(data['title'], '<script>not executable</script>')
        self.assertEqual(data['paragraphs'][1]['text'], 'hello world')
        self.assertEqual(data['chapters'][0]['time'], 1)
        save(self.draft / 'review.json', {'transcript': None, 'chapters': []})
        self.assertEqual(self.lib.review(str(self.project), '001')[0]['paragraphs'], [])

    def test_conventional_metadata_and_bad_optional_data(self):
        save(self.draft / 'transcript-timed.json', {'paragraphs': [{'start': 1, 'end': 2, 'text': 'Text'}]})
        save(self.draft / 'chapters.json', {'chapters': [{'time': 0, 'title': 'Beginning'}]})
        data, _ = self.lib.review(str(self.project), '001')
        self.assertEqual(data['paragraphs'][0]['text'], 'Text')
        self.assertEqual(len(data['chapters']), 1)
        (self.draft / 'transcript-timed.json').write_text('not json')
        data, video = self.lib.review(str(self.project), '001')
        self.assertEqual(video, self.video); self.assertIn('Transcript unavailable', ' '.join(data['warnings']))
        save(self.draft / 'review.json', {'transcript': 'raw-response.json'})
        save(self.draft / 'raw-response.json', {'words': []})
        self.assertIn('not raw-response.json', ' '.join(self.lib.review(str(self.project), '001')[0]['warnings']))

    def test_final_root_and_edit_chapters(self):
        (self.project / 'final.mp4').write_bytes(b'final')
        (self.project / 'video.mp4').write_bytes(b'original')
        ids = [d['id'] for d in self.lib.overview(str(self.project))['drafts']]
        self.assertIn('final', ids); self.assertIn('project', ids)
        save(self.draft / 'edit.json', {'sequence': [{'output_start': 0, 'intent': 'Introduction'},
             {'output_start': 4, 'card': 'closing'}]})
        self.assertEqual(len(self.lib.review(str(self.project), '001')[0]['chapters']), 2)
        # Never automatically attach source-clock transcripts from assets to a render.
        save(self.project / 'assets/transcripts/source/transcript.json', {'words': []})
        self.assertEqual(self.lib.review(str(self.project), 'final')[0]['paragraphs'], [])

    def test_outside_symlinks_and_file_types(self):
        with self.assertRaises(ReviewError): self.lib.project(str(self.other))
        with self.assertRaises(ReviewError): self.lib.project('../project')
        with self.assertRaises(ReviewError): self.lib.review(str(self.project), '../outside')
        foreign = self.other / 'outside.mp4'; foreign.write_bytes(b'external')
        (self.draft / 'escape.mp4').symlink_to(foreign)
        save(self.draft / 'review.json', {'video': 'escape.mp4'})
        with self.assertRaises(ReviewError): self.lib.review(str(self.project), '001')
        allowed = Library(projects=[self.project], media_roots=[self.other])
        self.assertEqual(allowed.review(str(self.project), '001')[1], foreign)
        secret = self.project / '.env'; secret.write_text('not a real secret')
        save(self.draft / 'review.json', {'video': '../../.env'})
        with self.assertRaises(ReviewError): self.lib.review(str(self.project), '001')
        save(self.draft / 'review.json', {'transcript': str(foreign)})
        self.assertIn('outside', ' '.join(allowed.review(str(self.project), '001')[0]['warnings']))

    def test_bad_edit_sequence_does_not_disable_video(self):
        save(self.draft / 'edit.json', {'sequence': None})
        data, video = self.lib.review(str(self.project), '001')
        self.assertEqual(video, self.video)
        self.assertEqual(data['chapters'], [])
        self.assertIn('No usable', ' '.join(data['warnings']))

    def test_times_and_ranges(self):
        self.assertEqual(time_value('1:02:03.5'), 3723.5)
        for t in (-1, 'nan', 'inf', True, '1:70'):
            with self.assertRaises(ReviewError): time_value(t)
        for value, expected in [('bytes=1-3', (1, 3, True)), ('bytes=-3', (7, 9, True)),
                                ('bytes=8-', (8, 9, True)), (None, (0, 9, False))]:
            self.assertEqual(byte_range(value, 10), expected)
        for bad in ['bytes=10-', 'bytes=3-1', 'bytes=-0', 'bytes=0-1,3-4', 'bytes=-', 'invalid']:
            with self.assertRaises(ReviewError): byte_range(bad, 10)
        with self.assertRaises(ReviewError): read_transcript({'words': [{'word': 'x', 'start': 2, 'end': 1}]})

    def test_http_media_and_isolation(self):
        server = make_server(self.lib, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        base = f'http://127.0.0.1:{server.server_port}'
        query = parse.urlencode({'path': str(self.project), 'draft': '001'})
        def get(path, headers=None, method='GET'):
            try:
                response = request.urlopen(request.Request(base + path, headers=headers or {}, method=method))
            except error.HTTPError as e:
                response = e
            with response:
                return response.status, response.headers, response.read()
        status, headers, html = get('/review?' + query + '&t=1.5')
        self.assertEqual(status, 200); self.assertIn(b'app.js', html)
        self.assertEqual(headers['X-Frame-Options'], 'DENY')
        self.assertNotIn('unsafe-inline', headers['Content-Security-Policy'])
        self.assertEqual(get('/api/review?' + query)[0], 200)
        self.assertEqual(get('/static/app.js')[0], 200)
        status, headers, body = get('/media?' + query, {'Range': 'bytes=256-259'})
        self.assertEqual((status, body), (206, bytes(range(4))))
        self.assertEqual(headers['Content-Range'], 'bytes 256-259/2048')
        status, headers, body = get('/media?' + query, method='HEAD')
        self.assertEqual((status, len(body), headers['Content-Length']), (200, 0, '2048'))
        self.assertEqual(get('/media?' + query, {'Range': 'bytes=9999-'})[0], 416)
        for path in ['/api/review?' + parse.urlencode({'path': str(self.other)}), '/static/../.env', '/.env', '/unknown']:
            self.assertIn(get(path)[0], (403, 404))
        self.assertEqual(get('/api/projects', {'Host': 'evil.example'})[0], 403)
        self.assertEqual(get('/api/projects', {'Origin': 'https://evil.example'})[0], 403)
        self.assertEqual(get('/media?' + query, {'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'no-cors'})[0], 403)
        self.assertEqual(get('/review?' + query, {'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'navigate'})[0], 200)
        self.assertEqual(get('/api/projects', method='POST')[0], 405)
        self.assertEqual(get('/api/project?path=x&path=y')[0], 400)
        # Page visits do not alter the reviewed content.
        self.assertEqual(self.video.read_bytes(), bytes(range(256)) * 8)


if __name__ == '__main__': unittest.main()
