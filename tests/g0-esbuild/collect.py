"""Portable static callsite inventory; inspect verified bytes, never execute vendor code."""
from pathlib import Path
import json
import re

out = Path('evidence/g0-esbuild')
rows = []
for p in sorted((out/'baseline-files').rglob('*')):
    if p.is_file() and p.suffix in {'.js', '.cjs', '.json'}:
        for number, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
            if re.search(r'\besbuild\b|\bbuildSync\b|\btransformSync\b|\.serve\(', line):
                rows.append({'path': str(p.relative_to(out/'baseline-files')), 'line': number, 'source': line})
assert any('import { build } from "esbuild"' in x['source'] for x in rows)
(out/'esbuild-callsites.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
