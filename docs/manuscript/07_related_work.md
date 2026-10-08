# Related Work {#sec:related_work}

## Scientific Language and Categories

Philosophy of science and discourse research provide context for studying terminology as part of research practice \citep{kuhn1996, latour1987, longino1990, fairclough1992, wodak2009methods}. Conceptual and deliberate-metaphor frameworks supply complementary questions about ordinary connotations and communicative intention \citep{lakoff1980metaphors, steen2017deliberate}. This study draws motivation from those traditions, while keeping computational lexical proxies separate from claims about thought, intention, or causal influence.

Work on scientific classification and cultural histories offers additional context \citep{berlin1992, hacking1999social, sleigh2007ants}. The present six-domain taxonomy is a proposed analytic organization; it is not independently established as exhaustive or uniquely appropriate.

## Terminology in Social-Insect Research

Debates over caste categories and descriptions of ant behavior motivate explicit definitions \citep{gordon1992wittgenstein, boomsma2018superorganismality}. Research on collective behavior provides biological context for distinguishing task allocation from an assumed centralized controller \citep{gordon2010, gordon2019ecology, gordon2023ecology}. The descriptive corpus pipeline does not itself test those mechanisms.

Discussions of racially loaded language in social-insect research provide a substantive case for examining terminology choices \citep{herbers2006, herbers2007}. The ESA Better Common Names Project is a related institutional initiative \citep{betternamesproject2024}, and the term *colony* itself has been examined for its settler-colonial connotations \citep{vis2026colony}. Neither the current frequency analysis nor CACE scoring measures the adoption or effects of these reforms.

Molecular accounts of caste and epigenetic mechanisms \citep{sumner2018molecular, oldroyd2021epigenetics} and developmental canalization research \citep{qiu2022canalized} reinforce the need to distinguish developmental processes from temporary behavioral labels. Canalization must not be interpreted as proof that every caste category is labile. The historical superorganism literature \citep{wheeler1911} and later conceptual analysis \citep{boomsma2018superorganismality} also caution against dating a concept's origin from an absent OCR match.

## Computational Mapping and Source-Layer Analysis

Computational literature mapping supplies methods for examining connections among terms and publications \citep{chen2006citespace}. Here, document co-occurrence is kept separate from vocabulary-overlap relationships between predefined concepts. TF-IDF/KMeans occupancy entropy is used as a descriptive measure of context distributions, without claiming independent sense annotation or validated linguistic ambiguity.

Source-layer comparisons are also descriptive. Abstracts, full texts, historical volumes and preprints differ in access, genre, length, topic and extraction threshold. An observed difference between layers is not automatically a robustness result or a historical change in meaning.

## Validation and Experimental Evidence

\citet{grimmer2013text} emphasize, for automated content analysis, validation tailored to the substantive question. Its relevance here is methodological: word counts and computational categories require an explicit connection to the construct they are intended to measure. This study's receipts establish computational custody, not construct validity; Section \ref{sec:measurement_validation} specifies the annotation design that would address the latter.

Experimental metaphor research supplies a complementary way to investigate reader responses. \citet{thibodeau2011metaphors} studied how contrasting crime metaphors affected reasoning. That evidence concerns a different topic and participant setting. It supports using controlled language manipulations to formulate testable questions, while leaving the effects of technical ant terminology on specialists and students unresolved. Connecting these traditions requires both measurement validation and a direct communication experiment.

## Active Inference and Colony Modeling

The Free Energy Principle and Active Inference supply theoretical vocabulary for generative modeling \citep{friston2010free, friston2013life, clark2013whatever, kirchhoff2018markov}. The Active Inferants framework supplies a simulated ant-foraging example \citep{friedman2021active}; model behavior alone cannot establish how terminology choices affect scientific reasoning.

Theoretical perspectives on eusociality and biological individuality \citep{nowak2010evolution, boomsma2018superorganismality} motivate careful definition of units and mechanisms. The Environment-Centric Active Inference extensions in the supplement remain proposed constructions requiring explicit models and empirical testing.

## Collective Behavior and Complex Systems

Collective-behavior research supplies a mechanistic counterpart to the terminology framework. \citet{couzin2009collective} relates group-level response to social interaction, individual state and environmental modification. \citet{feinerman2017cognition} distinguishes collective responses supported by individual information from outcomes that require interactions across a scale gap. These accounts motivate asking which entity holds information and which process combines it; a colony-level description alone does not identify the computation.

Ecological conditions also matter to how interaction processes regulate activity \citep{gordon2014ecology}. In an experimental harvester-ant example, combined food and forager chemical cues on mimics increased outgoing foraging activity \citep{greene2013chemical}. Such experiments link a defined intervention to an observed response. They illustrate the level of biological evidence needed for a mechanistic claim, rather than validating any particular lexical label. The corpus network instead records pairs of expressions in documents: its vertices, edges and timescale differ from those of a measured ant-interaction network. Similar graph vocabulary should prompt an explicit comparison of observational units before a mechanism is transferred between fields.

## Positioning This Work

This repository contributes a six-domain descriptive workflow with auditable source layers, inspectable computational definitions, regenerable figures and receipt-bound values. CACE is a proposed evaluation framework, not a validated measure or intervention. Its independent validation would require annotated meanings, blinded judgments, measured agreement, and tests of sensitivity and communication outcomes. The distinction between implemented measurement, theoretical motivation, and unperformed validation is part of the contribution.
