"""Render the static 'systems' panel as terminal-style SVGs (light and dark, desktop and mobile).

Run from the repo root:  python scripts/panels.py
Edit SYSTEMS below, then re-run.
"""
from pathlib import Path

from terminal import BAR_H, THEMES, frame, prompt, text, wrap

# What I build: (name, description, flow steps, tech used)
SYSTEMS = [
    ('voice-agents', 'Real-time phone and web voice agents',
     ['Phone / WebRTC', 'Speech-to-text', 'LLM + tools', 'Text-to-speech'],
     ['LiveKit Agents', 'Twilio', 'Deepgram', 'ElevenLabs', 'Silero VAD']),
    ('agent-systems', 'Multi-agent workflows with tools and memory',
     ['Task', 'Orchestrator', 'Specialist agents', 'MCP tools + RAG'],
     ['Google ADK (A2A)', 'MCP', 'OpenAI', 'Gemini', 'Pinecone', 'Langfuse']),
    ('ai-video', 'Automated video production',
     ['Script', 'Narration', 'Shot assets', 'Rendered video'],
     ['LLM scripting', 'TTS narration', 'AWS Step Functions', 'S3']),
    ('ai-products', 'Full-stack apps around AI backends',
     ['Web / mobile UI', 'API layer', 'LLM services', 'PostgreSQL'],
     ['Next.js', 'React Native', 'FastAPI', 'NestJS', 'Supabase', 'Neon']),
]
SEP = '  ·  '


def marker(t):
    return (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{t["dim"]}"/></marker></defs>')


def chip(t, x, y, w, h, label, size):
    return '\n'.join([
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="5" fill="{t["chip"]}" stroke="{t["border"]}"/>',
        text(f'{x + w / 2:.1f}', f'{y + h / 2 + size * 0.35:.1f}', label, size, t['text'], None, 'middle'),
    ])


def dashed(t, x1, x2, y):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{t["border"]}" stroke-dasharray="3 4"/>'


def systems(t, mobile):
    out = [marker(t)]
    if not mobile:
        w, x, s = 1080, 36, 15
        y = BAR_H + 42
        out.append(prompt(t, x, y, 'ls ~/systems', s))
        y += 22
        fx, ch, gap = 336, 36, 30
        cw = (w - x - fx - gap * 3) / 4
        for i, (name, desc, flow, tech) in enumerate(SYSTEMS):
            top = y + 20
            if i:
                out.append(dashed(t, x, w - x, y + 2))
            out.append(text(x + 18, top + 22, f'{name}/', s, t['blue']))
            for j, ln in enumerate(wrap(desc, 32)):
                out.append(text(x + 18, top + 44 + 18 * j, ln, 13, t['muted']))
            for j, step in enumerate(flow):
                cx = fx + j * (cw + gap)
                out.append(chip(t, cx, top + 4, cw, ch, step, 13.5))
                if j:
                    out.append(f'<line x1="{cx - gap + 4:.1f}" y1="{top + 4 + ch / 2:.1f}" x2="{cx - 4:.1f}" '
                               f'y2="{top + 4 + ch / 2:.1f}" stroke="{t["dim"]}" stroke-width="1.4" marker-end="url(#ah)"/>')
            out.append(text(fx, top + ch + 30, SEP.join(tech), 12.5, t['dim']))
            y = top + ch + 50
        h = y + 8
    else:
        w, x, s = 440, 20, 12.5
        y = BAR_H + 32
        out.append(prompt(t, x, y, 'ls ~/systems', s))
        y += 8
        for i, (name, desc, flow, tech) in enumerate(SYSTEMS):
            y += 14
            if i:
                out.append(dashed(t, x, w - x, y - 4))
            y += 18
            out.append(text(x + 8, y, f'{name}/', s, t['blue']))
            y += 18
            out.append(text(x + 8, y, desc, 11.5, t['muted']))
            for ln in wrap(' → '.join(flow), 52):
                y += 19
                out.append(text(x + 8, y, ln, s, t['text']))
            for ln in wrap(' · '.join(tech), 58):
                y += 17
                out.append(text(x + 8, y, ln, 11, t['dim']))
            y += 6
        h = y + 20
    label = 'What I build. ' + ' '.join(
        f'{n}: {d} ({" to ".join(f)}), using {", ".join(tc)}.' for n, d, f, tc in SYSTEMS)
    return frame(t, w, h, 'systems', '\n'.join(out), label)


def main():
    for theme, t in THEMES.items():
        for mobile in (False, True):
            name = f'systems-{theme}' + ('-mobile' if mobile else '')
            Path(f'assets/{name}.svg').write_text(systems(t, mobile), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
