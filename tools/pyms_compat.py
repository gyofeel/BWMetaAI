#!/usr/bin/env python3
"""Convert BWMetaAI's legacy PyAI source into neivv/PyMS (aise fork) syntax.

- `XXXX(1342, 101, aiscript):` headers become `script XXXX { ... }` blocks
  followed by an entry label.
- Block labels are global in the fork, so each script's labels get a
  per-script prefix (`s0_`, `s1_`, ...).
- '-' and '+' are not valid in fork identifiers, so labels use '_' instead.
- Unit names the fork does not know (it wants full stat_txt names) become unit ids.
- Arguments with an apostrophe are double-quoted, or the fork reads them as a string start.
"""
import re
import sys

HEADER = re.compile(r'^(\S{4})\((\d+), ([01]{3}), (aiscript|bwscript)\):\s*$')
LABEL = re.compile(r'^\s*--([\w+][\w+-]*)--\s*$')
WORD = re.compile(r'[\w+](?:[\w+-]*\w)?')
LEGACY_UNIT = re.compile(r'(?<=[(,])\s*Terran Siege Tank\s*(?=[,)])')
APOSTROPHE_ARG = re.compile(r'(?<=[(,])\s*([^,()"]*\'[^,()"]*?)\s*(?=[,)])')


def header(script_id, string_id, flags, bin_file, entry):
    value = int(flags, 2)
    return [
        f'script {script_id} {{',
        f'    name_string {string_id}',
        f'    bin_file {bin_file}',
        f'    broodwar_only {value >> 2 & 1}',
        f'    staredit_hidden {value >> 1 & 1}',
        f'    requires_location {value & 1}',
        f'    entry_point {entry}',
        '}',
        f'--{entry}--',
    ]


def convert(src):
    out = []
    sections = []
    for line in src.split('\n'):
        m = HEADER.match(line)
        if m:
            sections.append((m, []))
        elif sections:
            sections[-1][1].append(line)
        else:
            out.append(line)
    for index, (m, body) in enumerate(sections):
        prefix = f's{index}_'
        labels = {LABEL.match(l).group(1) for l in body if LABEL.match(l)}

        def rename(word):
            name = word.group(0)
            return prefix + re.sub(r'[+-]', '_', name) if name in labels else name

        out += header(*m.groups(), prefix + 'entry')
        ended = False
        dead = 0
        for line in body:
            code = line.strip()
            if not code or code.startswith('#'):
                out.append(line)
                continue
            # Legacy macros leave unreachable code after goto/stop; the fork
            # only accepts commands inside a labelled block.
            if ended and not LABEL.match(line):
                dead += 1
                out.append(f'--{prefix}dead_{dead}--')
            line = LEGACY_UNIT.sub(' 5', WORD.sub(rename, line))
            out.append(APOSTROPHE_ARG.sub(r' "\1"', line))
            ended = code.startswith(('goto(', 'stop('))
    return '\n'.join(out)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(f'Usage: python3 {sys.argv[0]} legacy.pyai out.pyai')
    with open(sys.argv[1], encoding='utf-8') as f:
        src = f.read()
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        f.write(convert(src))
