# Course of Computational Physics

Initiated by Harvey Tan.

A compact computational-physics knowledge map for readers with a background in mathematics and numerical computation. The text connects model assumptions, PDE structure, discretization, and solver design. Chapter overviews explain dependencies; targeted prompts provide routes to derivations, examples, and numerical experiments while keeping the main exposition concise.

## Read the Volumes

| Volume | Language | PDF | LaTeX source |
| --- | --- | --- | --- |
| I: From Particles to Computational Meshes | Chinese | [Read](CourseofComputationPhysics_Vol1_CN.pdf) | [Source](CourseofComputationPhysics_Vol1_CN.tex) |
| I: From Particles to Computational Meshes | English, earlier abridged draft | Not bundled | [Source](CourseofComputationPhysics_Vol1_EN.tex) |
| II: From Lorentz Covariance to Hyperbolic Conservation Laws | Chinese | [Read](CourseofComputationPhysics_Vol2_CN.pdf) | [Source](CourseofComputationPhysics_Vol2_CN.tex) |
| II: From Lorentz Covariance to Hyperbolic Conservation Laws | English | [Read](CourseofComputationPhysics_Vol2_EN.pdf) | [Source](CourseofComputationPhysics_Vol2_EN.tex) |

The two Volume II editions share chapter structure, equation labels, exercises, figures, and code. The earlier English Volume I draft is not yet synchronized with the revised Chinese edition.

See the [editing report (Chinese)](EDITING_REPORT.md) for the revision scope, learning-prompt counts, and verification notes.

### Volume I

The modeling chain runs from deterministic many-particle dynamics through probability distributions, marginalization, kinetic equations, moments, and continuum closure. It then connects asymptotic regimes to numerical transport, discretization, matrix structure, Krylov methods, preconditioning, multigrid, and mesh design.

The time-integration section introduces ADER, continuous explicit Runge--Kutta (CERK), and conservative local time stepping (LTS). It distinguishes within-step prediction from shared-flux conservation and physical-time accuracy.

### Volume II

Maxwell equations provide a common example linking differential forms and Lorentz covariance to evolution/constraint decomposition, symmetric hyperbolicity, energy estimates, finite-volume fluxes, compatible discrete operators, and high-order DG dispersion.

Chapter 5.5 connects the method of lines to RK and symplectic integration, ADER, CERK, LTS, and implicit--explicit (IMEX) methods. The conductive Maxwell example separates wave propagation from stiff Ohmic relaxation and identifies the stability, charge-compatibility, and energy checks needed for the split. Chapter 7 and its Python appendix provide a reproducible one-dimensional DG dispersion experiment.

## Learning Structure

- **Chapter overviews** locate each chapter in the dependency chain.
- **Potential conceptual jumps** in Volume I identify questions and their core conceptual connections. Author supplements are editable drafts.
- **Further detail and search terms** state what has been omitted and identify terminology for follow-up study.
- **Ask AI** prompts specify a derivation, example, comparison, or computational check using the surrounding notation.
- **Active recall and concept checks** in Volume II test understanding before implementation.

The author supplies motivation, assumptions, and conceptual connections. AI-assisted work develops the intermediate steps and examples; results should be checked against the stated conventions and cited sources.

## Build

Use a TeX distribution with XeLaTeX, Chinese fonts supported by `ctex`, and the packages used in the sources, including `tcolorbox`, `pgfplots`, `listings`, `needspace`, `placeins`, and Latin Modern.

With `latexmk`:

```sh
latexmk -xelatex -outdir=build -interaction=nonstopmode -halt-on-error CourseofComputationPhysics_Vol1_CN.tex
latexmk -xelatex -outdir=build -interaction=nonstopmode -halt-on-error CourseofComputationPhysics_Vol2_CN.tex
latexmk -xelatex -outdir=build -interaction=nonstopmode -halt-on-error CourseofComputationPhysics_Vol2_EN.tex
```

Alternatively, run `xelatex -interaction=nonstopmode -halt-on-error <file>.tex` repeatedly until the table of contents and cross-references are stable, usually two or three passes. The commands above place build artifacts in `build/`; checked-in PDFs are available at the repository root.

The DG dispersion code printed in Volume II requires Python 3 and NumPy. It evaluates a semidiscrete Fourier--Bloch symbol, not a full Maxwell field solver.

## Background and Contributions

The project began with a mathematically trained friend's request for a route into physics, alongside an ambition inspired by Landau and Lifshitz's *Course of Theoretical Physics*. Its present emphasis is computational fluid dynamics, computational electromagnetics, and plasma physics.

Contributions may address derivations, numerical verification, terminology, translations, or additional domains such as first-principles methods, nonlinear continuum mechanics, and explosion mechanics. Please preserve the compact structure, make assumptions explicit, and provide references for new technical material.

## Acknowledgement

Thanks to GPT for assistance in turning the author's ideas into a working manuscript.
