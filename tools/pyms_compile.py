#!/usr/bin/env python3
"""Compile PyMS-fork AI source to aiscript.bin/bwscript.bin.

The fork's `PyAI.pyw --compile` at 58e4c25 drops the compiled scripts before
saving (writes an empty 8 byte file), so this does what its GUI does instead.
Run with the fork's python: PYTHONPATH=../pyms-aise ../pyms-aise/.venv/bin/python
"""
import os
import sys

from PyMS.FileFormats import DAT, TBL
from PyMS.FileFormats.AIBIN import AIBIN
from PyMS.FileFormats.AIBIN.CodeHandlers.AILexer import AILexer
from PyMS.FileFormats.AIBIN.CodeHandlers.AIParseContext import AIParseContext, AIParseSettings
from PyMS.FileFormats.AIBIN.CodeHandlers.DataContext import DataContext
from PyMS.Utilities import Assets
from PyMS.Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from PyMS.Utilities.PyMSError import PyMSError


def data_context():
    tbl = TBL.TBL()
    tbl.load(Assets.mpq_file_path('rez', 'stat_txt.tbl'))
    units = DAT.UnitsDAT()
    units.load(Assets.mpq_file_path('arr', 'units.dat'))
    upgrades = DAT.UpgradesDAT()
    upgrades.load(Assets.mpq_file_path('arr', 'upgrades.dat'))
    techs = DAT.TechDAT()
    techs.load(Assets.mpq_file_path('arr', 'techdata.dat'))
    return DataContext(stattxt_tbl=tbl, units_dat=units, upgrades_dat=upgrades, techdata_dat=techs)


def main(source, ai_out, bw_out):
    with open(source, encoding='utf-8') as f:
        code = f.read()
    parse_context = AIParseContext(AILexer(code), AIParseSettings(), DefinitionsHandler(), data_context())
    try:
        scripts = AIBIN.AIBIN.compile(parse_context)
    except PyMSError as e:
        sys.exit(repr(e))
    aibin = AIBIN.AIBIN()
    if any(aibin.can_add_scripts(scripts)):
        aibin.expand()
    aibin.active_plugins.update(parse_context.language_context.active_plugins())
    aibin.add_scripts(scripts)
    aibin.save(ai_out, bw_out)
    if not os.path.exists(bw_out):
        # Fork skips an empty bwscript.bin; its own decompiler still wants one.
        with open(bw_out, 'wb') as f:
            f.write(b'\x04\x00\x00\x00\x00\x00\x00\x00')
    print(f'{source} -> {ai_out} ({len(scripts)} scripts, expanded={aibin.expanded})')


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(f'Usage: {sys.argv[0]} source.pyai aiscript.bin bwscript.bin')
    main(*sys.argv[1:])
