# Co-author Guidelines

**English** | [简体中文](CONTRIBUTING.zh-CN.md)

These guidelines distill the writing and verification conventions of Volumes 0, I, and II for chapter authors, technical reviewers, translators, and code contributors. The project develops a compact map of computational physics: authors organize the conceptual connections, and AI supports detailed exploration on demand.

**Start here:** [Chapter templates](docs/templates/README.md) · [AI prompts](docs/ai-prompts.md) · [Build instructions](README.md#build-and-verify) · [Experiment conventions](docs/experiments.md)

## 1. Readers and Purpose

Readers know mathematical analysis, linear algebra, ODEs/PDEs, and elementary numerical computation. They may have little experience with CFD, computational electromagnetics, plasma physics, or HPC practice. Make the reasoning behind expert choices accessible.

Organize material around a recognizable chain: **established result → unresolved problem → present choice → resulting capability → later use**. Retain mathematical density while identifying modeling levels, approximation conditions, and variable meanings. Use references, search terms, AI prompts, and code for extended technical detail.

## 2. Roles of the Three Volumes

| Volume | Main chain and deliverable | How new material should connect |
| --- | --- | --- |
| 0 | Discrete equations → matrix structure → factorization and Krylov methods → preconditioning and multigrid → hardware cost | Identify the operator's origin, residual semantics, admissible matrix classes, and total solution cost. See [GMRES](Vol0_Linear_Algebra_HPC_EN/chapters/part03_krylov/ch12.tex) and [communication](Vol0_Linear_Algebra_HPC_EN/chapters/part05_roofline_hpc/ch28.tex). |
| I | Particles → statistics and closure → continuum equations → weak forms and high-order discretization → physical models, meshes, and verification | Explain which information is retained or discarded and which assumptions each reduction or discretization introduces. See [kinetic models](vol1_revised_en/chapters/ch01.tex) and [method composition and time integration](vol1_revised_en/chapters/ch14.tex). |
| II | Maxwell geometry → evolution and constraints → hyperbolicity and energy → compatible discretization and DG dispersion | Distinguish geometric identities, physical input, well-posedness, discrete stability, and propagation accuracy. See the [English source](CourseofComputationPhysics_Vol2_EN.tex). |

Reference the result needed across volumes. Volume I derives algebraic systems, Volume 0 develops their solvers, and Volume II examines structure preservation through Maxwell equations. Propose the location and dependency interfaces before adding chapters or changing their order.

## 3. Language and Argument

- Use concise, objective academic prose. Name the object or question in headings, state the task at paragraph openings, and explain causality in transitions.
- Introduce terms with their standard name and abbreviation; provide Chinese and English terminology in the Chinese edition. Use established search terms.
- Remove self-evaluation about length, difficulty, or author expertise. Express scope through specific omissions and applicability conditions.
- Retain conditions that determine a result: periodic boundaries, regularity, positive definiteness, exact quadrature, or a fixed preconditioner are part of the argument.
- Distinguish definitions, identities, modeling assumptions, asymptotic approximations, algorithmic choices, and measurements. Each inference should have an identifiable basis.
- Introduce why an object is needed before its equation, and interpret the result afterward. Make normalization and initial/boundary conditions easy to locate.

| Wording to revise | Expected approach |
| --- | --- |
| “We do not attempt a complete discussion of this difficult topic.” | “This section retains …; it omits …, which can be found under ….” |
| “The matrix form is obvious.” | “Expanding the unknown in a chosen basis and testing the equations gives finite-dimensional relations between its coefficients.” |
| “This method is more advanced and efficient.” | Identify the baseline, error target, workload, and cost measure, then provide evidence or applicability conditions. |

Language editing preserves the author's claims, equations, derivation order, and chapter structure. Record technical questions separately for author confirmation before changing them.

## 4. Minimum Chapter Structure

1. **Chapter overview:** immediately after the chapter heading, before the body. Aim for 100–250 Chinese characters in Chinese and comparable information in English. Connect the preceding result, remaining problem, present choice, later use, and one core idea.
2. **Learning goals and entry question:** Volumes 0 and I use the existing learning-goal macro, with assessable verbs such as construct, derive, compare, and verify. Volume II retains its established chapter format.
3. **Mathematical framework:** specify objects, assumptions, key relations, and their interpretation. Retain the steps essential to understanding the conclusion.
4. **Minimal example or check:** choose a calculation, limiting case, or example that exposes the mechanism.
5. **Computational or cross-volume interface:** where relevant, identify inputs, outputs, error measures, and costs. Add code when it serves an actual experiment.
6. **Expansion route:** name omitted proofs, algebra, prerequisites, or implementation details, with specific search terms, references, or AI prompts.

These are content responsibilities; keep each volume's established ordering. Place callouts where a conceptual transition or substantial expansion warrants one.

## 5. Author and AI Responsibilities

| Diagnosis | Editing action | Responsibility |
| --- | --- | --- |
| A: motivation and steps are clear | Leave the text unchanged | Avoid redundant callouts |
| B: the reason for selecting a model, variable, or operation is missing | Mark a potential conceptual jump and leave an author input area | The author supplies WHY THIS, WHY NOW, and WHAT MATTERS |
| C: motivation is clear, but a derivation, example, or technical detail is omitted | Write a specific Ask-AI prompt | AI supports SHOW ME, DERIVE IT, GIVE ME AN EXAMPLE, LET ME TRY, and WHAT IF |

B and C may occur together, with distinct roles. Retain existing author-approved supplements. Leave new, unapproved author areas as placeholders.

For Volumes 0 and I, use the existing `authornote` or `conceptbridge` interface:

```text
Potential Conceptual Jump
Potential question: Why move from [established object] to [new object]?
Author Supplement: [AUTHOR TO COMPLETE: explain the need and selection rationale.]
Core conceptual connection: [established object] → [new object]
```

The connection names the endpoints without supplying the missing rationale. Chinese author inputs normally request 80–300 characters. Volume II currently has no `authornote` macro: use a plain draft paragraph with the same fields for author review. Its `studentinput` environment is a reader exercise, not an author placeholder.

An AI prompt identifies the current notation, assumptions, starting point, task, and checkable output, followed by a useful variation. For example:

> For left-preconditioned GMRES applied to `Ax=b`, start from the Arnoldi relation and derive the difference between the internal least-squares residual and the original-system residual. Use this chapter's `M^{-1}`, and show how to recompute `b-Ax` for acceptance. Then construct a diagonal-scaling example comparing the two residuals.

“Explain this section” does not locate the reader's difficulty. The [prompt collection](docs/ai-prompts.md) provides full templates for proposals, learning-interface editing, prose revision, translation, experiments, and review.

## 6. Notation, Terminology, and Sources

- Reuse the target volume's notation and macros. Identify probability, number-density, or mass-density normalization for distribution functions; distinguish mass density from charge density.
- State trace, normal, and jump conventions in DG derivations. The existing one-dimensional convention uses minus for the left trace, plus for the right, and right minus left for the jump. Specify multidimensional normals separately.
- Follow Volume II's prefatory units, metric signature, and orientations. Identify affected Hodge-star signs, component expressions, and boundary terms when changing conventions.
- Use CERK for continuous explicit Runge–Kutta. Describe ADER, CERK, LTS, and IMEX through their respective prediction, continuous-extension, time-scheduling, and stiff-splitting roles.
- Keep formulas, labels, citations, exercises, and technical qualifications aligned between languages. Translate terminology consistently and use natural syntax in the target language.
- Support technical claims with verifiable original papers, textbooks, or official documentation, identifying the chapter, algorithm, DOI, or other precise location. Independently check AI-generated references, coefficients, and derivations.

## 7. Code, Experiments, and Evidence

An experiment specifies the model, initial/boundary conditions, discretization parameters, precision and stopping criteria, commands, and validation measures. Reuse [code_examples](Vol0_Linear_Algebra_HPC/code_examples/) and the [experiment guide](docs/experiments.md); record dependencies and random seeds where applicable.

Compare methods on the same physical problem, final time, and comparable error target. Report error, iteration or update counts, and total cost separately. Distinguish measured runtime, modeled FLOPs/traffic, and hardware calibration. State whether GPU timings include transfers; identify same-host versus cross-node MPI, rank placement, and slowest-rank time.

Limit conclusions to what the implementation tests. The Volume II Fourier–Bloch program checks one-dimensional DG dispersion; same-host MPI checks communication semantics. Three-dimensional, full time-domain, or cross-node claims require corresponding implementations and data.

Confirm permissions and writable directories before hardware or SSH experiments. Remove private host identifiers, paths, and credentials from public records while preserving reproducibility-relevant hardware and timing conventions. Mark unexecuted checks as “not run”; report measurements only when collected.

## 8. Files and Builds

| Content | Chinese location | English location |
| --- | --- | --- |
| Volume 0 chapters | `Vol0_Linear_Algebra_HPC/chapters/` | `Vol0_Linear_Algebra_HPC_EN/chapters/` |
| Volume I chapters | `vol1_revised/chapters/` | `vol1_revised_en/chapters/` |
| Volume II | `CourseofComputationPhysics_Vol2_CN.tex` | `CourseofComputationPhysics_Vol2_EN.tex` |

Use the [volume-specific templates](docs/templates/README.md) with the existing preamble, chapter labels, and bibliography keys. `studyroute` takes two arguments in Volume 0 and three in Volumes I and II. New chapters also require checking main-file inputs, cross-references, and chapter counts in the validators.

```sh
make check
python verification/check_english_editions.py --sources-only
```

`make check` covers the current Volume 0/I builds and mathematical, structural, numerical, and English PDF checks, and checks Volume II's frozen files. After editing Volume II, also build both languages using the [README commands](README.md#build-and-verify), inspect the logs, and review the layout.

`verification/math_reference.json` and `verification/volume2_reference.json` are intentional change baselines. Review mathematical or Volume II differences before updating the relevant baseline and tests, and explain the approved change. Do not regenerate baselines to conceal unintended changes. Guide-only and template-only edits do not require rebuilding book PDFs.

## 9. Collaboration and Submission

Small corrections can be submitted directly as a PR. Propose new chapters, substantial derivations, and cross-volume changes through an Issue or PR first: identify the question, reader entry point, dependencies, deliverables, and bilingual plan. Before a full-chapter collaboration, agree on responsibilities, attribution, and material permissions with the maintainer. Identify actual contributions and third-party material when submitting.

List authors by volume on the cover, keeping the two language editions and PDF author metadata aligned. Harvey Tan is currently credited on all three volumes. Agree on a new co-author's volumes, chapters, and responsibilities in the collaboration proposal, and describe contributions in that volume's preface or acknowledgements. Record translation, technical review, and code contributions by their actual roles. Covers follow Volume 0's centered title-page style: topic, authors, series and volume, then date.

Suggested proposal or PR format:

```text
Topic and target volume/chapter:
Result already available to the reader:
Unresolved question:
New conceptual connection and later use:
Assumptions, notation, equations, and structure preserved:
Omitted details and search terms / AI entry points:
Affected files, code, figures, and reference sources:
Participants, roles, and responsible volumes/chapters:
Chinese/English synchronization:
Validation commands, results, and unexecuted checks:
Modeling rationale or technical judgment requiring author confirmation:
```

Before submission:

- [ ] Dependencies are explicit; terminology and notation are searchable; new claims have sources or checkable derivations.
- [ ] Unapproved author inputs remain placeholders, approved supplements remain intact, and AI prompts have checkable tasks.
- [ ] Prose is concise and connected, technical conditions are intact, and both languages agree.
- [ ] Affected builds, references, equations, and experiments pass their checks; unexecuted checks are identified.
- [ ] The public tree contains current books, necessary code, references, and durable user documentation. Exclude build caches, private records, writing/revision logs, and Legacy editions.

Keep the change rationale and validation results in the PR for review. Repository documentation should serve readers and collaborators over time.
