# Introduction {#sec:introduction}

## Terminology as a Research Question

Scientific terminology connects observations, categories, and explanatory models. In social-insect research, familiar labels such as queen, worker, caste, kin, and colony can serve technical functions while retaining ordinary-language connotations. The relevant question is when those connotations help communication, when explicit definitions are needed, and how either possibility can be studied without inferring beliefs from word counts alone.

Philosophical and linguistic work supplies motivation for examining terminology within scientific practice \cite{latour1987, longino1990, lakoff1980metaphors}. Entomological discussions of categories and loaded metaphors provide field-specific context \cite{gordon1992wittgenstein, herbers2006, herbers2007}. These perspectives motivate empirical questions; they do not make every conventional term misleading or demonstrate that a replacement improves scientific understanding.

## The Challenge of Terminological Reform

Established terms support literature discovery and can carry precise operational meanings. Proposed alternatives therefore require context-specific comparison rather than automatic replacement. A task-based description may be useful for a behavioral observation without replacing a developmentally defined caste category. Molecular and developmental research makes that distinction especially important \cite{sumner2018molecular, qiu2022canalized}.

CACE---Clarity, Appropriateness, Consistency, and Evolvability---is introduced as an explicit set of evaluation questions. Its numerical scoring rules are one inspectable implementation, rather than an independently validated measure of understanding. The biological mechanism, intended referent, reader population, and definition supplied by an author remain central to evaluating terminology.

## From Labels to Biological Explanation

A useful terminology analysis separates the expression, its referent, and the mechanism invoked to explain that referent. *Worker* can identify a reproductive category or describe an individual performing a task; neither usage alone specifies how task allocation is regulated. Definitions of caste have themselves been examined as a conceptual problem \cite{villet1992caste}, while experimental work shows that individual experience can contribute to persistent division of labor \cite{ravary2007}. These examples locate the research question in the relationship between definitions and evidence, rather than in a presumption that social vocabulary is necessarily inaccurate.

The six domains provide questions to ask of a passage: what entity is described, at which biological scale, using which observable criteria, and with what explanatory commitment? Frequency and co-occurrence help locate passages for this inquiry. Assessing whether a label obscures a mechanism requires examining those passages and evaluating readers' inferences. This distinction makes the framework useful for comparative reading without treating the taxonomy as a discovered ontology.

## Six Analytical Domains

The framework defines six overlapping domains:

1. **Unit of Individuality:** terms identifying ants, nestmates, colonies, collectives, and superorganisms; how an author specifies the unit being observed or modeled.
2. **Behavior and Identity:** distinctions between a task, an observed behavior, a persistent propensity, and a developmental category.
3. **Power and Labor:** queen, worker, caste, and related labels; whether descriptions imply control mechanisms or simply name biological roles.
4. **Sex and Reproduction:** reproductive and developmental categories; how definitions accommodate variation across taxa and mating systems.
5. **Kin and Relatedness:** pedigrees, demographic assumptions, and relatedness terminology. For example, expected sister relatedness of $r=0.75$ requires an outbred haplodiploid pedigree with one mother and one haploid father; it is not a universal property of colonies.
6. **Economics:** resource, allocation, investment, and related expressions; distinctions between measured energetic expenditure, fitness consequences, and metaphorical usage.

These are predefined organizational categories. A term receiving several labels does not establish that its meaning changed over time. Each domain also requires qualitative annotation before lexical patterns can be interpreted as ambiguity or framing.

## Research Approach

The headline computation analyzes {{CORPUS_PUBLICATIONS}} stored abstracts, yielding {{CORPUS_TOTAL_TOKENS}} processed tokens and {{CORPUS_CANDIDATE_TERMS}} candidates, of which {{CORPUS_DOMAIN_TERMS}} receive domain assignments. Complementary PMC, BHL, and arXiv layers retain separate source identities. The workflow distinguishes corpus frequencies, observed document co-occurrence, vocabulary overlap, context-cluster entropy, and heuristic scores.

Active Inference and multiscale modeling provide a theoretical perspective \cite{friston2010free, friedman2021active}, but the present pipeline does not fit a generative model of scientific language or measure variational free energy. A Markov blanket specifies conditional-independence relationships in a model; it is not a lexical security filter or a biological boundary established by terminology alone.

The contribution is a descriptive workflow, a proposed taxonomy, and explicit questions for subsequent validation. Historical OCR frequencies provide dated source-layer observations rather than proof of conceptual origins or causal reform. Methods and limitations state source custody gaps, convenience-sample retrieval, statistical dependence, and bounded analyses so that interpretation remains tied to the evidence actually produced.
