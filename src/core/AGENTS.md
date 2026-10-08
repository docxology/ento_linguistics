# Core utilities

This directory belongs to the standalone Ento-Linguistics repository. Follow ../../AGENTS.md and ../AGENTS.md.

For provenance or resource changes, inspect callers of analysis_signature and the real-file controls in ../../tests/test_provenance.py and ../../tests/test_nltk_resources.py. Signatures must bind ordered contents and selected inputs rather than timestamps or row counts. Missing resources and corrupt receipts must fail.

The schema-2 analysis receipt binds corpus/export/figure inventory, Python sources, uv.lock and the selected English NLTK inputs. It is software custody evidence; it does not certify relevance, licenses, word senses or causal validity.
