#!/bin/sh
# A1: upstream source must compile to the same AI with legacy PyAI and the PyMS aise fork.
set -e
PYMS=${PYMS:-../pyms-aise}
PYMS_PY=${PYMS_PY:-$PYMS/.venv/bin/python}
OUT=build/a1
mkdir -p $OUT
rm -f build/*.pyai
make build/combined.pyai
python3.11 tools/PyAI.pyw --compile --hidewarns ../build/combined.pyai ../$OUT/legacy.bin ../$OUT/legacy_bw.bin
python3 tools/pyms_compat.py build/combined.pyai $OUT/fork.pyai
PYTHONPATH=$PYMS $PYMS_PY tools/pyms_compile.py $OUT/fork.pyai $OUT/fork.bin $OUT/fork_bw.bin
if cmp -s $OUT/legacy.bin $OUT/fork.bin; then
    echo "A1 PASS: byte-identical"
    exit 0
fi
$PYMS_PY $PYMS/PyAI.pyw --decompile $OUT/legacy.bin $OUT/legacy_bw.bin $OUT/legacy.txt
$PYMS_PY $PYMS/PyAI.pyw --decompile $OUT/fork.bin $OUT/legacy_bw.bin $OUT/fork.txt
if diff -q $OUT/legacy.txt $OUT/fork.txt >/dev/null; then
    echo "A1 PASS: same decompiled flow (bytes differ)"
else
    echo "A1 FAIL: diff $OUT/legacy.txt $OUT/fork.txt"
    exit 1
fi
