"""Shared terminal-window styling for the profile SVG panels."""
from html import escape

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
BG = '#0d1117'
BAR = '#161b22'
BORDER = '#30363d'
TEXT = '#e6edf3'
MUTED = '#8b949e'
DIM = '#6e7681'
GREEN = '#3fb950'
BLUE = '#79c0ff'
BAR_H = 34


def esc(s):
    return escape(str(s), quote=True)


def frame(width, height, title, body, label):
    """Wrap SVG body content in a terminal window of the given size."""
    dots = ''.join(f'<circle cx="{20 + i * 18}" cy="{BAR_H / 2}" r="5.5" fill="{BORDER}"/>' for i in range(3))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<defs><clipPath id="win"><rect width="{width}" height="{height}" rx="10"/></clipPath></defs>
<g clip-path="url(#win)">
<rect width="{width}" height="{height}" fill="{BG}"/>
<rect width="{width}" height="{BAR_H}" fill="{BAR}"/>
<line x1="0" y1="{BAR_H}" x2="{width}" y2="{BAR_H}" stroke="{BORDER}"/>
</g>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="10" fill="none" stroke="{BORDER}"/>
{dots}
<text x="{width / 2}" y="{BAR_H / 2 + 4.5}" text-anchor="middle" font-family="{FONT}" font-size="12.5" fill="{MUTED}">{esc(title)}</text>
<g font-family="{FONT}">
{body}
</g>
</svg>
'''


def prompt(x, y, command, size=15, cursor=False):
    """A shell prompt line: raj@dev:~$ command"""
    cw = size * 0.6
    parts = [
        f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve">'
        f'<tspan fill="{GREEN}">raj@dev</tspan><tspan fill="{MUTED}">:</tspan>'
        f'<tspan fill="{BLUE}">~</tspan><tspan fill="{MUTED}">$ </tspan>'
        f'<tspan fill="{TEXT}">{esc(command)}</tspan></text>'
    ]
    if cursor:
        cx = x + cw * (len('raj@dev:~$ ') + len(command))
        parts.append(f'<rect x="{cx:.1f}" y="{y - size * 0.8:.1f}" width="{cw:.1f}" height="{size:.1f}" fill="{MUTED}" opacity=".85"/>')
    return '\n'.join(parts)


def text(x, y, s, size=15, fill=TEXT, weight=None, anchor=None):
    w = f' font-weight="{weight}"' if weight else ''
    a = f' text-anchor="{anchor}"' if anchor else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{w}{a} xml:space="preserve">{esc(s)}</text>'


def wrap(s, width):
    words, lines, line = s.split(' '), [], ''
    for w in words:
        if line and len(line) + 1 + len(w) > width:
            lines.append(line)
            line = w
        else:
            line = f'{line} {w}' if line else w
    if line:
        lines.append(line)
    return lines
