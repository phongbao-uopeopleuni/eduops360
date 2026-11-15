#!/usr/bin/env python3
"""Validate EduOps 360 governance structure (stdlib only; no code execution from zip)."""
from pathlib import Path
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
IGNORE_DIRS = {'.git', 'node_modules', '.venv', 'venv', 'dist', 'build', '__pycache__',
               '.pytest_cache', '.ruff_cache', '.local', 'test-results', 'playwright-report'}
GROUPS = ('giam-sat','graphify','kiem-thu','lap-ke-hoach','ra-soat','thuc-thi','trien-khai')
REQUIRED = ('AGENTS.md','CLAUDE.md','docs/requirements/SRS_MASTER.md','docs/roles/README.md',
            'docs/architecture/TECHNICAL_ARCHITECTURE.md','docs/quality/TRACEABILITY_MATRIX.md',
            'docs/phases/PHASE-00.md',
            'docs/quality/PHASE_00_ACCEPTANCE.md','docs/decisions/ADR-0001-single-school-extensible.md',
            'ai-agent-sp/skills/REGISTRY.md','docs/phases/README.md')


def validate(root=ROOT):
    errors=[]
    for name in REQUIRED:
        if not (root/name).is_file(): errors.append('missing '+name)
    for n in range(12):
        p=root/f'docs/phases/PHASE-{n:02d}.md'
        if not p.is_file(): errors.append('missing '+str(p.relative_to(root)))
        else:
            t=p.read_text(encoding='utf-8')
            for required in ('## C. Detailed execution steps','## E. Verification and exit gate'):
                if required not in t:errors.append('missing section in '+str(p.relative_to(root))+': '+required)
    for stale in (root/'ai-agent-sp/skills').glob('*/SKILL.md'):
        errors.append('legacy flat skill causes source-of-truth mismatch: '+str(stale.relative_to(root)))
    count=0
    for group in GROUPS:
        folder=root/'ai-agent-sp/skills'/group
        if not folder.is_dir(): errors.append('missing skill group '+group);continue
        files=list(folder.glob('*/SKILL.md'))
        if not files: errors.append('empty skill group '+group)
        for f in files:
            count+=1
            content=f.read_text(encoding='utf-8')
            matched=re.match(r'\A---\n(.*?)\n---\n',content,re.S)
            if not matched:errors.append('missing frontmatter '+str(f));continue
            front=matched.group(1)
            for key in ('name','description'):
                if not re.search(rf'(?m)^{key}:\s*\S',front):errors.append('missing '+key+' '+str(f))
            if f.parent.name not in front:errors.append('name mismatch '+str(f))
            if '## Execution procedure' not in content:errors.append('no execution procedure '+str(f))
    count_roles=len(list((root/'docs/roles').glob('*.md')))-1
    if count_roles<10:errors.append('insufficient role files')
    entrypath=root/'AGENTS.md'
    if entrypath.is_file():
        entry=entrypath.read_text(encoding='utf-8')
        if 'ai-agent-sp/skills/REGISTRY.md' not in entry:
            errors.append('AGENTS.md fails to route skill registry')
    for directory, folders, filenames in os.walk(root):
        folders[:] = [name for name in folders if name not in IGNORE_DIRS and not name.endswith('.egg-info')]
        for filename in filenames:
            file = Path(directory) / filename
            if file.suffix in {'.md','.py','.json','.yml','.yaml','.txt','.ts','.tsx','.css','.html'}:
                try:file.read_text(encoding='utf-8')
                except UnicodeError:errors.append('invalid UTF-8 '+str(file.relative_to(root)))
    return count,count_roles,errors

if __name__ == '__main__':
    count,roles,errors=validate()
    print(f'Blueprint: 12 phases, {count} skills, {roles} role cards')
    if errors:
        for err in errors: print('ERROR:',err)
        sys.exit(1)
    print('PASS: all required blueprint checks')
