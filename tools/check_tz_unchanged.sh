#!/bin/sh
# A5: terran/zerg preprocessor output must match upstream 81367cf (build timestamp masked).
set -e
REF=build/ref
rm -rf $REF && mkdir -p $REF
git archive 81367cf | tar -x -C $REF
mask() { sed 's/BWMetaAI github.com\/jncraton\/BWMetaAI .*)$/BWMetaAI MASKED)/' "$1"; }
status=0
for lv in 1 2 3; do
    cp tools/config_lv$lv.json $REF/tools/config.json
    for race in terran zerg; do
        (cd $REF && python3 tools/build_ai.py $race ref_$race.pyai)
        mask $REF/ref_$race.pyai > $REF/old.pyai
        mask build/lv$lv/$race.pyai > $REF/new.pyai
        if cmp -s $REF/old.pyai $REF/new.pyai; then
            echo "A5 lv$lv $race OK"
        else
            echo "A5 lv$lv $race DIFF"
            diff $REF/old.pyai $REF/new.pyai | head -20
            status=1
        fi
    done
done
exit $status
