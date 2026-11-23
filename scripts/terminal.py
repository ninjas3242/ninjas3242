"""Shared terminal-window styling for the profile SVG panels (light and dark themes)."""
from html import escape

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
BAR_H = 34

THEMES = {
    'dark': dict(bg='#0d1117', bar='#161b22', border='#30363d', chip='#161b22', text='#e6edf3',
                 muted='#8b949e', dim='#6e7681', green='#3fb950', blue='#79c0ff',
                 ramp=['#0e4429', '#006d32', '#26a641', '#39d353']),
    'light': dict(bg='#ffffff', bar='#f6f8fa', border='#d0d7de', chip='#f6f8fa', text='#1f2328',
                  muted='#59636e', dim='#818b98', green='#1a7f37', blue='#0969da',
                  ramp=['#9be9a8', '#40c463', '#30a14e', '#216e39']),
}


def esc(s):
    return escape(str(s), quote=True)


def frame(t, width, height, title, body, label):
    """Wrap SVG body content in a terminal window."""
    dots = ''.join(f'<circle cx="{20 + i * 18}" cy="{BAR_H / 2}" r="5.5" fill="{t["border"]}"/>' for i in range(3))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<defs><clipPath id="win"><rect width="{width}" height="{height}" rx="10"/></clipPath></defs>
<g clip-path="url(#win)">
<rect width="{width}" height="{height}" fill="{t["bg"]}"/>
<rect width="{width}" height="{BAR_H}" fill="{t["bar"]}"/>
<line x1="0" y1="{BAR_H}" x2="{width}" y2="{BAR_H}" stroke="{t["border"]}"/>
</g>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="10" fill="none" stroke="{t["border"]}"/>
{dots}
<text x="{width / 2}" y="{BAR_H / 2 + 4.5}" text-anchor="middle" font-family="{FONT}" font-size="12.5" fill="{t["muted"]}">{esc(title)}</text>
<g font-family="{FONT}">
{body}
</g>
</svg>
'''


def prompt(t, x, y, command, size=15, cursor=False):
    """A shell prompt line: raj@dev:~$ command"""
    cw = size * 0.6
    parts = [
        f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve">'
        f'<tspan fill="{t["green"]}">raj@dev</tspan><tspan fill="{t["muted"]}">:</tspan>'
        f'<tspan fill="{t["blue"]}">~</tspan><tspan fill="{t["muted"]}">$ </tspan>'
        f'<tspan fill="{t["text"]}">{esc(command)}</tspan></text>'
    ]
    if cursor:
        cx = x + cw * (len('raj@dev:~$ ') + len(command))
        parts.append(f'<rect x="{cx:.1f}" y="{y - size * 0.8:.1f}" width="{cw:.1f}" height="{size:.1f}" '
                     f'fill="{t["muted"]}" opacity=".85"/>')
    return '\n'.join(parts)


def text(x, y, s, size, fill, weight=None, anchor=None):
    w = f' font-weight="{weight}"' if weight else ''
    a = f' text-anchor="{anchor}"' if anchor else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{w}{a} xml:space="preserve">{esc(s)}</text>'


def spans(x, y, size, parts):
    """One text line made of (string, colour) parts."""
    inner = ''.join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in parts)
    return f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve">{inner}</text>'


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
