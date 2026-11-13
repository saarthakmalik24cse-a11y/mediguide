# Development evaluation — 17 September 2026

The bundled knowledge snapshot contains 36 MedlinePlus topic records and five FDA product-label records. Patient documents and insurance policy examples are synthetic.

The broader authored development set has 14 answerable questions and four unsupported questions. It is small, has not been independently clinically reviewed, and is not a held-out benchmark.

| Metric | K=1 | K=3 |
|---|---:|---:|
| Precision@K | 100% | 45.24% |
| Recall@K | 67.86% | 85.71% |
| Hit Rate | 100% | 100% |
| Citation source relevance | 100% | 97.62% |
| Citation label validity | 100% | 100% |
| Correct abstention on four negative cases | 100% | 100% |

Precision counts distinct annotated source/page hits divided by requested K. Multiple chunks from the same source/page do not increase hits. Some cases annotate more than one acceptable source, explaining why Recall@1 is lower than Hit Rate@1.

These numbers establish that the selected test questions retrieve appropriate sources. They do not establish clinical safety, factual completeness, semantic entailment of every answer claim, or performance on arbitrary patient questions. No paid LLM endpoint was exercised; evaluation used offline source excerpts.

Before a real pilot, independent reviewers should add paraphrases, ambiguous medication names, conflicting policy versions, table-heavy scans, numerical interpretation questions, adversarial documents, and clinician/policy-reviewed reference answers. Maintain a separate held-out set and measure claim support and refusal quality manually.

Reproduce using the commands in README.md. Machine-readable results are in data/gold/broader_results_k1.json and data/gold/broader_results_k3.json.
