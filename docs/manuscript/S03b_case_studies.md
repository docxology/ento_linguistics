# Supplemental Analysis: Case Studies and Validation {#sec:supplemental_case_studies}

## Validation Frameworks

### Inter-Subjectivity Validation

Validation incorporates multiple perspectives:

**Expert Validation**: Entomological domain experts review classifications
**Peer Validation**: Interdisciplinary researchers assess cross-domain mappings
**Historical Validation**: Analysis of terminology evolution against known conceptual shifts
**Cross-Cultural Validation**: Comparison with non-English entomological literature

### Robustness Testing

Robustness analysis ensures result stability:

**Subsampling Stability**: Performance across different corpus subsets
**Parameter Sensitivity**: Robustness to algorithmic parameter variations
**Annotation Consistency**: Agreement across multiple human annotators
**Temporal Stability**: Consistency across publication periods

## Case Study Analysis

### Caste Terminology Evolution: 1850-2024

Ultra-longitudinal analysis reveals century-scale conceptual evolution:

**Pre-Darwinian Period (1850-1859)**: Essentialist caste categories based on morphological differences

**Darwinian Synthesis (1860-1899)**: Evolutionary explanations for caste differences

**Genetic Revolution (1900-1949)**: Chromosomal mechanisms underlying caste determination

**Molecular Biology Era (1950-1999)**: Gene expression and hormonal control of caste differentiation

**Genomic Era (2000-2024)**: Epigenetic and transcriptomic regulation of caste phenotypes \cite{chandra2021epigenetics}, accompanied by growing recognition that rigid caste categories fail to capture the labile, environmentally responsive nature of social insect development \cite{boomsma2018superorganismality}. \citet{warner2024caste} demonstrate that caste differentiation becomes increasingly *canalized* from early development through cascading gene-expression changes modulated by juvenile hormone signaling, while gene expression in *Lasius niger* is more strongly influenced by age than by caste—further undermining the fixedness implied by "caste" terminology.

#### BHL Historical-Layer Grounding (1850-1970) {#sec:bhl_grounding}

These period claims are anchored in measurable term usage by the
Biodiversity Heritage Library historical full-text layer:
{{BHL_DOCUMENTS}} ant/myrmecology documents harvested from the BHL
mirror collection on the Internet Archive (BHL API v3 requires a
key; see `data/bhl/README.md` for the provenance and the verbatim
query). The era-stratified artifact `data/bhl/era_term_usage.json`,
produced by `src/pipeline/bhl_analysis.py`, reports "caste" rising
monotonically from {{BHL_ERA_1850_1899_CASTE_PER_10K}} per 10k
tokens in 1850-1899 ({{BHL_ERA_1850_1899_DOCS}} documents) to
{{BHL_ERA_1900_1949_CASTE_PER_10K}} in 1900-1949
({{BHL_ERA_1900_1949_DOCS}} documents) and
{{BHL_ERA_1950_1970_CASTE_PER_10K}} in 1950-1970
({{BHL_ERA_1950_1970_DOCS}} documents) — an intensification
consistent with the Genetic Revolution and Molecular Biology era
framings above. The labor vocabulary shows the same arc: "worker"
rises from {{BHL_ERA_1850_1899_WORKER_PER_10K}} to
{{BHL_ERA_1900_1949_WORKER_PER_10K}} to
{{BHL_ERA_1950_1970_WORKER_PER_10K}} per 10k tokens across the
eras, while "queen" remains the anchor term throughout
({{BHL_ERA_1850_1899_QUEEN_PER_10K}} →
{{BHL_ERA_1900_1949_QUEEN_PER_10K}} →
{{BHL_ERA_1950_1970_QUEEN_PER_10K}} per 10k). The integrative-era
vocabulary is absent from the entire stratum: "superorganism"
registers {{BHL_ERA_1850_1899_SUPERORGANISM_PER_10K}},
{{BHL_ERA_1900_1949_SUPERORGANISM_PER_10K}}, and
{{BHL_ERA_1950_1970_SUPERORGANISM_PER_10K}} per 10k tokens across
the three eras — zero throughout — marking it as a post-1970 import
into general monographic usage rather than a term the historical
corpus itself carries. All numbers resolve at render time from the
BHL_* manuscript tokens.

### Superorganism Concept Evolution

Table \ref{tab:superorganism_concept_evolution} traces the
superorganism concept across seven decades of research:

The BHL historical layer brackets the start of this table from
below: across {{BHL_DOCUMENTS}} BHL-mirror documents, "superorganism"
occurs {{BHL_ERA_1850_1899_SUPERORGANISM_PER_10K}} per 10k tokens in
1850-1899, {{BHL_ERA_1900_1949_SUPERORGANISM_PER_10K}} in 1900-1949,
and {{BHL_ERA_1950_1970_SUPERORGANISM_PER_10K}} in 1950-1970 — zero
throughout (`data/bhl/era_term_usage.json`, produced by
`src/pipeline/bhl_analysis.py`), confirming that the concept's
theoretical vocabulary lived outside the monographic stratum and
entered routine usage only in the post-1970 decades traced here.

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|c|c|}
\hline
\textbf{Era} & \textbf{Dominant Metaphor} & \textbf{Key Evidence} & \textbf{Critiques} & \textbf{Legacy} \\
\hline
1960s & Organismic & Division of labor analogies & Ignores individual variation & Established field \\
1970s & Cybernetic & Communication networks & Mechanistic reductionism & Systems thinking \\
1980s & Genetic & Kin selection theory & Haplodiploidy focus & Evolutionary framework \\
1990s & Neuroendocrine & Pheromonal control & Colony complexity & Regulatory mechanisms \\
2000s & Epigenetic & DNA methylation & Environmental effects & Developmental plasticity \\
2010s & Microbiome & Symbiont communities & Host-symbiont dynamics & Extended organism concept \\
2020s & Canalization & Cascading gene expression & Lability of ``caste'' & Terminological reform \\
\hline
\end{tabular}
\caption{Evolution of superorganism concept across research eras}
\label{tab:superorganism_concept_evolution}
\end{table}

## Methodological Reflections

### Mixed-Methodology Integration

Our approach integrates qualitative and quantitative methods:

**Qualitative Contributions**:

- Theoretical framework development
- Conceptual category identification
- Historical context analysis
- Cross-domain relationship mapping

**Quantitative Contributions**:

- Statistical pattern identification
- Network structure analysis
- Temporal trend quantification
- Validation metric development

For a discussion of methodological limitations and scope considerations, see Section \ref{sec:discussion}. Future research directions, including semantic analysis (transformer-based embeddings, multilingual extensions) and practical applications (terminology standards, peer review tools), are discussed in Section \ref{sec:conclusion}.
