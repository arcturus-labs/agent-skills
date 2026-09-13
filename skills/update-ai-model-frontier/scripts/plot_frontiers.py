#!/usr/bin/env python3
"""Plot the company frontiers and combined watchlist frontier from report JSON."""
import argparse
import json
from pathlib import Path
import sys
import textwrap
import re
from thinking_levels import thinking_level, THINKING_STYLES

def model_family(name):
    """Remove only explicit thinking qualifiers, preserving versions/fallbacks."""
    def keep(match):
        parts = [part.strip() for part in match.group(1).split(',')]
        parts = [part for part in parts if not re.fullmatch(
            r'(?:non[- ]reasoning|reasoning|adaptive reasoning|thinking|'
            r'(?:minimal|low|medium|high|xhigh|extra[- ]high|max)(?: effort)?)', part, re.I)]
        return ' (' + ', '.join(parts) + ')' if parts else ''
    return re.sub(r'\s*\(([^)]*)\)', keep, name).strip().casefold()

def thinking_families(frontier_rows, eligible, aliases):
    wanted = {(r['_company'], model_family(r['model'])) for r in frontier_rows}
    families = {}
    for r in eligible:
        company = aliases.get(r['company'], r['company'])
        key = (company, model_family(r['model']))
        if key in wanted:
            families.setdefault(key, {})[r['id']] = r
    return {key: sorted(rows.values(), key=lambda r: (r['quality'], r['cost'], r['id']))
            for key, rows in families.items() if len(rows) > 1}

def add_model_labels(fig, ax, rows, company_colors):
    """Label all main frontier points, not supplemental thinking variants."""
    selected = sorted(rows, key=lambda r: (-r['quality'], r['cost'], r['model']))
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    occupied = []
    for row in selected:
        # Only remove thinking qualifiers; preserve unrelated parentheticals.
        def clean(match):
            pieces = [x.strip() for x in match.group(1).split(',')]
            pieces = [x for x in pieces if not re.search(r'reasoning|effort|^(max|xhigh|high|medium|low|minimal)$', x, re.I)]
            return '(' + ', '.join(pieces) + ')' if pieces else ''
        label = re.sub(r'\s*\(([^)]*)\)', clean, row['model']).strip()
        label = textwrap.fill(label, 28)
        best = None
        for distance in (8, 16, 26, 38, 52):
            for dx, dy, ha, va in [(distance,distance,'left','bottom'),(-distance,distance,'right','bottom'),
                                   (distance,-distance,'left','top'),(-distance,-distance,'right','top'),
                                   (distance,0,'left','center'),(-distance,0,'right','center')]:
                a = ax.annotate(label, (row['cost'], row['quality']), xytext=(dx,dy),
                                textcoords='offset points', ha=ha, va=va, fontsize=9,
                                color=company_colors[row['_company']], zorder=25,
                                bbox={'facecolor':'white','alpha':.85,'edgecolor':'none','pad':1})
                box = a.get_window_extent(renderer).expanded(1.04,1.12)
                bounds = ax.get_window_extent(renderer)
                penalty = sum(box.overlaps(b) for b in occupied) * 10000
                penalty += 10000 * (box.x0 < bounds.x0 or box.x1 > bounds.x1 or box.y0 < bounds.y0 or box.y1 > bounds.y1)
                penalty += distance
                if best is None or penalty < best[0]:
                    if best is not None:
                        best[1].remove()
                    best = (penalty,a,box)
                else:
                    a.remove()
            if best[0] < 10000:
                break
        occupied.append(best[2])

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('report', type=Path)
    p.add_argument('--output', type=Path, required=True, help='PNG output path; SVG also saved')
    args = p.parse_args()
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        data = json.loads(args.report.read_text())
        groups = data.get('individual', data.get('perCompany'))
        aliases = {'OpenAI':'OpenAI', 'Anthropic':'Anthropic', 'Meta':'Meta', 'SpaceXAI':'xAI / Grok', 'xAI':'xAI / Grok', 'Alibaba':'Alibaba / Qwen', 'Alibaba / Qwen':'Alibaba / Qwen', 'DeepSeek':'DeepSeek', 'Z AI':'Z AI'}
        groups = {aliases[k]: v for k, v in groups.items() if k in aliases}
        all_rows = [{**r, '_company': company} for company, rows in groups.items() for r in rows]
        combined = sorted([r for r in all_rows if not any(o['cost'] <= r['cost'] and o['quality'] >= r['quality'] and (o['cost'] < r['cost'] or o['quality'] > r['quality']) for o in all_rows)], key=lambda r:r['cost'])
        meta = data.get('metadata', {})
        date = data.get('retrieved_at', meta.get('retrieved', 'unknown'))[:10]
        version = data.get('index_version', meta.get('index_version', 'unknown'))
        colors = plt.get_cmap('tab20').colors
        line_count = sum(len(textwrap.wrap(r['model'], width=35)) + 1.7 for r in all_rows)
        fig, ax = plt.subplots(figsize=(16, 10))
        company_colors = {}
        axes = [ax]
        fig.patch.set_facecolor('#f8fafc')
        for ax in axes:
            ax.set_facecolor('white')
            ax.grid(True, color='#e2e8f0', linewidth=.7)
            ax.set_axisbelow(True)
            ax.spines[['top', 'right']].set_visible(False)
            ax.set_xlabel('Cost · USD per million tokens', fontsize=11, labelpad=10)
            ax.set_ylabel(f'Quality · AA Intelligence Index v{version}', fontsize=11)
        for j, (company, rows) in enumerate(groups.items()):
            rows = sorted(rows, key=lambda r: (r['cost'], r['quality']))
            color = colors[(j * 2) % 20 if j < 10 else (j - 10) * 2 + 1]
            company_colors[company] = color
            for ax in axes:
                ax.plot([r['cost'] for r in rows], [r['quality'] for r in rows],
                        '-', color=color, lw=1.6, alpha=.85, label=company)
                for row in rows:
                    level = row.get('thinking_level', thinking_level(row['model']))
                    if level == 'reasoning_unspecified':
                        level = 'unspecified'
                    marker = THINKING_STYLES[level][0]
                    ax.scatter(row['cost'], row['quality'], marker=marker,
                               s=95 if level == 'max' else 48, color=color,
                               edgecolors='white', linewidths=.35, zorder=12)
        for ax in axes:
            ax.plot([r['cost'] for r in combined], [r['quality'] for r in combined],
                    color='#0f172a', linestyle=':', linewidth=3, label='Combined frontier', zorder=10)
        families = thinking_families(all_rows, data.get('eligible_models', []), aliases)
        frontier_ids = {r['id'] for r in all_rows}
        added = 0
        for (company, family), variants in families.items():
            color = company_colors[company]
            ax.plot([r['cost'] for r in variants], [r['quality'] for r in variants],
                    color=color, linewidth=.5, alpha=.65, zorder=3)
            for r in variants:
                if r['id'] in frontier_ids:
                    continue
                level = r.get('thinking_level', thinking_level(r['model']))
                if level == 'reasoning_unspecified':
                    level = 'unspecified'
                ax.scatter(r['cost'], r['quality'], marker=THINKING_STYLES[level][0],
                           s=65 if level == 'max' else 32, color=color, alpha=.8,
                           edgecolors='white', linewidths=.3, zorder=7)
                added += 1
        if 'eligible_models' not in data:
            print('WARNING: No eligible_models in report; regenerate it to include thinking variants.', file=sys.stderr)
        print(f'Added {added} measured variants across {len(families)} model families.')
        axes[0].set_xlim(-.25, max(r['cost'] for r in combined) * 1.07)
        axes[0].set_ylim(0, max(r['quality'] for rows in groups.values() for r in rows) + 4)
        axes[0].set_title('All price tiers', loc='left', fontsize=13, fontweight='bold')
        fig.suptitle('AI model Pareto frontiers', x=.065, y=.98, ha='left', fontsize=23, fontweight='bold', color='#0f172a')
        fig.text(.065, .925, f'{len(groups)} companies · snapshot {date} · color = company · symbol = thinking level', fontsize=11, color='#475569')
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(.5, .065), ncol=4, frameon=False, fontsize=10)
        fig.text(.065, .035, 'Cost = (3 × input + output) / 4. Dotted line = combined frontier of these seven companies.', fontsize=9, color='#475569')
        fig.text(.065, .013, 'Source: Artificial Analysis · artificialanalysis.ai   |   Thin lines connect recorded thinking settings of the same model.', fontsize=9, color='#475569')
        fig.subplots_adjust(top=.86, bottom=.17, left=.065, right=.97)
        add_model_labels(fig, ax, all_rows, company_colors)
        present = {r.get('thinking_level', thinking_level(r['model'])) for r in all_rows}
        present.update(r.get('thinking_level', thinking_level(r['model'])) for variants in families.values() for r in variants)
        present.discard('reasoning_unspecified')
        present.add('unspecified')
        # Show the shared six-level vocabulary even when some levels are dominated.
        levels = {'none', 'low', 'medium', 'high', 'xhigh', 'max'} | present
        thinking_handles = [Line2D([], [], color='#334155', marker=marker, linestyle='None',
                                   markersize=8, label=label)
                            for level, (marker, label) in THINKING_STYLES.items() if level in levels]
        legend = ax.legend(handles=thinking_handles, title='Thinking level', loc='lower right',
                           fontsize=9, title_fontsize=10, frameon=True, facecolor='white', framealpha=1,
                           edgecolor='#e2e8f0', borderpad=1, labelspacing=.65)
        legend.set_zorder(50)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.output, dpi=180, facecolor=fig.get_facecolor())
        fig.savefig(args.output.with_suffix('.svg'), facecolor=fig.get_facecolor())
        plt.close(fig)
        print(args.output.resolve())
    except ImportError:
        print('ERROR CHART_DEPENDENCY: matplotlib is required. Use a Python runtime with matplotlib; the standard-library report generator still works.', file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f'ERROR CHART: Check the report JSON and writable output path ({type(e).__name__}).', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
