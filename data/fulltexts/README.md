# PMC Open-Access Full-Text Corpus (parallel layer)

Parallel analysis layer harvested from PubMed Central via the
E-utilities; the abstract corpus (`data/corpus/abstracts.json`) remains
the headline corpus.

## Files

- `fulltexts_NNNNN.json` — shard files, at most 1000 records
  each (~39 MB at full-text length), holding JSON lists of full-text
  records (`pmcid`, `doi`, `title`, `year`, `journal`, `license`,
  `abstract`, `body_text`).  Concatenation order is the filename
  order:

- `fulltexts_00001.json`
- `fulltexts_00002.json`
- `fulltexts_00003.json`
- `fulltexts_00004.json`
- `fulltexts_00005.json`
- `fulltexts_00006.json`
- `fulltexts_00007.json`
- `fulltexts_00008.json`

- `provenance.json` — single sidecar mapping `sha256(body_text)` to
  `{pmcid, doi, query, retrieved_at}`.
- `README.md` — this document.

## Search query (verbatim)

```
("ant"[Title/Abstract] OR "ants"[Title/Abstract] OR "Formicidae"[Title/Abstract] OR "myrmecolog*"[Title/Abstract] OR "eusocial"[Title/Abstract] OR "eusociality"[Title/Abstract] OR "social insect"[Title/Abstract]) AND "open access"[Filter]
```

Applied against `esearch db=pmc` with `retmode=json`,
`sort=relevance`, `retmax=10000`, and the project's NCBI `tool`/`email`
identification.  The `open access[Filter]` clause restricts hits to the
PMC open-access subset, so every hit has a retrievable full text.

## Filters

1. esearch relevance ranking over `("ant"[Title/Abstract] OR "ants"[Title/Abstract] OR "Formicidae"[Title/Abstract] OR "myrmecolog*"[Title/Abstract] OR "eusocial"[Title/Abstract] OR "eusociality"[Title/Abstract] OR "social insect"[Title/Abstract]) AND "open access"[Filter]`; harvest order prioritizes
   documents with a locally matchable OpenAlex `cited_by_count`
   (highest cited first), relevance order otherwise.
2. `efetch db=pmc retmode=xml` in batches of
   10 PMCIDs, spaced
   0.5s apart (NCBI politeness).
3. Record kept only when: PMCID resolves in the response, the article
   has a non-empty body, and a word-boundary relevance term
   (ant/ants, Formicidae, myrmecology*, eusocial/eusociality,
   social insects, Formicinae, Myrmicinae, Dorylinae, Linepithema,
   Solenopsis) occurs in title/abstract/body.
4. Duplicates dropped by PMCID (first occurrence kept).
5. Target: every candidate from the relevance esearch (no cap).

## Sharding and resumability

- Shards hold at most 1000 records (GitHub rejects blobs
  >100 MB).  Each shard and the provenance sidecar are written
  atomically (tmp file + rename) after every shard fill.
- The harvester skips any PMCID already present in the shards or
  provenance, so an interrupted run resumes where it stopped:

```bash
uv run python src/data/pmc_fulltext.py
```

- Load the whole corpus in order with the frozen helper:

```python
from data.pmc_fulltext import load_fulltexts
records = load_fulltexts(Path("data/fulltexts"))
```

Last harvest run: 3 new documents from 7205 candidates (0 failed batches skipped).

## Coverage (7073 documents)

- Publication years: 1873–2026
- Distinct journals: 1093
- Body text: 273,559,168 characters
- License coverage:

- `https://creativecommons.org/licenses/by/4.0/`: 5133 documents
- `https://creativecommons.org/licenses/by-nc-nd/4.0/`: 629 documents
- `https://creativecommons.org/licenses/by-nc/4.0/`: 358 documents
- `https://creativecommons.org/licenses/by/3.0/`: 227 documents
- `https://creativecommons.org/licenses/by/2.0/`: 195 documents
- `https://creativecommons.org/licenses/by/2.5/`: 121 documents
- `https://creativecommons.org/licenses/by-nc/3.0/`: 83 documents
- `https://creativecommons.org/publicdomain/zero/1.0/`: 53 documents
- `unknown`: 46 documents
- `This article is made available via the PMC Open Access Subset for unrestricted research re-use and secondary analysis in any form or by any means with acknowledgement of the original source. These per`: 35 documents
- `https://creativecommons.org/licenses/by-nc-sa/4.0/`: 34 documents
- `https://creativecommons.org/licenses/by-nc-sa/3.0/`: 28 documents
- `open-access`: 26 documents
- `https://creativecommons.org/licenses/by-nc-nd/3.0/`: 21 documents
- `Since January 2020 Elsevier has created a COVID-19 resource centre with free information in English and Mandarin on the novel coronavirus COVID-19. The COVID-19 resource centre is hosted on Elsevier C`: 19 documents
- `https://creativecommons.org/publicdomain/mark/1.0/`: 8 documents
- `https://creativecommons.org/licenses/by-nd/4.0/`: 7 documents
- `This is an open access article published under an ACS AuthorChoice License, which permits copying and redistribution of the article or any adaptations for non-commercial purposes.`: 6 documents
- `https://creativecommons.org/licenses/by-nc/2.5/`: 5 documents
- `Users may view, print, copy, and download text and data-mine the content in such documents, for the purposes of academic research, subject always to the full Conditions of use:http://www.nature.com/au`: 4 documents
- `This is an open access article published under a Creative Commons Attribution (CC-BY) License, which permits unrestricted use, distribution and reproduction in any medium, provided the author and sour`: 3 documents
- `Reproduction is permitted for noncommercial purposes.`: 2 documents
- `This work is licensed under a Creative Commons Attribution-NonCommercial-NoDerivs 3.0 Unported License`: 2 documents
- `Users may view, print, copy, download and text and data- mine the content in such documents, for the purposes of academic research, subject always to the full Conditions of use: http://www.nature.com/`: 2 documents
- `creativeCommonsBy`: 2 documents
- `http://creativecommons.org/licenses/by/2.0</url>),`: 2 documents
- `http://www.nature.com/authors/editorial_policies/license.html#terms`: 2 documents
- `https://creativecommons.org/licenses/by-nc/2.0/`: 2 documents
- `https://creativecommons.org/licenses/by/2.0/uk/`: 2 documents
- `License information: This is an open-access article distributed under the terms of the Creative Commons Attribution License, which permits unrestricted use, distribution, and reproduction in any mediu`: 1 documents
- `Permissions https://www.science.org/help/reprints-and-permissions`: 1 documents
- `Published under exclusive license by The American Society for Biochemistry and Molecular Biology, Inc.`: 1 documents
- `Reprints and permissions information is available at www.nature.com/reprints.`: 1 documents
- `This is an Open Access article which permits unrestricted noncommercial use, provided the original work is properly cited.`: 1 documents
- `This is an Open Access article: verbatim copying and redistribution of this article are permitted in all media for any purpose`: 1 documents
- `This is an open access article distributed under the terms of the Open Government License.`: 1 documents
- `creative-commons`: 1 documents
- `http://creativecommons.org/licenses/by/4.0/`: 1 documents
- `https://creativecommons.org/licenses/by-nc-nd/3.0/igo/`: 1 documents
- `https://creativecommons.org/licenses/by-nc-nd/3.0/us/`: 1 documents
- `https://creativecommons.org/licenses/by-nc/2.0/uk/`: 1 documents
- `https://creativecommons.org/licenses/by/3.0/us/`: 1 documents
- `oup-standard`: 1 documents
- `public-domain`: 1 documents
- `us-gov`: 1 documents

The analysis layer is built separately:

```bash
uv run python src/pipeline/fulltext_pipeline.py
```
