"""Render the static profile panels (intro, systems, stack) as terminal-style SVGs.

Run from the repo root:  python scripts/panels.py
Edit the content constants below, then re-run.
"""
from pathlib import Path

from terminal import BAR_H, BLUE, BORDER, DIM, MUTED, TEXT, frame, prompt, text, wrap

NAME = 'Raj Acharya'
ROLE = 'Applied AI Engineer'
SUMMARY = ('I build AI systems end to end: real-time voice agents, multi-agent workflows, '
           'AI video pipelines and the applications around them.')

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

STACK = [
    ('languages', ['Python', 'TypeScript', 'JavaScript', 'SQL']),
    ('voice', ['LiveKit Agents', 'Twilio', 'Deepgram', 'ElevenLabs', 'Silero VAD']),
    ('llm_agents', ['OpenAI', 'Gemini', 'Google ADK (A2A)', 'MCP', 'Vercel AI SDK', 'Ollama']),
    ('retrieval', ['Pinecone', 'Embeddings', 'RAG pipelines']),
    ('observability', ['Langfuse tracing']),
    ('backend', ['FastAPI', 'NestJS', 'Node.js', 'WebSockets']),
    ('frontend', ['Next.js', 'React', 'React Native (Expo)', 'Tailwind CSS', 'shadcn/ui']),
    ('data', ['PostgreSQL', 'Neon', 'Supabase', 'Drizzle', 'TypeORM']),
    ('cloud', ['AWS (S3, SES, Step Functions)', 'Docker', 'Railway', 'Render']),
]

SEP = '  ·  '


def hero(mobile):
    if not mobile:
        w, x, s = 1080, 36, 15
        y = BAR_H + 42
        out = [prompt(x, y, 'whoami', s)]
        y += 52
        out.append(text(x, y, NAME, 40, TEXT, 700))
        y += 36
        out.append(text(x, y, ROLE, 19, TEXT))
        for ln in wrap(SUMMARY, 96):
            y += 26
            out.append(text(x, y, ln, s, MUTED))
        y += 46
        out.append(prompt(x, y, '', s, cursor=True))
        h = y + 30
    else:
        w, x, s = 440, 20, 12.5
        y = BAR_H + 32
        out = [prompt(x, y, 'whoami', s)]
        y += 40
        out.append(text(x, y, NAME, 30, TEXT, 700))
        y += 26
        out.append(text(x, y, ROLE, 15, TEXT))
        y += 4
        for ln in wrap(SUMMARY, 52):
            y += 19
            out.append(text(x, y, ln, s, MUTED))
        y += 34
        out.append(prompt(x, y, '', s, cursor=True))
        h = y + 24
    return frame(w, h, 'raj@dev: ~', '\n'.join(out), f'{NAME}, {ROLE}. {SUMMARY}')


MARKER = (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
          f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{DIM}"/></marker></defs>')


def chip(x, y, w, h, label, size):
    return '\n'.join([
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="5" fill="#161b22" stroke="{BORDER}"/>',
        text(f'{x + w / 2:.1f}', f'{y + h / 2 + size * 0.35:.1f}', label, size, TEXT, None, 'middle'),
    ])


def systems(mobile):
    out = [MARKER]
    if not mobile:
        w, x, s = 1080, 36, 15
        y = BAR_H + 42
        out.append(prompt(x, y, 'ls ~/systems', s))
        y += 22
        fx, ch, gap = 336, 36, 30
        cw = (w - x - fx - gap * 3) / 4
        for i, (name, desc, flow, tech) in enumerate(SYSTEMS):
            top = y + 20
            if i:
                out.append(f'<line x1="{x}" y1="{y + 2}" x2="{w - x}" y2="{y + 2}" stroke="{BORDER}" stroke-dasharray="3 4"/>')
            out.append(text(x + 18, top + 22, f'{name}/', s, BLUE))
            out.append(text(x + 18, top + 44, desc if len(desc) <= 32 else wrap(desc, 32)[0], 13, MUTED))
            if len(desc) > 32:
                out.append(text(x + 18, top + 62, wrap(desc, 32)[1], 13, MUTED))
            for j, step in enumerate(flow):
                cx = fx + j * (cw + gap)
                out.append(chip(cx, top + 4, cw, ch, step, 13.5))
                if j:
                    out.append(f'<line x1="{cx - gap + 4:.1f}" y1="{top + 4 + ch / 2:.1f}" x2="{cx - 4:.1f}" '
                               f'y2="{top + 4 + ch / 2:.1f}" stroke="{DIM}" stroke-width="1.4" marker-end="url(#ah)"/>')
            out.append(text(fx, top + ch + 30, SEP.join(tech), 12.5, DIM))
            y = top + ch + 50
        h = y + 8
    else:
        w, x, s = 440, 20, 12.5
        y = BAR_H + 32
        out.append(prompt(x, y, 'ls ~/systems', s))
        y += 8
        for i, (name, desc, flow, tech) in enumerate(SYSTEMS):
            y += 14
            if i:
                out.append(f'<line x1="{x}" y1="{y - 4}" x2="{w - x}" y2="{y - 4}" stroke="{BORDER}" stroke-dasharray="3 4"/>')
            y += 18
            out.append(text(x + 8, y, f'{name}/', s, BLUE))
            y += 18
            out.append(text(x + 8, y, desc, 11.5, MUTED))
            for ln in wrap(' → '.join(flow), 52):
                y += 19
                out.append(text(x + 8, y, ln, s, TEXT))
            for ln in wrap(' · '.join(tech), 58):
                y += 17
                out.append(text(x + 8, y, ln, 11, DIM))
            y += 6
        h = y + 20
    label = 'What I build. ' + ' '.join(
        f'{n}: {d} ({" to ".join(f)}), using {", ".join(t)}.' for n, d, f, t in SYSTEMS)
    return frame(w, h, 'systems', '\n'.join(out), label)


def stack(mobile):
    out = []
    if not mobile:
        w, x, s = 1080, 36, 15
        y = BAR_H + 42
        out.append(prompt(x, y, 'cat stack.yml', s))
        y += 12
        for key, vals in STACK:
            y += 30
            out.append(text(x + 18, y, f'{key}:', s, BLUE))
            out.append(text(x + 210, y, SEP.join(vals), s, TEXT))
        h = y + 32
    else:
        w, x, s = 440, 20, 12.5
        y = BAR_H + 32
        out.append(prompt(x, y, 'cat stack.yml', s))
        y += 6
        for key, vals in STACK:
            y += 26
            out.append(text(x + 12, y, f'{key}:', s, BLUE))
            for ln in wrap(' · '.join(vals), 48):
                y += 18
                out.append(text(x + 28, y, ln, s, TEXT))
        h = y + 26
    label = 'Tech stack. ' + ' '.join(f'{k}: {", ".join(v)}.' for k, v in STACK)
    return frame(w, h, 'stack.yml', '\n'.join(out), label)


def main():
    for name, fn in [('intro', hero), ('systems', systems), ('stack', stack)]:
        Path(f'assets/{name}.svg').write_text(fn(False), encoding='utf-8', newline='\n')
        Path(f'assets/{name}-mobile.svg').write_text(fn(True), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
