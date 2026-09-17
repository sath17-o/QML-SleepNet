#!/usr/bin/env bash
set -euo pipefail
python scripts/run_pipeline.py --mode methodology-replay "$@"
