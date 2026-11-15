#!/usr/bin/env python3
"""Create new planned task journal from template. No git operations."""
from pathlib import Path
import argparse
import re

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('id', help='e.g. EDU-0005')
    ap.add_argument('--title',required=True)
    ap.add_argument('--phase',default='00')
    args=ap.parse_args()
    if not re.fullmatch(r'EDU-\d{4}',args.id):raise SystemExit('Use EDU-XXXX')
    path=ROOT/'docs/progress/tasks'/f'{args.id}.md'
    if path.exists():raise SystemExit('Task exists, refusing overwrite')
    from datetime import datetime,timezone
    stamp=datetime.now(timezone.utc).date().isoformat()
    content=(ROOT/'docs/progress/TASK_TEMPLATE.md').read_text(encoding='utf-8')
    content=content.replace('EDU-XXXX',args.id).replace('YYYY-MM-DD',stamp).replace('Task title',args.title).replace('module: module-owner',f'module: phase-{args.phase}')
    path.write_text(content,encoding='utf-8')
    print(path.relative_to(ROOT))
if __name__=='__main__':main()
