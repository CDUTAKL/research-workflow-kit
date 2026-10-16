# Experiment Protocol Freeze And Test Access

For each confirmatory experiment, complete the `Frozen Protocol Record` in `docs/thesis/experiment-integrity-checklist.md` before the first formal run. Record the file/config hash and code commit so the planned analysis can be distinguished from later exploration.

Freeze the question, primary hypothesis, outcome/metric and direction, baseline, analysis unit, split and exclusions, model-selection rule, seed/run budget, stopping rule, secondary analyses, and test-set release condition. State how failures and multiple comparisons will be handled. Stage gates allow justified revisions, but every post-result change must be dated, linked to the result exposure, and labeled exploratory when it was informed by test outcomes.

Log test-set access whenever rows or aggregate results become visible. Specify whether access was `not_loaded`, `summary_seen`, or `row_level`, what information was exposed, and what decisions followed. A test score is not an untouched confirmation if it informed model or protocol selection. Do not relabel previously viewed results as a fresh holdout.

Before claim promotion, the analysis owner checks the frozen record against actual run configs, registry rows, logs, and result artifacts. Missing pre-registration or access records are evidence limitations to disclose; do not reconstruct a pre-run decision from memory and present it as contemporaneous.
