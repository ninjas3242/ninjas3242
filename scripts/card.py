"""Render the neofetch-style profile card from GitHub GraphQL JSON on stdin.

Writes assets/card-{dark,light}.svg and assets/card-{dark,light}-mobile.svg.
Edit ROWS to change the profile text.
"""
import json
import math
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from terminal import BAR_H, THEMES, frame, spans, text, wrap

USER = 'raj'
HOST = 'ninjas3242'
ROWS = [
    ('Role', 'Applied AI Engineer'),
    ('Focus', 'Voice agents · Multi-agent systems · AI video'),
    ('Uptime', None),  # filled with time on GitHub
    ('Languages', 'Python · TypeScript · JavaScript · SQL'),
    None,
    ('Stack.Voice', 'LiveKit · Twilio · Deepgram · ElevenLabs'),
    ('Stack.Agents', 'Google ADK · MCP · OpenAI · Gemini'),
    ('Stack.RAG', 'Pinecone · Embeddings · Langfuse tracing'),
    ('Stack.Backend', 'FastAPI · NestJS · Node.js · WebSockets'),
    ('Stack.Frontend', 'Next.js · React · React Native'),
    ('Stack.Infra', 'PostgreSQL · Supabase · AWS · Docker'),
]
CHARS = ' .:-=+*#%@'


def waveform(cols, rows):
    """ASCII audio waveform: bars on alternate columns, list of rows of (char, level 0..3 or None)."""
    mid = (rows - 1) / 2
    amps = []
    for c in range(cols):
        x = c / max(1, cols - 1)
        env = 0.3 + 0.7 * math.sin(math.pi * x) ** 1.2
        r = (math.sin(c * 12.9898 + 4.1) * 43758.5453) % 1.0
        amps.append(env * (0.22 + 0.78 * r) if c % 2 == 0 else 0)
    grid = []
    for r in range(rows):
        d = abs(r - mid) / (mid + 0.5)
        line = []
        for a in amps:
            if a <= 0 or d > a:
                line.append((' ', None))
                continue
            k = 1 - d / a
            ch = '@' if k > .75 else '#' if k > .5 else '*' if k > .3 else '=' if k > .12 else ':'
            line.append((ch, 3 if k > .75 else 2 if k > .5 else 1 if k > .25 else 0))
        grid.append(line)
    return grid


def draw_art(t, x, y, cols, rows, size, lh):
    out = []
    for r, line in enumerate(waveform(cols, rows)):
        parts = []
        for ch, lvl in line:
            parts.append((ch, t['ramp'][lvl] if lvl is not None else t['bg']))
        # merge runs of the same colour to keep the SVG small
        merged = []
        for s, c in parts:
            if merged and merged[-1][1] == c:
                merged[-1] = (merged[-1][0] + s, c)
            else:
                merged.append((s, c))
        out.append(spans(x, f'{y + r * lh:.1f}', size, merged))
    return '\n'.join(out)


def uptime(created, today):
    years = today.year - created.year
    months = today.month - created.month
    days = today.day - created.day
    if days < 0:
        months -= 1
        prev = today.replace(day=1) - timedelta(days=1)
        days += prev.day
    if months < 0:
        years -= 1
        months += 12
    plural = lambda n, w: f'{n} {w}' + ('' if n == 1 else 's')
    return f'{plural(years, "year")}, {plural(months, "month")}, {plural(days, "day")}'


def stats(data):
    user = data['data']['user']
    cal = user['contributionsCollection']['contributionCalendar']
    days = sorted((date.fromisoformat(d['date']), d['contributionCount'])
                  for w in cal['weeks'] for d in w['contributionDays'])
    end = days[-1][0]
    days = [(d, n) for d, n in days if d > end - timedelta(days=365)]
    created = datetime.fromisoformat(user['createdAt'].replace('Z', '+00:00')).date()
    return {
        'contributions': sum(n for _, n in days),
        'active_days': sum(1 for _, n in days if n),
        'best_day': max(n for _, n in days),
        'active_weeks': len({d - timedelta(days=d.weekday()) for d, n in days if n}),
        'repos': user['repositories']['totalCount'],
        'uptime': uptime(created, end),
        'since': created.strftime('%b %Y'),
        'end': end,
    }


def kv(t, x, y, size, key, value, keyw):
    dots = ' ' + '.' * max(2, keyw - len(key) - 1) + ' '
    return spans(x, y, size, [(key, t['blue']), (dots, t['dim']), (value, t['text'])])


def rule(t, x, y, size, label, width, head=False):
    if head:
        parts = [(USER, t['green']), ('@', t['muted']), (HOST, t['green']), (' ', t['muted'])]
        used = len(USER) + 1 + len(HOST) + 1
    else:
        parts = [('— ', t['dim']), (label, t['text']), (' ', t['dim'])]
        used = len(label) + 3
    parts.append(('—' * max(0, width - used), t['dim']))
    return spans(x, y, size, parts)


def card(t, s, mobile):
    rows = [(k, s['uptime'] if v is None else v) if k else None for k, v in
            ((r if r else (None, None)) for r in ROWS)]
    gh = [('Contributions', f'{s["contributions"]:,}'), ('Active days', f'{s["active_days"]}'),
          ('Active weeks', f'{s["active_weeks"]}'), ('Best day', f'{s["best_day"]}'),
          ('Public repos', f'{s["repos"]}'), ('Member since', s['since'])]
    out = []
    if not mobile:
        w, size, lh = 1080, 15, 23.5
        art_size, art_lh, cols, art_rows = 14, 15, 33, 21
        ix = 36 + cols * art_size * 0.6 + 44
        chars = int((w - 36 - ix) / (size * 0.6))
        y = BAR_H + 44
        lines = [rule(t, ix, y, size, '', chars, head=True)]
        for row in rows:
            y += lh
            if row:
                lines.append(kv(t, ix, y, size, row[0], row[1], 17))
        y += lh * 1.5
        lines.append(rule(t, ix, y, size, 'GitHub · past year', chars))
        for i in range(0, len(gh), 2):
            y += lh
            lines.append(kv(t, ix, y, size, gh[i][0], gh[i][1], 17))
            lines.append(kv(t, ix + chars * size * 0.6 / 2 + 18, y, size, gh[i + 1][0], gh[i + 1][1], 15))
        h = y + 38
        art_h = art_rows * art_lh
        ay = BAR_H + (h - BAR_H - art_h) / 2 + art_lh * 0.75
        out.append(draw_art(t, 36, ay, cols, art_rows, art_size, art_lh))
        out.extend(lines)
    else:
        w, size, lh = 440, 11.5, 19
        x = 20
        chars = int((w - 2 * x) / (size * 0.6))
        art_rows, art_lh = 11, 9
        y = BAR_H + 22
        out.append(draw_art(t, x, y, chars, art_rows, size, art_lh))
        y += art_rows * art_lh + 22
        out.append(rule(t, x, y, size, '', chars, head=True))
        for row in rows:
            if not row:
                y += 6
                continue
            vals = wrap(row[1], chars - 15)
            y += lh
            out.append(kv(t, x, y, size, row[0], vals[0], 14))
            for v in vals[1:]:
                y += lh - 3
                out.append(text(x + 15 * size * 0.6, y, v, size, t['text']))
        y += lh * 1.4
        out.append(rule(t, x, y, size, 'GitHub · past year', chars))
        for k, v in gh:
            y += lh
            out.append(kv(t, x, y, size, k, v, 16))
        h = y + 26
    label = (f'Raj Acharya, Applied AI Engineer. Focus: voice agents, multi-agent systems, AI video. '
             f'{s["contributions"]:,} GitHub contributions in the past year across {s["active_days"]} active days.')
    return frame(t, w, h, f'{USER}@{HOST} — neofetch', '\n'.join(out), label)


def main():
    s = stats(json.load(sys.stdin))
    for theme, t in THEMES.items():
        for mobile in (False, True):
            name = f'card-{theme}' + ('-mobile' if mobile else '')
            Path(f'assets/{name}.svg').write_text(card(t, s, mobile), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
