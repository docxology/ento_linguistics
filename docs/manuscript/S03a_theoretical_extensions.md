# Supplemental Analysis: Theoretical Extensions {#sec:supplemental_analysis}

This section provides analytical results and theoretical extensions that complement the main findings presented in Sections \ref{sec:methodology} and \ref{sec:experimental_results}.

## Theoretical Extensions

### Formalism of Individuality: Markov Blankets

To rigorize the "Unit of Individuality" domain, we employ the **Markov Blanket** formalism \cite{friston2013life, kirchhoff2018markov}. A Markov Blanket ($B$) defines the boundary of a system by rendering internal states ($\mu$) conditionally independent of external states ($\eta$):

\begin{equation}\label{eq:markov_blanket}
P(\mu | \eta, B) = P(\mu | B)
\end{equation}

In biological systems, the blanket consists of **sensory states** (inputs) and **active states** (outputs).

- **Organismal Blanket**: The ant's cuticle and sensory receptors.
- **Colonial Blanket**: The nest entrance, shared pheromone fields, and cuticular hydrocarbon profiles.

Linguistic confusion arises when terms index the wrong blanket. "Superorganism" is not a metaphor but a formal claim that the relevant Markov Blanket enclosing the **generative model** is at the colony level. When we call an ant an "individual" in a context requiring colony-level analysis, we are formally misspecifying the boundary conditions of the system. The Active Inferants framework \cite{friedman2021active} operationalizes this insight, showing that foraging behavior emerges from ensemble-level inference over pheromone gradients—locating the generative model at the colony blanket rather than the organismal blanket.

### Discourse Analysis Frameworks

Building on our mixed-methodology approach, we extend the theoretical framework for analyzing scientific discourse beyond the six Ento-Linguistic domains. Our analysis reveals that terminology networks serve as both descriptive tools and constitutive elements of scientific knowledge production.

**Constitutive Framework**:

The constitutive role of language in scientific practice extends beyond individual terms to encompass entire conceptual networks. We formalize this through the concept of **discursive framing networks**:

\begin{equation}\label{eq:discursive_framing}
F(D, T) = \sum_{t \in T} w_t \cdot f_t(D) \cdot c_t
\end{equation}

where $D$ represents a domain, $T$ is the terminology set, $w_t$ are term weights, $f_t(D)$ is the framing function for domain $D$, and $c_t$ represents contextual factors.

### Ambiguity Classification Systems

Our ambiguity detection framework extends beyond simple polysemy to include context-dependent meaning shifts characteristic of scientific terminology evolution:

**Multi-Level Ambiguity Classification**:

\begin{enumerate}
\item **Lexical Ambiguity**: Multiple dictionary meanings (e.g., "individual" in biological vs. psychological contexts)
\item **Contextual Ambiguity**: Meaning shifts based on research tradition (e.g., "caste" in classical vs. modern entomology)
\item **Scale Ambiguity**: Meaning variations across biological scales (e.g., "behavior" at individual vs. colony levels)
\item **Temporal Ambiguity**: Historical meaning evolution (e.g., "superorganism" from 1970s to present)
\end{enumerate}

### Cross-Domain Conceptual Mapping

We develop conceptual mapping techniques that reveal relationships between domains:

\begin{equation}\label{eq:cross_domain_mapping}
M_{ij} = \frac{1}{|T_i \cap T_j|} \sum_{t \in T_i \cap T_j} s(t, D_i, D_j)
\end{equation}

where $M_{ij}$ is the mapping strength between domains $D_i$ and $D_j$, and $s(t, D_i, D_j)$ measures semantic similarity of term $t$ across domains.

## Framing Analysis Methods

### Anthropomorphic Framing Detection

Anthropomorphic framing detection incorporates linguistic and conceptual indicators:

**Linguistic Indicators**:

- Pronominalization (use of "it" vs. "she/he" for colonies)
- Agency attribution (active vs. passive voice patterns)
- Intentionality markers (words implying purpose or planning)

**Conceptual Indicators**:

- Social structure projections (human hierarchies onto insect societies)
- Emotional attribution (anthropomorphic emotional terms)
- Cultural bias patterns (Western social norms in biological descriptions)

### Hierarchical Framing Analysis

Analysis of hierarchical framing reveals nested levels of social structure imposition:

**Macro-Level Hierarchies**: Colony-level social organization (queen → workers → males)

**Micro-Level Hierarchies**: Individual-level interactions (dominant → subordinate nestmates)

**Inter-Colony Hierarchies**: Population-level relationships (territorial dominance, resource competition)

## Network Analysis

### Temporal Network Evolution

Analysis of how terminology networks evolve over time reveals conceptual shifts:

\begin{equation}\label{eq:temporal_network_evolution}
\Delta G(t) = G(t+1) - G(t) = \sum_{e \in E} \delta_e(t) + \sum_{v \in V} \delta_v(t)
\end{equation}

where $\delta_e(t)$ and $\delta_v(t)$ represent edge and vertex changes over time periods.

**Key Evolutionary Patterns**:

- **Network Growth**: Addition of new terms and relationships
- **Structural Rearrangements**: Changes in network topology
- **Conceptual Consolidation**: Strengthening of established relationships
- **Paradigm Shifts**: Major restructuring events

### Multi-Scale Network Analysis

Network analysis at multiple scales reveals hierarchical organization:

**Local Scale**: Individual term relationships within domains
**Domain Scale**: Inter-term relationships within domains
**Cross-Domain Scale**: Relationships between domains
**Field Scale**: Relationships across the entire entomological terminology network
