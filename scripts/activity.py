"""Render the profile activity strip from GitHub's contribution calendar JSON."""
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


def render_strip(width, height, weekly, metrics, period):
    compact = width < 600
    margin = 18 if compact else 38
    column = (width - 2 * margin) / 3
    number_size = 37 if compact else 58
    label_size = 13 if compact else 21
    figure_y = 92 if compact else 130
    chart_y = figure_y + (65 if compact else 83)
    base_y = height - 15
    bars = []
    slot = (width - 2 * margin) / len(weekly)
    peak = max(weekly) or 1
    for n, count in enumerate(weekly):
        h = max(2, (base_y - chart_y) * count / peak)
        color = '#e96b33' if count == peak else '#23635c' if count else '#d9e2d8'
        bars.append(f'<rect x="{margin+n*slot:.1f}" y="{base_y-h:.1f}" width="{slot*.72:.1f}" height="{h:.1f}" rx="1" fill="{color}"><title>{count} contributions</title></rect>')
    figures = []
    for n, (name, value) in enumerate(metrics):
        x = margin + column*n
        figures.append(f'<text x="{x}" y="{figure_y}" font-size="{number_size}" font-weight="700" letter-spacing="-1.6">{value:,}</text>')
        figures.append(f'<text x="{x}" y="{figure_y+label_size+8}" font-size="{label_size}">{name}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">
<title>GitHub activity · {period}</title>
<rect width="100%" height="100%" rx="13" fill="#f5f7ec"/>
<g font-family="system-ui, sans-serif" fill="#173e36">
<text x="{margin}" y="{30 if compact else 44}" font-size="{14 if compact else 22}" font-weight="600">GitHub activity</text>
<text x="{width-margin}" y="{30 if compact else 44}" text-anchor="end" font-size="{11 if compact else 17}">{period}</text>
{chr(10).join(figures)}
<text x="{margin}" y="{chart_y-5}" font-size="{10 if compact else 15}" fill="#45675e">Contributions by week</text>
</g>
{chr(10).join(bars)}
</svg>
'''


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
    for name, width, height in [('activity', 1080, 280), ('activity-mobile', 440, 209)]:
        Path(f'assets/{name}.svg').write_text(render_strip(width, height, list(weekly.values()), metrics, period), encoding='utf-8')
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
    readme_path.write_text(head + block + tail, encoding='utf-8')


if __name__ == '__main__':
    main()
