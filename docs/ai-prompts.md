# AI Prompts for Co-authors

**English** | [简体中文](ai-prompts.zh-CN.md) · [Co-author Guidelines](../CONTRIBUTING.md) · [LaTeX templates](templates/README.md)

Provide the target chapter, neighboring chapter overviews, its preamble, and the reference material before using the shared constraints with one task. Fill in the bracketed fields. Contributors verify AI output; unapproved author inputs remain placeholders.

## Shared Constraints

```text
You are contributing to Course of Computational Physics. Readers know
analysis, linear algebra, ODEs/PDEs, and elementary numerical computation,
but may lack CFD/CEM/plasma or HPC experience.

Target volume/chapter: [fill in].
Provided material: [chapter, dependencies, preamble, references, or code].
Files and scope authorized for editing: [fill in].
Deliverable: [fill in]. If file changes are not requested, propose changes first.

Use concise, objective, connected academic prose. Preserve the author's
claims, chapter structure, equations, derivation order, labels, and citations.
Only make changes authorized by this task; prose editing preserves technical content.
Retain conditions affecting conclusions. Replace self-evaluative or defensive
phrasing with explicit scope, omissions, and search routes. Identify the established
result, unresolved problem, and subsequent use at each conceptual transition.

The author supplies WHY THIS, WHY NOW, and WHAT MATTERS.
AI supports derivations, examples, calculations, comparisons, and experiments.
Mark missing author rationale with [AUTHOR TO COMPLETE: ...] and leave it unfilled.
Retain existing author-approved supplements.
Technical facts, sources, coefficients, code execution, and performance data
must be verifiable. Mark missing sources for verification and unexecuted checks
as not run. Distinguish assumptions, derivations, and measurements.
Reuse the target volume's notation, macros, and bilingual terminology.
List suspected errors or dependency-order issues separately for confirmation.
Maintain authorship per volume; align both covers and PDF author metadata.
Keep revision commentary in this conversation or PR, not in repository revision logs.
```

## 1. Propose a Chapter

```text
Using the supplied three-volume contents and neighboring chapters, propose
a chapter on [topic] in no more than one page.
Locate existing coverage first, identify the unresolved problem, and specify:
1. Proposed position, available results, and prerequisites to supply;
2. The question answered, one core idea, and its later use;
3. Three to six sections, each with a relation, judgment, or calculation to deliver;
4. A minimal checkable example, omitted details, and precise English search terms;
5. Required sources, code/figures, and a bilingual synchronization plan.
Separate source-supported material from modeling choices requiring the author.
Do not draft the chapter or reorder chapters yet.
```

## 2. Edit the AI-native Learning Interface

```text
Read [chapters] and establish their role in the dependency chain.
Edit only the learning interface. Add a chapter overview with information
comparable to 100–250 Chinese characters: established result, unresolved question,
present choice, later use, and core idea, all grounded in existing text.

Classify each location:
A Motivation and steps are clear: leave it unchanged.
B Model selection or conceptual motivation is missing: add an unfilled author area.
C Motivation is clear but algebra, examples, or prerequisites are omitted:
  write a specific AI prompt and follow-up variation.
Each B area has Potential question, Author Supplement, and Core conceptual connection.
Each C prompt names current notation, assumptions, starting point, task,
and checkable output. Name the omitted material and useful search terms.
Use the target volume's existing macros. Volume II studentinput is a reader exercise.
Preserve the body and all equations; place callouts at meaningful transitions.
Summarize added-area counts and author decisions in this conversation.
```

## 3. Revise Academic Prose

```text
Revise the language of [chapter excerpt] without adding physical content.
Identify each paragraph's function, then fix repetition, ambiguous references,
inconsistent terminology, and causal connections.
Replace self-justification such as "we do not attempt rigor here" or
"the reader need not worry" with explicit applicability, retained results,
omitted steps, and search routes.
Preserve periodicity, positive definiteness, smoothness, quadrature accuracy,
and other technical conditions.
If "obviously" or "naturally" masks missing motivation, keep the mathematical
framework and mark an author input rather than inventing an explanation.
Return the revised text in its original format; list technical questions separately.
```

## 4. Synchronize Languages

```text
Translate [Chinese chapter] into English using [English preamble/neighboring chapter].
Preserve section hierarchy, notation, equations, label/ref/eqref/cite keys,
exercises, and callouts one to one.
Establish a terminology mapping, then use natural, concise English syntax.
Translate prose inside mathematics while preserving mathematical relations,
normalization, normals, and sign conventions.
Use CERK = continuous explicit Runge–Kutta.
Keep unapproved author inputs as placeholders and translate approved supplements faithfully.
Check omissions, extra assumptions, meaning changes, and cross-references.
Return English LaTeX; report terminology questions and checks actually run
only in this conversation.
```

## 5. Contribute an Experiment or Code

```text
Design a minimal reproducible experiment for [algorithm or claim],
reusing [existing code path].
First specify the claim, equations, initial/boundary conditions, discretization
and time parameters, error/conservation measures, and checkable expected trends.
Generate measurements by running the experiment; do not prefill numerical results.
Compare against [baseline] on the same physical problem, final time, and comparable accuracy.
Provide dependencies, commands, output structure, and validation tests.
Separate measured time, modeled operations/traffic, and hardware calibration.
Report total cost and error; state GPU transfer scope and MPI rank placement
and same-host/cross-node scope.
Execute only on authorized hardware and directories [fill in].
If authorization is missing, provide the design only.
List commands actually run, results, unexecuted checks, and the supported conclusion scope.
```

## 6. Independent Technical and Pedagogical Review

```text
Review [chapter and neighboring dependencies] without editing files.
List correctness findings first, then pedagogical/navigation issues.
Each finding identifies its location, evidence, impact, and minimal remedy.
Distinguish definite errors, reasonable questions, and missing author rationale.
Check normalization, units, traces/normals, boundary terms, and hypothesis–conclusion
consistency. Distinguish continuous, semidiscrete, and fully discrete claims,
and measured costs from cost models.
Check for undefined objects, unavailable prerequisite results, and circular dependencies.
Check that AI prompts are specific and verifiable and do not replace author motivation.
Compare languages and correspondence between prose, code, and data.
Avoid unsupported verdicts; identify sources not verified and tests not run.
```

## Reader-facing Expansion Examples

These start from the existing mathematical framework and can be used in the corresponding Ask-AI areas.

**Volume 0: GMRES residuals.**

```text
For left-preconditioned GMRES on Ax=b, use this chapter's M^{-1}.
Derive the reduced least-squares problem from the Arnoldi relation, then write
the internally monitored residual and b-Ax.
Use a 3-by-3 diagonal-scaling example to compare them, identifying each norm
and stopping criterion.
Follow-up: keep A and b fixed and scale only the preconditioner.
Which reported quantities change?
```

**Volume I: marginalization and closure.**

```text
Use the chapter's two-particle probability density varrho_2(z1,z2,t),
with z_i=(x_i,v_i). Starting from g1(z1,t)=integral varrho_2 dz2,
integrate the Liouville equation step by step.
Use a smooth pair potential and identify the decay assumptions needed
to eliminate integration boundary terms.
Retain the mean interaction term and locate its dependence on the pair distribution.
Do not assume independence; distinguish exact marginalization from added closure assumptions.
Follow-up: construct two joint distributions with the same g1 but different correlations.
Compare the statistics determined by g1 alone.
```

**Volume II: DG dispersion.**

```text
Use Chapter 7's one-dimensional periodic advection, exact integration,
upwind flux, and p=1 Legendre basis.
Compute M, N, r, and ell from the local weak form, then assemble the Fourier–Bloch symbol.
Use theta=kh and [u]=u^+-u^-; explicitly compute both eigenvalue branches.
Identify the physical branch as theta approaches zero and reproduce
the appendix's phase-speed errors.
Follow-up: apply a chosen RK stability function to the spatial eigenvalues
and report spatial and fully discrete errors separately.
```
