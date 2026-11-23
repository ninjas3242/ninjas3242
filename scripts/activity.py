"""Render the profile activity strip from GitHub's contribution calendar JSON."""
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

from terminal import BAR_H, BLUE, BORDER, DIM, GREEN, TEXT, frame, prompt, text


def render_strip(width, height, weekly, metrics, period):
    compact = width < 600
    x = 20 if compact else 36
    size = 12.5 if compact else 15
    y = BAR_H + (32 if compact else 42)
    out = [prompt(x, y, 'gh contributions --last 365d', size),
           text(x, y + (20 if compact else 26), f'# {period}', size - 1, DIM)]
    column = (width - 2 * x) / 3
    fig_y = y + (68 if compact else 88)
    for n, (name, value) in enumerate(metrics):
        fx = x + column * n
        out.append(text(fx, fig_y, f'{value:,}', 28 if compact else 44, TEXT, 700))
        out.append(text(fx, fig_y + (20 if compact else 28), name.lower().replace(' ', '_'), size, BLUE))
    chart_top = fig_y + (44 if compact else 62)
    base_y = height - (18 if compact else 26)
    slot = (width - 2 * x) / len(weekly)
    peak = max(weekly) or 1
    for n, count in enumerate(weekly):
        h = max(2, (base_y - chart_top) * count / peak)
        color = GREEN if count else BORDER
        opacity = 1 if count == peak else .55 + .4 * count / peak if count else 1
        out.append(f'<rect x="{x+n*slot:.1f}" y="{base_y-h:.1f}" width="{slot*.7:.1f}" height="{h:.1f}" rx="1" '
                   f'fill="{color}" opacity="{opacity:.2f}"><title>{count} contributions</title></rect>')
    label = f'GitHub contributions, {period}: ' + ', '.join(f'{v:,} {k.lower()}' for k, v in metrics) + '.'
    return frame(width, height, 'activity', chr(10).join(out), label)


def main():
    calendar = json.load(sys.stdin)['data']['user']['contributionsCollection']['contributionCalendar']
    days = sorted((date.fromisoformat(day['date']), day['contributionCount'])
                  for week in calendar['weeks'] for day in week['contributionDays'])
    end = days[-1][0]
    start = end - timedelta(days=364)
    days = [(day, count) for day, count in days if start <= day <= end]
    if len({day for day, _ in days}) != 365:
        raise ValueError('Expected a complete 365-day calendar')
    weekly = defaultdict(int)
    for day, count in days:
        weekly[day - timedelta(days=(day.weekday()+1) % 7)] += count
    metrics = [('Contributions', sum(count for _, count in days)),
               ('Active weeks', sum(count > 0 for count in weekly.values())),
               ('Best day', max(count for _, count in days))]
    period = f'{start:%d %b %Y} – {end:%d %b %Y}'
    for name, width, height in [('activity', 1080, 340), ('activity-mobile', 440, 280)]:
        Path(f'assets/{name}.svg').write_text(render_strip(width, height, list(weekly.values()), metrics, period), encoding='utf-8', newline='\n')
    alt = f'GitHub activity from {period}. {metrics[0][1]:,} contributions across {metrics[1][1]} active weeks. Busiest day: {metrics[2][1]} contributions.'
    block = f'''<!-- activity:start -->
<picture>
  <source media="(max-width: 600px)" srcset="assets/activity-mobile.svg">
  <img src="assets/activity.svg" width="100%" alt="{alt}">
</picture>
<!-- activity:end -->'''
    readme_path = Path('README.md')
    readme = readme_path.read_text(encoding='utf-8')
    head, sep, rest = readme.partition('<!-- activity:start -->')
    _, sep2, tail = rest.partition('<!-- activity:end -->')
    if not (sep and sep2):
        raise ValueError('README.md is missing the activity markers')
    readme_path.write_text(head + block + tail, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
