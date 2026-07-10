#!/usr/bin/env bash
set -euo pipefail

cd /root/autodl-tmp/research-workflow-kit
source .venv/bin/activate

python -m pip install -r configs/requirements-exp108-autodl.txt
python scripts/check_experiment_contract.py \
  --experiment-id EXP-108-standard-baselines \
  --config configs/experiment/EXP-108-standard-baselines.yaml \
  --smoke-config configs/smoke/EXP-108-standard-baselines-smoke.yaml \
  --output outputs/EXP-108-standard-baselines \
  --warn-only

python scripts/run_exp108_standard_baselines.py \
  --config configs/smoke/EXP-108-standard-baselines-smoke.yaml \
  --out outputs/EXP-108-standard-baselines-smoke

for seed in 42 2026 3407; do
  python scripts/run_exp108_standard_baselines.py \
    --config configs/experiment/EXP-108-standard-baselines.yaml \
    --seed "${seed}" \
    --methods persistence,lightgbm,gru,stgcn \
    --out "outputs/EXP-108-standard-baselines/seed-${seed}" \
    2>&1 | tee "outputs/EXP-108-standard-baselines/seed-${seed}.log"
done
