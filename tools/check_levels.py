#!/usr/bin/env python3
"""A3 and source lint for BWMetaAI-aise. Run from the repo root after `make aise`.

check_levels(): expected aise commands per level in build/lvN/decompiled.txt.
lint_sources(): text that macros.py, race.py or the PyMS fork would mangle,
and aise code reachable outside PvT.
"""
import glob
import os
import re
import sys

# regex -> expected match count for (Lv1, Lv2, Lv3)
EXPECT = {
    r'idle_orders\W+PsiStorm': (1, 1, 1),
    r'idle_orders\W+StasisField': (0, 1, 1),
    r'idle_orders\W+AttackUnit': (0, 1, 1),
    r'idle_orders\W+Move': (0, 0, 1),
    r'max_workers': (1, 1, 1),
    r'wait_rand': (5, 6, 6),
    r'ai_order\W+AttackUnit': (1, 2, 3),
}

AISE_CMD = re.compile(r'\b(idle_orders|ai_order|wait_rand|max_workers|print)\(|\{lv\.')
PVT_GATE = 'if enemyowns(Command Center):'


def check_levels():
    errors = []
    for i, level in enumerate((1, 2, 3)):
        with open(f'build/lv{level}/decompiled.txt', encoding='utf-8') as f:
            text = f.read()
        if not re.search(rf'BWMetaAI-aise PvT Lv{level}\b', text):
            errors.append(f'lv{level}: start message missing')
        with open(f'build/lv{level}/protoss.pyai', encoding='utf-8') as f:
            protoss = f.read()
        hook, builds = protoss.find('multirun(gen_aise_manager)'), protoss.find('--gen_builds--')
        if not 0 <= hook < builds:
            errors.append(f'lv{level}: aise manager must start before the build order')
        for pattern, counts in EXPECT.items():
            found = len(re.findall(pattern, text))
            if found != counts[i]:
                errors.append(f'lv{level}: {pattern} found {found}, expected {counts[i]}')
    return errors


def lint_sources(root='src/protoss'):
    errors = []
    for path in sorted(glob.glob(os.path.join(root, '**', '*.pyai'), recursive=True)):
        with open(path, encoding='utf-8') as f:
            lines = f.read().split('\n')
        in_aise_dir = os.sep + 'aise' + os.sep in path
        if not in_aise_dir and not any(AISE_CMD.search(l) for l in lines):
            continue
        pvt_file = lines[0].strip() == 'use_build_vs(Terran)'
        gated = False
        prev = ''
        for n, line in enumerate(lines, 1):
            code = line.strip()
            where = f'{path}:{n}'
            if code.startswith('#'):
                if ':' in code or re.search(r'if .*\(.*\)', code):
                    errors.append(f'{where}: ":" or "if x(...)" in a comment breaks macros.py')
                continue
            if code.startswith('--aise_'):
                gated = True
            if in_aise_dir:
                if any(word in code for word in ('Gas', 'Peon', 'Town Hall')):
                    errors.append(f'{where}: race.py rewrites Gas/Peon/Town Hall')
                for m in re.finditer(r'print\((.*)\)', code):
                    if re.search(r'[,()]', m.group(1)):
                        errors.append(f'{where}: "," or parens in print text are cut by the PyMS fork')
            elif AISE_CMD.search(code) and not (pvt_file or gated or prev == PVT_GATE):
                errors.append(f'{where}: aise code outside a PvT-only path')
            if code:
                prev = code
    return errors


if __name__ == '__main__':
    errors = lint_sources() + check_levels()
    for error in errors:
        print('FAIL', error)
    print(f'check_levels: {len(errors)} problem(s)' if errors else 'check_levels: OK')
    sys.exit(1 if errors else 0)
