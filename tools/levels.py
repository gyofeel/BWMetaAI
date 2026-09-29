"""Compile-time difficulty levels for BWMetaAI-aise.

`if_level(n):` keeps its indented body only when the build level is >= n.
`{lv.key}` is replaced with config["aise"][key]; a missing key fails the build.
"""
import re

IF_LEVEL = re.compile(r'^( *)if_level\((\d+)\):\s*$')
KEY = re.compile(r'\{lv\.(\w+)\}')


def _blocks(lines, level):
    out = []
    i = 0
    while i < len(lines):
        m = IF_LEVEL.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        indent = len(m.group(1))
        body = []
        i += 1
        while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip(' ')) > indent):
            body.append(lines[i])
            i += 1
        if level >= int(m.group(2)):
            out += _blocks([l[:indent] + l[indent + 4:] if l.strip() else l for l in body], level)
    return out


def apply(content, cfg):
    if 'if_level(' not in content and '{lv.' not in content:
        return content
    if not cfg:
        raise SystemExit('aise markers found but config has no "aise" section')
    text = '\n'.join(_blocks(content.split('\n'), cfg['level']))

    def value(m):
        if m.group(1) not in cfg:
            raise SystemExit(f'missing config key aise.{m.group(1)}')
        return str(cfg[m.group(1)])

    return KEY.sub(value, text)
