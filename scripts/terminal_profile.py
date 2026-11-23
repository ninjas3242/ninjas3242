"""Render the animated terminal profile from GitHub GraphQL JSON on stdin.

Writes assets/terminal.svg: a looping terminal session that types `neofetch`,
`ls ~/systems` and `cat ~/.github/stats`, with live stats and a subtle glitch.
Edit the content constants below; the daily workflow re-renders the file.
"""
import json
import sys
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path

USER, HOST = 'raj', 'ninjas3242'
INFO = [
    ('Role', 'Applied AI Engineer'),
    ('Focus', 'Voice agents, multi-agent systems, AI video'),
    ('Uptime', None),  # time on GitHub, filled in from stats
    ('Languages', 'Python, TypeScript, JavaScript, SQL'),
    ('Voice', 'LiveKit, Twilio, Deepgram, ElevenLabs'),
    ('Agents', 'Google ADK, MCP, OpenAI, Gemini'),
    ('Retrieval', 'Pinecone, embeddings, Langfuse tracing'),
    ('Backend', 'FastAPI, NestJS, Node.js, WebSockets'),
    ('Frontend', 'Next.js, React, React Native'),
    ('Infra', 'PostgreSQL, Supabase, AWS, Docker'),
]
SYSTEMS = [
    ('voice-agents/', 'real-time phone and web voice agents: STT, LLM tool calling, TTS'),
    ('agent-systems/', 'multi-agent workflows with MCP tools, RAG memory and tracing'),
    ('ai-video/', 'automated pipelines from script and narration to rendered video'),
    ('ai-products/', 'full-stack web and mobile apps around AI backends'),
]

# Palette: dark teal terminal, mint accents (pixegami-style)
BG, BAR, EDGE = '#0c1d24', '#152a31', '#24414b'
TEXT, MUTED, DIM = '#dce9e7', '#86a3a8', '#4f6d73'
MINT, TEAL, BLUE = '#5af78e', '#3fbfa8', '#57b8ff'
SEG = ('#2b3d45', '#1d5a57', MINT)
ART = {'.': '#2a5f5a', ':': '#358a7d', '+': '#3fbfa8', '*': '#5af78e', '(': MINT, '@': MINT, ')': MINT}
BLOCKS = [['#1d2b33', '#ff5370', '#5af78e', '#f4b860', '#57b8ff', '#b07cff', '#2fbfa5', '#c9d4d6'],
          ['#2e4450', '#ff8a9e', '#9effbf', '#ffd38a', '#9ad3ff', '#d0b0ff', '#7fe0cf', '#ffffff']]
GLITCH_RED, GLITCH_CYAN = '#ff4f7b', '#4de8ff'

FONT = "'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"
W, SIZE, LH, X0 = 1000, 15, 21, 26
CW = SIZE * 0.6
BAR_H = 34
LOOP = 26.0          # seconds per loop
FADE_AT = LOOP - 1.4  # everything fades out here, then the loop restarts
GLITCHES = [2.15, 13.4, 18.2, 22.3]


def esc(s):
    return escape(str(s), quote=True)


# ---------- ASCII art: a stippled 3-5-5-3 neural network ----------
def neural_net(cols=37, rows=17, layers=(3, 5, 5, 3)):
    g = [[0] * cols for _ in range(rows)]
    xs = [round(2 + i * (cols - 5) / (len(layers) - 1)) for i in range(len(layers))]
    nodes = []
    for i, n in enumerate(layers):
        span = (rows - 1) * (n - 1) / (max(layers) - 1)
        nodes.append([(xs[i], round((rows - 1) / 2 - span / 2 + j * span / max(1, n - 1))) for j in range(n)])
    for a, b in zip(nodes, nodes[1:]):
        for x1, y1 in a:
            for x2, y2 in b:
                steps, seen = abs(x2 - x1) * 3, set()
                for k in range(1, steps):
                    p = (round(x1 + (x2 - x1) * k / steps), round(y1 + (y2 - y1) * k / steps))
                    if p not in seen:
                        seen.add(p)
                        g[p[1]][p[0]] += 1
    out = [[' ' if v == 0 else '.' if v == 1 else ':' if v == 2 else '+' if v <= 4 else '*' for v in r] for r in g]
    for layer in nodes:
        for x, y in layer:
            out[y][x - 1:x + 2] = list('(@)')
    return [''.join(r) for r in out]


# ---------- stats ----------
def uptime(created, today):
    y, m, d = today.year - created.year, today.month - created.month, today.day - created.day
    if d < 0:
        m -= 1
        d += (today.replace(day=1) - timedelta(days=1)).day
    if m < 0:
        y, m = y - 1, m + 12
    pl = lambda n, w: f'{n} {w}' + ('' if n == 1 else 's')
    return f'{pl(y, "year")}, {pl(m, "month")}, {pl(d, "day")}'


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
        'active_weeks': len({d - timedelta(days=d.weekday()) for d, n in days if n}),
        'best_day': max(n for _, n in days),
        'repos': user['repositories']['totalCount'],
        'uptime': uptime(created, end),
        'since': created.strftime('%b %Y'),
    }


# ---------- animation helpers ----------
class Timeline:
    def __init__(self):
        self.frames = {}

    def show(self, t):
        """Class name for an element that appears at time t and stays until the loop fades."""
        key = f'a{int(round(t * 100))}'
        if key not in self.frames:
            p = t / LOOP * 100
            f = FADE_AT / LOOP * 100
            self.frames[key] = (f'@keyframes {key}{{0%,{p:.3f}%{{opacity:0}}{p + 0.01:.3f}%,{f:.3f}%{{opacity:1}}'
                                f'{f + 1.6:.3f}%,100%{{opacity:0}}}}'
                                f'.{key}{{animation:{key} {LOOP}s linear infinite}}')
        return key

    def css(self):
        return '\n'.join(self.frames.values())


def glitch_keyframes(name, dx):
    """Brief offset flashes at each glitch time; invisible otherwise."""
    stops = ['0%{opacity:0;transform:translate(0,0)}']
    for g in GLITCHES:
        a, b, c = (g / LOOP * 100, (g + 0.07) / LOOP * 100, (g + 0.16) / LOOP * 100)
        stops += [f'{a - 0.01:.3f}%{{opacity:0;transform:translate(0,0)}}',
                  f'{a:.3f}%{{opacity:.9;transform:translate({dx}px,0)}}',
                  f'{b:.3f}%{{opacity:.7;transform:translate({-dx * 0.6:.1f}px,1px)}}',
                  f'{c:.3f}%{{opacity:0;transform:translate(0,0)}}']
    stops.append('100%{opacity:0}')
    return f'@keyframes {name}{{{"".join(stops)}}}.{name}{{animation:{name} {LOOP}s linear infinite}}'


def jitter_keyframes(name, dx):
    stops = ['0%{transform:translate(0,0)}']
    for g in GLITCHES:
        a, b = g / LOOP * 100, (g + 0.12) / LOOP * 100
        stops += [f'{a - 0.01:.3f}%{{transform:translate(0,0)}}', f'{a:.3f}%{{transform:translate({dx}px,0)}}',
                  f'{b:.3f}%{{transform:translate(0,0)}}']
    stops.append('100%{transform:translate(0,0)}')
    return f'@keyframes {name}{{{"".join(stops)}}}.{name}{{animation:{name} {LOOP}s linear infinite}}'


def txt(x, y, s, fill, cls='', weight=None, extra=''):
    c = f' class="{cls}"' if cls else ''
    w = f' font-weight="{weight}"' if weight else ''
    return f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}"{w}{c}{extra}>{esc(s)}</text>'


def prompt(tl, x, y, t, command, type_from):
    """Powerline prompt drawn at time t, then the command typed starting at type_from. Returns (svg, end_time)."""
    cls = tl.show(t)
    out, h, top = [], LH - 3, y - 15
    segs = [(f' {USER} ', TEXT, SEG[0]), (' ~ ', TEXT, SEG[1]), ('   main ', BG, SEG[2])]
    cx = x
    for i, (label, fg, bg) in enumerate(segs):
        w = len(label) * CW
        out.append(f'<rect x="{cx:.1f}" y="{top}" width="{w + 8:.1f}" height="{h}" fill="{bg}" class="{cls}"/>')
        out.append(txt(cx + 4, y, label, fg, cls, 600 if i == 2 else None))
        if i == 2:  # git branch glyph, drawn so it never depends on font support
            bx, by = cx + 4 + CW * 1.2, top + 3.5
            out.append(f'<g class="{cls}" stroke="{BG}" stroke-width="1.6" fill="none">'
                       f'<line x1="{bx}" y1="{by}" x2="{bx}" y2="{by + 10}"/>'
                       f'<circle cx="{bx}" cy="{by + 11.5}" r="1.6"/><circle cx="{bx + 6}" cy="{by + 2}" r="1.6"/>'
                       f'<path d="M{bx + 6} {by + 3.6} C{bx + 6} {by + 7} {bx} {by + 6} {bx} {by + 9}"/></g>')
        cx += w + 8
        nxt = segs[i + 1][2] if i + 1 < len(segs) else BG
        out.append(f'<rect x="{cx:.1f}" y="{top}" width="9" height="{h}" fill="{nxt}" class="{cls}"/>')
        out.append(f'<path d="M{cx:.1f} {top} L{cx + 9:.1f} {top + h / 2:.1f} L{cx:.1f} {top + h}Z" fill="{bg}" class="{cls}"/>')
        cx += 9
    cx += CW
    tt = type_from
    for i, ch in enumerate(command):
        tt += 0.075 + (0.05 if ch == ' ' else 0) + (0.03 * ((i * 7) % 3))
        if ch != ' ':
            out.append(txt(cx + i * CW, y, ch, TEXT, tl.show(tt)))
    return '\n'.join(out), tt, cx + len(command) * CW


def render(s):
    tl = Timeline()
    body, css = [], []
    y = BAR_H + 30
    t = 0.35

    # 1) neofetch
    svg, t, _ = prompt(tl, X0, y, t, 'neofetch', t + 0.35)
    body.append(svg)
    t += 0.35
    art = neural_net()
    info_x = X0 + len(art[0]) * CW + 40
    y0 = y + LH
    css.append(jitter_keyframes('jit', 4))
    body.append('<g class="jit">')
    for r, line in enumerate(art):
        cls = tl.show(t + r * 0.035)
        parts, cur = [], None
        for ch in line:
            col = ART.get(ch, BG)
            if parts and col == cur:
                parts[-1][0] += ch
            else:
                parts.append([ch, col])
                cur = col
        spans = ''.join(f'<tspan fill="{c}"{" font-weight=&quot;700&quot;" if c == MINT else ""}>{esc(p)}</tspan>'
                        for p, c in parts).replace('&quot;', '"')
        body.append(f'<text x="{X0}" y="{y0 + r * LH:.1f}" class="{cls}">{spans}</text>')
    body.append('</g>')
    # name with glitch copies
    name = f'{USER}@{HOST}'
    cls = tl.show(t)
    css.append(glitch_keyframes('gr', -3))
    css.append(glitch_keyframes('gc', 3))
    css.append(jitter_keyframes('gj', 2))
    body.append(f'<g class="{cls}">'
                f'<text x="{info_x}" y="{y0}" fill="{GLITCH_RED}" font-weight="700" class="gr" opacity="0">{esc(name)}</text>'
                f'<text x="{info_x}" y="{y0}" fill="{GLITCH_CYAN}" font-weight="700" class="gc" opacity="0">{esc(name)}</text>'
                f'<g class="gj"><text x="{info_x}" y="{y0}" font-weight="700" xml:space="preserve">'
                f'<tspan fill="{MINT}">{USER}</tspan><tspan fill="{TEXT}">@</tspan><tspan fill="{MINT}">{HOST}</tspan>'
                f'</text></g></g>')
    body.append(txt(info_x, y0 + LH, '-' * len(name), DIM, tl.show(t + 0.035)))
    for i, (k, v) in enumerate(INFO):
        v = s['uptime'] if v is None else v
        cls = tl.show(t + (i + 2) * 0.035)
        body.append(f'<text x="{info_x}" y="{y0 + (i + 2) * LH:.1f}" class="{cls}" xml:space="preserve">'
                    f'<tspan fill="{MINT}" font-weight="700">{esc(k)}</tspan><tspan fill="{TEXT}">: {esc(v)}</tspan></text>')
    for r, row in enumerate(BLOCKS):
        cls = tl.show(t + (13 + r) * 0.035)
        for i, col in enumerate(row):
            body.append(f'<rect x="{info_x + i * CW * 3:.1f}" y="{y0 + (13 + r) * LH - 15:.1f}" width="{CW * 3:.1f}" '
                        f'height="{LH}" fill="{col}" class="{cls}"/>')
    y = y0 + len(art) * LH + LH * 0.6
    t += len(art) * 0.035 + 0.9

    # 2) ls ~/systems
    svg, t, _ = prompt(tl, X0, y, t, 'ls ~/systems', t + 0.3)
    body.append(svg)
    t += 0.35
    for i, (n, d) in enumerate(SYSTEMS):
        cls = tl.show(t + i * 0.05)
        yy = y + (i + 1) * LH
        body.append(txt(X0, yy, n, BLUE, cls, 700))
        body.append(txt(X0 + 17 * CW, yy, d, MUTED, cls))
    y += (len(SYSTEMS) + 1) * LH + LH * 0.6
    t += 1.1

    # 3) cat ~/.github/stats
    svg, t, _ = prompt(tl, X0, y, t, 'cat ~/.github/stats', t + 0.3)
    body.append(svg)
    t += 0.35
    cls = tl.show(t)
    bx, by, bw, bh = X0, y + 14, 640, LH * 3 + 26
    title = ' GitHub · past year '
    body.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6" fill="none" stroke="{TEAL}" '
                f'stroke-opacity=".7" class="{cls}"/>')
    body.append(f'<rect x="{bx + 14}" y="{by - 2}" width="{len(title) * CW:.1f}" height="4" fill="{BG}" class="{cls}"/>')
    body.append(txt(bx + 14, by + 5, title, MINT, cls, 700))
    cells = [('Contributions', f'{s["contributions"]:,}'), ('Active days', str(s['active_days'])),
             ('Active weeks', str(s['active_weeks'])), ('Best day', str(s['best_day'])),
             ('Public repos', str(s['repos'])), ('On GitHub since', s['since'])]
    for i, (k, v) in enumerate(cells):
        col, row = i % 2, i // 2
        cls = tl.show(t + 0.1 + row * 0.06)
        cx = bx + 22 + col * (bw / 2)
        yy = by + 32 + row * LH
        body.append(txt(cx, yy, k, MUTED, cls))
        body.append(txt(cx + 26 * CW - 22, yy, v, TEXT, cls, 700, ' text-anchor="end"'))
    y = by + bh + LH + 14
    t += 0.9

    # 4) idle prompt with blinking cursor
    svg, _, cur_x = prompt(tl, X0, y, t, '', t)
    body.append(svg)
    body.append(f'<g class="{tl.show(t)}"><rect x="{cur_x:.1f}" y="{y - 14}" width="{CW:.1f}" height="17" fill="{MINT}" '
                f'class="blink"/></g>')
    css.append(f'@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}.blink{{animation:blink 1.1s steps(1) infinite}}')
    # faint glitch scan line across the window
    css.append(glitch_keyframes('gs', 0))
    H = y + 34
    body.append(f'<rect x="0" y="{BAR_H + 150}" width="{W}" height="2" fill="{GLITCH_CYAN}" class="gs" opacity="0"/>')
    body.append(f'<rect x="0" y="{BAR_H + 420}" width="{W}" height="1" fill="{GLITCH_RED}" class="gs" opacity="0"/>')

    style = (f'text{{font-family:{FONT};font-size:{SIZE}px;white-space:pre}}\n{tl.css()}\n' + '\n'.join(css) +
             '\n@media (prefers-reduced-motion: reduce){*{animation:none!important}}')
    dots = ''.join(f'<circle cx="{W - 70 + i * 22}" cy="{BAR_H / 2}" r="6" fill="{c}"/>'
                   for i, c in enumerate(('#2e4a53', '#2e4a53', '#ff5f57')))
    label = (f'Animated terminal. neofetch: Raj Acharya, Applied AI Engineer focused on voice agents, multi-agent systems '
             f'and AI video; stack Python, TypeScript, LiveKit, Twilio, Deepgram, ElevenLabs, Google ADK, MCP, OpenAI, '
             f'Gemini, Pinecone, FastAPI, NestJS, Next.js, React Native, PostgreSQL, AWS. Systems: '
             + '; '.join(f'{n} {d}' for n, d in SYSTEMS) +
             f'. GitHub past year: {s["contributions"]:,} contributions, {s["active_days"]} active days.')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" width="{W}" height="{H:.0f}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<style>
{style}
</style>
<defs><clipPath id="win"><rect width="{W}" height="{H:.0f}" rx="12"/></clipPath></defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H:.0f}" fill="{BG}"/>
<rect width="{W}" height="{BAR_H}" fill="{BAR}"/>
<line x1="0" y1="{BAR_H}" x2="{W}" y2="{BAR_H}" stroke="{EDGE}"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1:.0f}" rx="12" fill="none" stroke="{EDGE}"/>
<text x="{W / 2}" y="{BAR_H / 2 + 5}" text-anchor="middle" fill="{MUTED}" style="font-size:13px">{USER}@{HOST}: ~</text>
{dots}
{chr(10).join(body)}
</svg>
'''


def main():
    s = stats(json.load(sys.stdin))
    Path('assets/terminal.svg').write_text(render(s), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
