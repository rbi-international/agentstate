# AgentState project instructions

- Read `docs/EXPERIMENT_BASE.md` completely before research-related changes.
  Treat it as the authoritative research protocol.
- Proceed one authorized stage at a time; respect experiment gates.
- Never invent results or claim novelty without evidence.
- Preserve immutable raw traces. Normalization produces separate derived files.
- Future events and future-outcome labels must never enter encoder inputs.
- Keep model/framework identity as metadata, outside encoder inputs during
  invariance experiments.
- Preserve task/repository-aware evaluation and all leakage controls.
- Start with one task and two framework traces before scaling.
- Compare structured features, generic embeddings, summaries, and hybrid
  baselines before training a specialized encoder.
- Treat unresolved labeling definitions as unresolved. Conceptual schemas and
  proposed labeling strategies are not validated schemas or finalized rules.
- Use the `agentstate` Conda environment. Expected interpreter:
  `C:\Users\rbhar\anaconda3\envs\agentstate\python.exe`.
- Keep dependencies minimal and record exact versions for experiments.
- Never commit credentials, weights, generated datasets, or checkpoints.
- Preserve unrelated user changes; read existing files before modifying them.
- Explain changes, verification results, and limitations. Do not claim tests
  passed when no tests exist.
- Do not commit or push unless explicitly instructed.
