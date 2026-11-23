"""Render the static profile panels (intro, architecture, stack) as terminal-style SVGs.

Run from the repo root:  python scripts/panels.py
Edit the content constants below, then re-run.
"""
from pathlib import Path

from terminal import BAR_H, BLUE, BORDER, DIM, MUTED, TEXT, frame, prompt, text, wrap

NAME = 'Raj Acharya'
ROLE = 'Applied AI Engineer'
SUMMARY = 'I design and ship real-time voice agents, agentic systems and AI video pipelines.'

FOCUS = [
    ('voice-agents', 'Phone and WebRTC agents: streaming STT, LLM tool calling, TTS, live call monitoring'),
    ('agentic-systems', 'Multi-agent orchestration, MCP tool servers, RAG retrieval, tracing with Langfuse'),
    ('ai-video', 'Automated pipelines from script and narration to a finished, rendered video'),
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

# Voice agent architecture: main pipeline and the services the LLM agent calls.
PIPELINE = [('Caller', 'PSTN / web'), ('Twilio', 'SIP trunk'), ('LiveKit', 'media room'),
            ('Deepgram', 'speech-to-text'), ('LLM agent', 'tool calling'), ('ElevenLabs', 'text-to-speech')]
SERVICES = [('MCP tools', 'calendar, CRM'), ('Pinecone', 'RAG retrieval'), ('PostgreSQL', 'state, history'),
            ('Langfuse', 'traces')]

SEP = '  ·  '


def hero(mobile):
    if not mobile:
        w, x, s = 1080, 36, 15
        y = BAR_H + 42
        out = [prompt(x, y, 'whoami', s)]
        y += 50
        out.append(text(x, y, NAME, 38, TEXT, 700))
        y += 34
        out.append(text(x, y, ROLE, 19, TEXT))
        y += 28
        out.append(text(x, y, SUMMARY, s, MUTED))
        y += 46
        out.append(prompt(x, y, 'cat focus.txt', s))
        for key, desc in FOCUS:
            y += 30
            out.append(text(x + 18, y, key, s, BLUE))
            out.append(text(x + 210, y, desc, s, TEXT))
        y += 44
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
        for line in wrap(SUMMARY, 52):
            y += 20
            out.append(text(x, y, line, s, MUTED))
        y += 36
        out.append(prompt(x, y, 'cat focus.txt', s))
        for key, desc in FOCUS:
            y += 26
            out.append(text(x + 12, y, key, s, BLUE))
            for line in wrap(desc, 50):
                y += 19
                out.append(text(x + 28, y, line, s, TEXT))
        y += 36
        out.append(prompt(x, y, '', s, cursor=True))
        h = y + 24
    label = f'{NAME}, {ROLE}. {SUMMARY} Focus: ' + '; '.join(f'{k}: {d}' for k, d in FOCUS) + '.'
    return frame(w, h, 'raj@dev: ~', '\n'.join(out), label)


def node(x, y, w, h, title, sub, size):
    return '\n'.join([
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="#161b22" stroke="{BORDER}"/>',
        text(f'{x + w / 2:.1f}', f'{y + h / 2 - 3:.1f}', title, size, TEXT, 600, 'middle'),
        text(f'{x + w / 2:.1f}', f'{y + h / 2 + size + 1:.1f}', sub, size - 2.5, MUTED, None, 'middle'),
    ])


def arrow(x1, y1, x2, y2):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{DIM}" stroke-width="1.4" '
            f'marker-end="url(#ah)"/>')


def line(points):
    pts = ' '.join(f'{x:.1f},{y:.1f}' for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{DIM}" stroke-width="1.4"/>'


MARKER = (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
          f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{DIM}"/></marker></defs>')


def architecture(mobile):
    out = [MARKER]
    if not mobile:
        w, x0 = 1080, 36
        y = BAR_H + 42
        out.append(prompt(x0, y, 'cat architecture/voice-agent.txt', 15))
        out.append(text(x0, y + 28, '# real-time voice agent: call audio in, agent reasoning, speech out', 13.5, DIM))
        n, gap, nh = len(PIPELINE), 30, 62
        nw = (w - 2 * x0 - gap * (n - 1)) / n
        ny = y + 82
        xs = [x0 + i * (nw + gap) for i in range(n)]
        for (t, s), x in zip(PIPELINE, xs):
            out.append(node(x, ny, nw, nh, t, s, 14.5))
        for i in range(n - 1):
            out.append(arrow(xs[i] + nw + 2, ny + nh / 2, xs[i + 1] - 2, ny + nh / 2))
        # return audio: TTS back into the LiveKit room
        top = ny - 22
        out.append(line([(xs[5] + nw / 2, ny - 2), (xs[5] + nw / 2, top), (xs[2] + nw / 2, top)]))
        out.append(arrow(xs[2] + nw / 2, top, xs[2] + nw / 2, ny - 2))
        out.append(text((xs[2] + xs[5] + nw) / 2, top - 7, 'synthesized audio back to caller', 12, MUTED, None, 'middle'))
        # services bus under the LLM agent
        llm_cx = xs[4] + nw / 2
        sy = ny + nh + 66
        m, sgap = len(SERVICES), 30
        sw = nw
        span = m * sw + (m - 1) * sgap
        sx0 = w - x0 - span
        sxs = [sx0 + i * (sw + sgap) for i in range(m)]
        bus = ny + nh + 33
        out.append(line([(llm_cx, ny + nh + 2), (llm_cx, bus)]))
        out.append(line([(sxs[0] + sw / 2, bus), (sxs[-1] + sw / 2, bus)]))
        for (t, s), sx in zip(SERVICES, sxs):
            out.append(arrow(sx + sw / 2, bus, sx + sw / 2, sy - 2))
            out.append(node(sx, sy, sw, nh, t, s, 14.5))
        out.append(text(x0, sy + 22, 'agent tools and services', 13.5, DIM))
        out.append(text(x0, sy + 42, 'called per turn, traced end to end', 13.5, DIM))
        h = sy + nh + 34
    else:
        w, x0 = 440, 20
        y = BAR_H + 32
        out.append(prompt(x0, y, 'cat architecture/voice-agent.txt', 12.5))
        out.append(text(x0, y + 22, '# call audio in, agent reasoning, speech out', 11.5, DIM))
        nw, nh, gap = 250, 46, 22
        nx = (w - nw) / 2 - 40
        ny = y + 46
        ys = []
        for i, (t, s) in enumerate(PIPELINE):
            yy = ny + i * (nh + gap)
            ys.append(yy)
            out.append(node(nx, yy, nw, nh, t, s, 13))
            if i:
                out.append(arrow(nx + nw / 2, yy - gap + 2, nx + nw / 2, yy - 2))
        # return path on the right side from TTS back to LiveKit
        rx = nx + nw + 22
        out.append(line([(nx + nw + 2, ys[5] + nh / 2), (rx, ys[5] + nh / 2), (rx, ys[2] + nh / 2)]))
        out.append(arrow(rx, ys[2] + nh / 2, nx + nw + 2, ys[2] + nh / 2))
        out.append(text(rx + 8, (ys[2] + ys[5] + nh) / 2, 'audio', 11, MUTED))
        out.append(text(rx + 8, (ys[2] + ys[5] + nh) / 2 + 15, 'out', 11, MUTED))
        sy = ys[-1] + nh + 40
        out.append(text(x0, sy, '# tools called by the LLM agent', 11.5, DIM))
        sw, sh = (w - 2 * x0 - 12) / 2, 44
        for i, (t, s) in enumerate(SERVICES):
            sx = x0 + (i % 2) * (sw + 12)
            yy = sy + 14 + (i // 2) * (sh + 12)
            out.append(node(sx, yy, sw, sh, t, s, 12.5))
        h = sy + 14 + 2 * (sh + 12) + 14
    label = ('Voice agent architecture: ' + ' to '.join(t for t, _ in PIPELINE) +
             ', with synthesized audio returned to the caller. The LLM agent calls ' +
             ', '.join(f'{t} ({s})' for t, s in SERVICES) + '.')
    return frame(w, h, 'architecture', '\n'.join(out), label)


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
    for name, fn in [('intro', hero), ('architecture', architecture), ('stack', stack)]:
        Path(f'assets/{name}.svg').write_text(fn(False), encoding='utf-8', newline='\n')
        Path(f'assets/{name}-mobile.svg').write_text(fn(True), encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
