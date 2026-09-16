# PMC Open-Access Full-Text Corpus (parallel layer)

Parallel analysis layer harvested from PubMed Central via the
E-utilities; the abstract corpus (`data/corpus/abstracts.json`) remains
the headline corpus.

## Files

- `fulltexts.json` — JSON list of full-text records
  (`pmcid`, `doi`, `title`, `year`, `journal`, `license`, `abstract`,
  `body_text`).
- `provenance.json` — sidecar mapping `sha256(body_text)` to
  `{pmcid, doi, query, retrieved_at}`.
- `README.md` — this document.

## Search query (verbatim)

```
("ant"[Title/Abstract] OR "ants"[Title/Abstract] OR "Formicidae"[Title/Abstract] OR "myrmecolog*"[Title/Abstract] OR "eusocial"[Title/Abstract] OR "eusociality"[Title/Abstract] OR "social insect"[Title/Abstract]) AND "open access"[Filter]
```

Applied against `esearch db=pmc` with `retmode=json`,
`sort=relevance`, `retmax=600`, and the project's NCBI `tool`/`email`
identification.  The `open access[Filter]` clause restricts hits to the
PMC open-access subset, so every hit has a retrievable full text.

## Filters

1. esearch relevance ranking over `("ant"[Title/Abstract] OR "ants"[Title/Abstract] OR "Formicidae"[Title/Abstract] OR "myrmecolog*"[Title/Abstract] OR "eusocial"[Title/Abstract] OR "eusociality"[Title/Abstract] OR "social insect"[Title/Abstract]) AND "open access"[Filter]`.
2. `efetch db=pmc retmode=xml` in batches of
   10 PMCIDs, spaced
   0.5s apart (NCBI politeness).
3. Record kept only when: PMCID resolves in the response, the article
   has a non-empty body, and a word-boundary relevance term
   (ant/ants, Formicidae, myrmecology*, eusocial/eusociality,
   social insects, Formicinae, Myrmicinae, Dorylinae, Linepithema,
   Solenopsis) occurs in title/abstract/body.
4. Duplicates dropped by PMCID (first occurrence kept).
5. Target cap: 500 documents.

## Coverage (500 documents)

- Publication years: 2002–2026
- Distinct journals: 125
- License coverage:

- `https://creativecommons.org/licenses/by/4.0/`: 354 documents
- `https://creativecommons.org/licenses/by-nc/4.0/`: 35 documents
- `https://creativecommons.org/licenses/by/2.5/`: 31 documents
- `https://creativecommons.org/licenses/by-nc-nd/4.0/`: 25 documents
- `https://creativecommons.org/licenses/by/3.0/`: 20 documents
- `https://creativecommons.org/licenses/by/2.0/`: 12 documents
- `https://creativecommons.org/publicdomain/zero/1.0/`: 7 documents
- `unknown`: 7 documents
- `https://creativecommons.org/licenses/by-nc/3.0/`: 5 documents
- `This article is made available via the PMC Open Access Subset for unrestricted research re-use and secondary analysis in any form or by any means with acknowledgement of the original source. These per`: 1 documents
- `creative-commons`: 1 documents
- `https://creativecommons.org/licenses/by-nc-sa/4.0/`: 1 documents
- `us-gov`: 1 documents

## Reproduction

```bash
uv run python src/data/pmc_fulltext.py --target 500
```

The analysis layer is built separately:

```bash
uv run python src/pipeline/fulltext_pipeline.py
```
