#!/bin/bash
cd "$(dirname "$0")"
for e in ep01_brakes ep02_air_filter ep03_cabin_filter ep04_oil_change ep05_intake ep06_spark_plugs ep07_battery ep08_wipers; do
  (cd $e && npx hyperframes render --quality looks --output ../out/$e.mp4 2>&1 | grep -E "complete|MB ·|✗" | tr '\n' ' '); echo " <- $e"
done
echo ALL_RENDERED
