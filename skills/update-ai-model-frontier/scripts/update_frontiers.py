#!/usr/bin/env python3
"""AA Pareto report generator. Python 3.10+, no third-party dependencies."""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import json
import math
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
from thinking_levels import thinking_level

URL = 'https://artificialanalysis.ai/api/v2/language/models/free'
COMPANIES = {
    'Meta': ['Meta'], 'DeepSeek': ['DeepSeek'], 'OpenAI': ['OpenAI'],
    'Anthropic': ['Anthropic'], 'Alibaba / Qwen': ['Alibaba', 'Qwen'],
    'Google': ['Google'], 'xAI': ['SpaceXAI', 'xAI'], 'Mistral': ['Mistral', 'Mistral AI'],
    'Z AI': ['Z AI', 'Z.ai'], 'Moonshot AI / Kimi': ['Kimi', 'Moonshot AI'],
    'MiniMax': ['MiniMax'], 'NVIDIA': ['NVIDIA'], 'Xiaomi': ['Xiaomi'],
    'Amazon': ['Amazon'], 'Cohere': ['Cohere'],
}


class Failure(Exception):
    pass


def validate(snapshot):
    pages = snapshot['pages']
    if not pages:
        raise Failure('SCHEMA: Empty snapshot; fetch a complete catalogue.')
    total = pages[0]['pagination']['total_pages']
    version = pages[0]['intelligence_index_version']
    if total != len(pages):
        raise Failure('SCHEMA: Incomplete snapshot pagination; refresh all pages.')
    seen = set()
    for number, page in enumerate(pages, 1):
        p = page['pagination']
        if (p['page'] != number or p['total_pages'] != total or
                p['has_more'] != (number < total) or page['intelligence_index_version'] != version):
            raise Failure('SCHEMA: Pagination or index version changed during retrieval; retry later.')
        for model in page['data']:
            if model['id'] in seen:
                raise Failure('SCHEMA: Duplicate model IDs across pages; refresh the snapshot.')
            seen.add(model['id'])
    return snapshot


def request_page(number, key):
    for attempt in range(3):
        try:
            req = urllib.request.Request(f'{URL}?page={number}', headers={'x-api-key': key})
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response), response.headers
        except urllib.error.HTTPError as exc:
            if exc.code == 401:
                raise Failure('AUTH: API key rejected (401). Check the exported key and its organisation.') from None
            if exc.code == 403:
                raise Failure('TIER: Access denied (403) on the free endpoint. Check organisation API access.') from None
            if exc.code == 429:
                raise Failure(f'RATE_LIMIT: Quota exhausted. Retry-After={exc.headers.get("Retry-After", "unknown")} seconds; reset epoch={exc.headers.get("X-RateLimit-Reset", "unknown")}. Use a saved snapshot or wait.') from None
            if exc.code >= 500 and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise Failure(f'HTTP: AA returned {exc.code} on page {number}. Consult current API documentation; no report generated.') from None
        except (urllib.error.URLError, TimeoutError):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise Failure('NETWORK: Cannot reach Artificial Analysis after 3 attempts. Check DNS, network, and sandbox permissions.') from None


def retrieve():
    key = os.environ.get('ARTIFICIAL_ANALYSIS_API_KEY', '').strip()
    if not key:
        raise Failure('KEY_MISSING: Export ARTIFICIAL_ANALYSIS_API_KEY from a shell profile or secret manager before running. Otherwise follow the skill setup instructions.')
    pages = []
    for number in range(1, 101):
        page, headers = request_page(number, key)
        pages.append(page)
        p = page['pagination']
        if not p['has_more']:
            break
        remaining = headers.get('X-RateLimit-Remaining')
        if remaining is not None and int(remaining) < p['total_pages'] - number:
            raise Failure(f'RATE_LIMIT: Only {remaining} calls remain, insufficient for a complete snapshot. Reset epoch={headers.get("X-RateLimit-Reset", "unknown")}.')
    else:
        raise Failure('SCHEMA: Exceeded 100-page safety bound; inspect API pagination.')
    return validate({'retrieved_at': datetime.now(timezone.utc).isoformat(), 'source': URL, 'pages': pages})


def dominates(a, b):
    return a['cost'] <= b['cost'] and a['quality'] >= b['quality'] and (a['cost'] < b['cost'] or a['quality'] > b['quality'])


def frontier(rows):
    return sorted((r for r in rows if not any(dominates(o, r) for o in rows)), key=lambda r: (r['cost'], -r['quality'], r['model']))


def calculate(snapshot):
    aliases = {alias.casefold(): name for name, values in COMPANIES.items() for alias in values}
    rows, excluded = [], []
    for page in snapshot['pages']:
        for m in page['data']:
            q = m['evaluations'].get('artificial_analysis_intelligence_index')
            i, o = (m['pricing'].get(k) for k in ('price_1m_input_tokens', 'price_1m_output_tokens'))
            if not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in (q, i, o)) or i < 0 or o < 0:
                excluded.append({'id': m['id'], 'model': m['name'], 'reason': 'Missing/nonfinite score or price, or negative price'})
                continue
            company = m['model_creator']['name']
            rows.append({'company': aliases.get(company.casefold(), company), 'aa_company': company,
                         'model': m['name'], 'id': m['id'], 'quality': q, 'input': i, 'output': o,
                         'thinking_level': thinking_level(m['name']),
                         'thinking_level_source': 'parsed from AA model name',
                         'benchmark_cost_per_task_usd': ((m.get('artificial_analysis_intelligence_index_cost') or {}).get('cost_per_task') or {}).get('total_cost'),
                         'benchmark_total_cost_usd': (m.get('artificial_analysis_intelligence_index_cost') or {}).get('total_cost'),
                         'median_response_seconds': (m.get('performance') or {}).get('median_end_to_end_response_time_seconds'),
                         'median_first_token_seconds': (m.get('performance') or {}).get('median_time_to_first_token_seconds'),
                         'median_first_answer_token_seconds': (m.get('performance') or {}).get('median_time_to_first_answer_token_seconds'),
                         'median_output_tokens_per_second': (m.get('performance') or {}).get('median_output_tokens_per_second'),
                         'cost': float((3 * Decimal(str(i)) + Decimal(str(o))) / 4),
                         'has-api': 'inferred from AA pricing', 'self-hosted': 'unknown (free API omits licensing)'})
    if not rows:
        raise Failure('SCHEMA: No eligible models. Check AA response fields before proceeding.')
    individual = {c: frontier([r for r in rows if r['company'] == c]) for c in COMPANIES}
    selected = [r for r in rows if r['company'] in COMPANIES]
    return {'retrieved_at': snapshot['retrieved_at'], 'index_version': snapshot['pages'][0]['intelligence_index_version'],
            'total': len(rows) + len(excluded), 'eligible': len(rows), 'selected_eligible': len(selected),
            'excluded': excluded, 'eligible_models': rows, 'individual': individual, 'combined': frontier(selected), 'entire_catalogue': frontier(rows)}


def table(rows):
    def esc(v):
        return str(v).replace('|', '\\|').replace('\n', ' ')
    return '| Company | Model | AA score | Blended $/M | has-api | self-hosted |\n|---|---|---:|---:|---|---|\n' + '\n'.join(
        f"| {esc(r['company'])} | {esc(r['model'])} | {r['quality']} | {r['cost']:.4f} | inferred | unknown |" for r in rows)


def write_reports(result, output):
    output.mkdir(parents=True, exist_ok=True)
    warnings = [f'{c}: no eligible models; inspect creator aliases and missing prices/scores.' for c, rows in result['individual'].items() if not rows]
    for warning in warnings:
        print('WARNING: ' + warning, file=sys.stderr)
    intro = (f"# AI model Pareto frontiers\n\nSnapshot: {result['retrieved_at']}. AA Intelligence Index v{result['index_version']}. "
             f"Catalogue: {result['total']} models; {result['eligible']} eligible, {len(result['excluded'])} excluded; {result['selected_eligible']} eligible in the 15-company watchlist.\n\n"
             'Quality is the AA Intelligence Index (higher is better). Cost is (3 × input + output) / 4, USD per million tokens (lower is better). '
             'A model is dominated only by an equal-or-cheaper, equal-or-better model with at least one strict improvement. Exact ties retained; configurations are separate models.\n\n'
             'Missing scores/prices are excluded. Explicit zero prices are retained as AA reports them and may have free-endpoint conditions. '
             'has-api is inferred from pricing, not independently verified; self-hosted is unknown because the free API omits licensing. API price does not describe self-hosting costs.\n\n'
             'Source: [Artificial Analysis](https://artificialanalysis.ai/) · [API documentation](https://artificialanalysis.ai/data-api/docs)\n\n')
    sections = [('Combined frontier — 15-company watchlist', result['combined'])] + list(result['individual'].items()) + [('Combined frontier — entire AA catalogue', result['entire_catalogue'])]
    (output / 'aa-frontiers.md').write_text(intro + ('Warnings: ' + ' '.join(warnings) + '\n\n' if warnings else '') + '\n\n'.join('## ' + title + '\n\n' + (table(rows) if rows else 'No eligible models.') for title, rows in sections) + '\n')
    (output / 'aa-frontiers.json').write_text(json.dumps(result, indent=2) + '\n')
    for name, rows in [('company-frontiers', sum(result['individual'].values(), [])), ('combined-frontier', result['combined']), ('entire-catalogue-frontier', result['entire_catalogue'])]:
        with (output / (name + '.csv')).open('w', newline='') as handle:
            keys = list(rows[0]) if rows else ['company', 'model', 'quality', 'cost']
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path('outputs/ai-frontier'))
    parser.add_argument('--snapshot', type=Path, help='Use a complete saved snapshot offline; no key required')
    parser.add_argument('--refresh', action='store_true', help='Bypass the default 24-hour cache')
    args = parser.parse_args()
    if args.snapshot and args.refresh:
        parser.error('--snapshot and --refresh are mutually exclusive')
    cache = args.output_dir / 'snapshot.json'
    try:
        snapshot = None
        if args.snapshot:
            snapshot = validate(json.loads(args.snapshot.read_text()))
        elif cache.exists() and not args.refresh:
            candidate = validate(json.loads(cache.read_text()))
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(candidate['retrieved_at'])).total_seconds()
            if 0 <= age < 86400:
                snapshot = candidate
                print('Using cached snapshot from ' + snapshot['retrieved_at'])
        if snapshot is None:
            snapshot = retrieve()
        result = calculate(snapshot)
        write_reports(result, args.output_dir)
        temp = cache.with_suffix('.tmp')
        temp.write_text(json.dumps(snapshot))
        temp.replace(cache)
        print(f"Report: {(args.output_dir / 'aa-frontiers.md').resolve()} ({len(result['combined'])} combined-frontier models)")
    except Failure as exc:
        print('ERROR ' + str(exc), file=sys.stderr)
        return 1
    except (KeyError, TypeError, ValueError) as exc:
        print(f'ERROR SCHEMA: Invalid snapshot or API structure ({type(exc).__name__}). Check current API docs; for a corrupt cache use --refresh.', file=sys.stderr)
        return 1
    except OSError as exc:
        print(f'ERROR FILESYSTEM: {exc.strerror}. Check snapshot path and output-directory permissions.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
