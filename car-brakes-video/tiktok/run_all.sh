#!/bin/bash
cd "$(dirname "$0")"
for e in episodes/ep0[2-8]*.py; do python3 render.py full "$e" 2>&1 | tail -1; done
echo ALL_DONE
