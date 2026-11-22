"""Stage the webpage and public-source fund data for GitHub Pages."""
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent
output = root / 'public'
output.mkdir(exist_ok=True)
for name in ('index.html', 'data.json'):
    shutil.copyfile(root / name, output / name)
(output / 'robots.txt').write_text('User-agent: *\nDisallow: /\n', encoding='utf-8')
(output / '_headers').write_text('/*\n  X-Robots-Tag: noindex, nofollow, noarchive\n  X-Content-Type-Options: nosniff\n', encoding='utf-8')
print('Website staged in public/ for GitHub Pages deployment.')
