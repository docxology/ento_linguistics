# Introduction {#sec:introduction}

## Linguistic Priors and Generative Models

Scientific inquiry is a process of **active inference**, where researchers refine generative models to minimize surprise about biological observations \cite{friston2010free}. Language acts as the **hyper-prior** for these models: it constrains the hypothesis space before data collection begins. When entomologists employ terms like "queen" or "caste," they are not merely labeling phenomena; they are importing a high-precision prior from human social systems into their model of insect biology. If this prior is structurally misaligned with the target system—for instance, assuming top-down control in a stigmergic network—the resulting model will necessarily suffer from high variational free energy, manifesting as persistent anomalies and theoretical epicycles \cite{kuhn1996, clark2013whatever}.

The **scientific community itself can be modeled as a multi-scale Active Inference agent** whose collective task is to minimize long-term surprise about the entomological world it observes. Its generative model is the shared ontology of the field—the lexicon and conceptual structures encoded in the literature. When this ontology is precise and plastic, the community efficiently updates its priors in response to new evidence (e.g., genomic data revealing that caste determination is a labile epigenetic process rather than a fixed fate). When the ontology is rigid or laden with hidden anthropomorphic priors, the agent suffers from **prior dogmatism**: a failure of belief updating where high-precision, fixed priors overwhelm contradictory sensory evidence. In this state, anomalies are explained away rather than used to update the model. Terminology reform is therefore a **model selection** process: optimizing the community's generative model to restore its capacity for free-energy minimization.

This optimization requires specific criteria. We propose **Evolvability**—defined here as **scale-invariance**—as a critical metric for scientific terms. An evolvable term maintains its validity across biological scales (gene, organism, superorganism) without fracturing. "Queen," by contrast, is scale-brittle: it functions as a metaphor at the colony level but dissolves into incoherence when applied to the underlying genetic or molecular mechanisms of reproductive differentiation.

The consequences of this misalignment are not merely philosophical. They propagate through every stage of the research cycle—from hypothesis formulation, through variable selection, to the causal explanations offered for observed phenomena. The following section formalizes this propagation as a problem of model integrity.

## Motivation: Minimizing Model Misspecification

The drive for terminological clarity is not a stylistic preference but a requirement for model integrity. As \citet{keller1991language} argued, the language of science constitutes the cognitive scaffolding of research. In the framework of Active Inference, an undefined or metaphor-laden term introduces **irreducible uncertainty** (entropy) into the scientific communication channel, degrading the precision of the community's collective generative model.

The present moment demands this formalization. Recent cognitive science emphasizes the distinction between deliberate and conventional metaphor use, demonstrating that metaphor in scientific discourse often operates as a conscious communicative strategy rather than an automatic conceptual mapping \cite{steen2017deliberate}. Rather than perpetuating inherited assumptions in our linguistic ontology, researchers must critically assess whether their terminological priors minimize or maximize the complexity of their biological models.

A paradigmatic example is the "slave-making" debate. \citet{herbers2006} showed that the term "slave" naturalizes a human institution while obscuring the biological mechanism of **social parasitism**. In formal terms, the "slave" metaphor implies a conscious coercion policy, whereas the replacement term "dulosis" correctly identifies the phenomenon as a breakdown in nestmate recognition signals—a failure of the Markov Blanket's security filter. Reform here is not merely ethical; it restores the causal fidelity of the scientific model by replacing a high-entropy metaphor with a mechanistically precise descriptor.

## The Challenge of Terminological Reform

A common objection to terminological reform is that changing vocabulary creates disconnection from existing literature. If entomologists abandon terms like "caste" or "slave," how would researchers locate papers on task performance or social parasitism?

This objection inadvertently strengthens the case for reform. Retaining problematic terminology for convenience perpetuates and compounds the conceptual distortions it encodes \cite{herbers2006}. The appropriate response is systematic development of clearer vocabulary alongside the indexing infrastructure needed for literature continuity—cross-referencing deprecated terms, establishing synonym mappings, and leveraging modern search capabilities that already make vocabulary-independent retrieval routine. Growing professional consensus around inclusive language in myrmecology and the Entomological Society of America's Better Common Names Project \cite{betternamesproject2024} demonstrate that the field increasingly recognizes both the necessity and the feasibility of reform.

## Ento-Linguistic Domains: A Framework for Analysis

We organize our analysis around six domains where entomological language creates ambiguity or imports unjustified assumptions. Each domain isolates a distinct category of terminological friction between human conceptual frameworks and ant biology.

**Unit of Individuality.** The definition of a biological individual is formally equivalent to the specification of a **Markov Blanket**—the statistical boundary separating internal states from external states \cite{friston2013life}. Terms like "colony," "superorganism," and "individual" confuse these boundaries, creating models where the relevant unit of agency is undefined. Critically, the term ``colony'' also carries a fraught ideological history: as \citet{vis2026colony} demonstrates, its too-casual adoption across entomological literature imports settler-colonial assumptions about social arrangements into descriptions of insect life, compounding the epistemic problem of misspecified Markov Blanket boundaries with a broader political–historical distortion.

**Behavior & Identity.** Task performance in ants is a fluid process of **policy selection** based on local cues \cite{gordon2010}. However, terminology transforms these transient policies into categorical identities ("forager," "nurse"). This effectively hard-codes a fixed-role prior into the model, obscuring the plasticity and Bayesian updating that actually drives task allocation.

**Power \& Labor.** Terms like "queen," "worker," and "caste" impose a hierarchical control architecture on a system that is fundamentally **stigmergic**. This introduces a causal error: it attributes colony-level regulation to centralized agency (the queen) rather than distributed feedback loops, fundamentally misrepresenting the system's control theory.

**Sex \& Reproduction.** Terms like "sex determination" and "sex differentiation" carry implicit assumptions about binary systems that may not map onto ant reproductive biology, where haplodiploidy creates fundamentally different patterns \cite{chandra2021epigenetics}.

**Kin \& Relatedness.** Human kinship terminology, grounded in bilateral relatedness, creates systematic friction when applied to ant societies structured by haplodiploidy. In haplodiploid species, full sisters share an average relatedness coefficient of $r = 0.75$—higher than the mother–daughter coefficient of $r = 0.5$—a fundamental asymmetry absent from human kinship models. Terms such as "sister," "mother," and "family" obscure this asymmetry and its profound consequences for kin selection theory \cite{chandra2021epigenetics}.

**Economics.** Economic metaphors—markets, trade, investment, cost-benefit—shape analysis of ant foraging, resource distribution, and colony-level resource management. This domain investigates how transactional frameworks constrain biological interpretation by conflating proximate energetic expenditure with ultimate fitness costs, importing assumptions of rational optimisation from microeconomics into systems that operate through evolved heuristics rather than deliberative calculation. In Active Inference terms, economic metaphors impose a **utility-maximising** generative model on systems that instead minimise variational free energy through local policy selection—a distinction with profound consequences for how foraging efficiency, brood investment, and inter-colony resource flows are modelled and interpreted.

## Research Approach

This work employs a mixed-methodology framework combining computational text analysis with theoretical discourse examination. The computational component processes a **corpus of 369 entomological publications** (48787 tokens; 7105 unique token types; 888 extracted candidate terms, 261 domain-assigned) using automated term extraction, co-occurrence network construction, and information-theoretic ambiguity scoring. The theoretical component, informed by \citeauthor{foucault1972archaeology}'s archaeological method \citeyearpar{foucault1972archaeology}, conceptual metaphor theory \cite{lakoff1980metaphors}, and \citeauthor{gordon2023ecology}'s \citeyearpar{gordon2023ecology} ecological framework for collective behavior, examines how the statistical patterns reflect deeper conceptual structures. Longitudinal case studies of "caste" and "superorganism" vocabularies (Section \ref{sec:experimental_results}) track terminological evolution alongside empirical discoveries over five decades, providing diachronic evidence for the framework's claims. All data and analysis code are reproducible and available for validation.

## Terminology Network Visualization

To illustrate the framework's output, Figure \ref{fig:concept_map} shows how terms cluster around the six Ento-Linguistic domains and form cross-domain networks of meaning; detailed quantitative analysis follows in Section \ref{sec:experimental_results}.

\begin{figure}[h]
\centering
\includegraphics[width=0.9\textwidth]{../output/figures/concept_map.png}
\caption{Conceptual map of Ento-Linguistic domains showing relationships between terminology networks. Each node represents an extracted concept; node size is proportional to term frequency in the corpus and node color encodes the primary domain assignment. Edges connect co-occurring concepts, with thickness reflecting co-occurrence strength. The six domains form interconnected clusters; central hub terms such as ``colony,'' ``caste,'' and ``individual'' bridge multiple domains, demonstrating how specific terminological choices propagate across the scientific discourse of entomology.}
\label{fig:concept_map}
\end{figure}
