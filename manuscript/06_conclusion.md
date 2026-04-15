# Conclusion {#sec:conclusion}

This work establishes Ento-Linguistic analysis as a methodology for examining how scientific language constitutes—rather than merely represents—knowledge about insect biology. Through computational analysis of terminology networks across **369 entomological publications** (48787 tokens; 888 extracted candidate terms, 261 domain-assigned) and six analytically distinct domains, we demonstrate that entomological terminology carries systematic patterns of ambiguity, anthropomorphic framing, and conceptual structure that actively shape research practice. The accompanying open-source computational pipeline provides a reproducible toolkit for extending this analysis to new corpora and domains.

## Core Contributions

The work makes three primary contributions. First, the six-domain analytical framework provides a comprehensive, reproducible architecture for examining how language shapes scientific understanding in entomology and, by extension, in other fields where human social concepts are projected onto non-human systems. Second, the computational pipeline demonstrates that large-scale, quantitative analysis of scientific discourse is both feasible and revealing—exposing structural patterns that qualitative analysis alone cannot detect. Third, the CACE meta-standards, defined in Section \ref{sec:methodology}, offer a practical evaluation framework:

- **Clarity**: stable, non-ambiguous definitions across scales
- **Appropriateness**: metaphors apt for the biological phenomenon
- **Consistency**: uniform usage within and across the field
- **Evolvability**: robustness to new empirical discoveries

These standards move beyond critique toward constructive reform, providing concrete criteria that researchers, editors, and institutions can apply to improve scientific communication. 

The quantitative reach of these findings underscores their significance. Across the 261 domain-assigned terms extracted from 369 publications, 16.9\% exhibit highly context-dependent meanings. The 6 conceptual clusters identified in the concept map (linked by 9 weighted relationships) confirm that the terminological landscape is both deeply interconnected and systematically biased. The Power \& Labor domain—containing the most entrenched anthropomorphic vocabulary—generates the strongest cross-domain interference, with 43 bridging terms propagating hierarchical framing into adjacent domains. The Economics domain, despite its tightly constrained 10-term vocabulary with 0 bridging terms, exhibits both the highest mean semantic entropy and the greatest proportion of high-entropy terms, indicating that economic metaphors form a self-contained but intensely polysemous subsystem. Crucially, CACE validation on the "slave" $\rightarrow$ "host worker" terminological reform demonstrates significant overarching score improvement, confirming that the framework functions as both an analytical diagnostic and a prescriptive template for actionable reform.

## Future Directions

Several avenues emerge for extending this work.

**Multilingual and Cross-Cultural Analysis.** Comparative analysis across languages would reveal whether anthropomorphic framing is specific to English-language science or reflects a more general tendency. Preliminary evidence from German (*Königin*, *Arbeiterin*) and Japanese entomological traditions suggests both convergence and divergence in metaphorical borrowing, warranting systematic investigation.

**Longitudinal Terminology Tracking.** Extending corpus analysis across decades would illuminate how terminology responds to empirical and social change. Do genomic discoveries erode the dominance of "caste" vocabulary? Does institutional reform (e.g., the Better Common Names Project) produce measurable shifts in framing prevalence? Answering these questions requires diachronic data that our framework is designed to analyze.

**Educational and Editorial Tools.** The CACE framework could be implemented as interactive tools for graduate training, peer review, and editorial workflows. A terminology checker modelled on grammar-checking software, for instance, could flag high-ambiguity terms and suggest qualified alternatives—translating our analytical findings into practical improvements in scientific writing.

**Cross-Disciplinary Extension.** The Ento-Linguistic framework is not specific to entomology. Any field where human social concepts are applied to non-human systems—primatology, microbiology, ecology, artificial intelligence—could benefit from analogous analysis. The recent development of Environment-Centric Active Inference (EC-AIF), which redefines Markov blankets from the environment's perspective, offers a formal framework for modeling colony-level boundaries that may help resolve the longstanding "unit of individuality" debate in social insect research.

**Cross-Era Semantic Meta-Analysis.** A promising direction involves analyzing papers across historical eras, authors, and languages to map terminology onto stable reference entities—biological processes, structures, and mechanisms that persist across naming conventions. By grounding each terminological variant (e.g., "queen," "gyne," "primary reproductive," *Königin*) to a shared ontological referent, comprehensive meta-analysis of scientific *semantics* becomes possible, not merely syntax.

Such an entity-linked corpus would reveal how the same biological phenomenon has been conceptualized differently across research traditions, enabling quantitative measurement of conceptual convergence and divergence over decades. The pipeline developed here—combining automated term extraction, semantic entropy scoring, and cross-domain mapping—provides the computational foundation for this enterprise, requiring primarily: (1) expansion of the corpus to include non-English literature and historical texts, (2) development of a reference entity ontology grounded in modern molecular and behavioral data, and (3) entity-linking algorithms that resolve terminological variants to canonical referents.

## Closing Remarks

The entanglement of speech and thought in scientific practice is neither accidental nor inconsequential. When a researcher describes *Diacamma* nestmates as "queens" and "workers," these terms carry an entire social ontology that may obscure the fluid, experience-dependent task performance documented by \citet{ravary2007}. Replacing "queen" with "primary reproductive" is not cosmetic—it is an act of **model repair**, aligning our linguistic priors with the physics of distributed systems and reducing the **variational free energy** of our scientific explanations.

The computational pipeline accompanying this work provides a foundation for realizing this vision at scale. Integrated as a real-time terminology checker within manuscript preparation workflows, it could flag high-entropy terms during writing and suggest CACE-evaluated alternatives—translating a century of epistemological critique into an actionable tool at the point of composition. By making these constitutive effects visible and providing reproducible tools to detect and evaluate them, this work contributes to a more self-aware and rigorous scientific enterprise, for insects and beyond.
