# Course of Computational Physics

Initiated by Harvey Tan.

A concise route from physical models to numerical algorithms and reproducible computation, for readers with a background in mathematics. The three volumes connect modeling assumptions, PDE structure, discretization, matrix solvers, and modern computer architecture.

## Read the Books

| Volume | Chinese PDF | English PDF | Chinese source | English source |
| --- | --- | --- | --- | --- |
| 0: Numerical Linear Algebra and Modern High-Performance Computing | [Read](Course_of_Computational_Physics_Vol0.pdf) | [Read](Course_of_Computational_Physics_Vol0_EN.pdf) | [LaTeX](Vol0_Linear_Algebra_HPC/main.tex) | [LaTeX](Course_of_Computational_Physics_Vol0_EN.tex) |
| I: From Dynamical Reduction to Modern High-Order Discretization | [Read](Course_of_Computational_Physics_Vol1_Revised.pdf) | [Read](Course_of_Computational_Physics_Vol1_EN.pdf) | [LaTeX](Course_of_Computational_Physics_Vol1_Revised.tex) | [LaTeX](Course_of_Computational_Physics_Vol1_EN.tex) |
| II: From Lorentz Covariance to Hyperbolic Conservation Laws | [Read](CourseofComputationPhysics_Vol2_CN.pdf) | [Read](CourseofComputationPhysics_Vol2_EN.pdf) | [LaTeX](CourseofComputationPhysics_Vol2_CN.tex) | [LaTeX](CourseofComputationPhysics_Vol2_EN.tex) |

### Volume 0

Five parts and 29 chapters develop matrix structure, factorization, Krylov methods, preconditioning, multigrid, and Roofline-based performance analysis. Yee-FDTD, DG/FR, FEM, FVM, and LBM connect solver design to concrete discrete operators. Time integration and parallel communication complete the route from one kernel to total solution cost.

Chinese and English editions share [companion code](Vol0_Linear_Algebra_HPC/code_examples/), [figures](Vol0_Linear_Algebra_HPC/figures/), and [measurement records](Vol0_Linear_Algebra_HPC/results/). See the [experiment guide](docs/experiments.md) for dependencies, validation, and timing conventions.

### Volume I

*A Concise Course of Computational Physics: From Dynamical Reduction to Modern High-Order Discretization* contains six parts and 22 chapters. Many-particle dynamics leads to statistical descriptions, kinetic equations, moments, and continuum closure. Function spaces and weak forms lead to finite differences, finite volumes, FEM, spectral methods, DG, FR, VCJH, and mortar coupling. LBM, rarefied gases, MHD, gyrokinetics, meshes, and verification complete the modeling chain.

Chapter 14 connects spatial operators to ADER, continuous explicit Runge--Kutta (CERK), conservative local time stepping (LTS), and implicit--explicit (IMEX) integration. Volume 0 develops the algebraic solution algorithms arising from these discretizations.

### Volume II

Maxwell equations connect differential forms and Lorentz covariance to evolution and constraints, symmetric hyperbolicity, energy estimates, compatible operators, and high-order DG dispersion. Section 5.5 develops RK, symplectic integration, ADER, CERK, LTS, and IMEX methods. Chapter 7 and its Python appendix provide a reproducible one-dimensional DG dispersion experiment.

Each English edition follows its Chinese counterpart in chapter structure, formulas, references, and exercises.

## Learning Routes

Chapter overviews locate each topic in the dependency chain. Conceptual connections identify the motivation for a transition; search terms identify omitted derivations and prerequisites. Specific Ask-AI prompts open routes to calculations, examples, comparisons, and experiments. Assumptions and cited sources provide the basis for checking the resulting work.

## Build and Verify

From the repository root:

```sh
make                     # Chinese and English Volumes 0 and I
make english             # English Volumes 0 and I
make check               # Mathematical, structural, numerical, and PDF checks
```

The build uses XeLaTeX through latexmk, generates the Volume I terminology index, and places delivery PDFs at the repository root. Intermediate files stay in build directories.

Use a TeX distribution with ctex-compatible Chinese fonts, Latin Modern, babel, tcolorbox, pgfplots, listings, needspace, and placeins. Verification requires Python 3, NumPy, SciPy, qpdf, and Poppler tools. The [experiment guide](docs/experiments.md) documents the optional CUDA and MPI toolchains.

Individual targets are available:

```sh
make vol0 vol0-en revised vol1-en
make verify vol0-verify math-verify translations-verify
```

Build Volume II explicitly:

```sh
latexmk -xelatex -outdir=build -interaction=nonstopmode -halt-on-error CourseofComputationPhysics_Vol2_CN.tex
latexmk -xelatex -outdir=build -interaction=nonstopmode -halt-on-error CourseofComputationPhysics_Vol2_EN.tex
```

## Experiments

```sh
python -m pip install -r Vol0_Linear_Algebra_HPC/code_examples/requirements.txt
make vol0-examples        # CPU experiments, figures, and bilingual result tables
make vol0-hardware        # Optional CUDA and same-host MPI experiments
```

These targets refresh measurement records. Recorded timings identify their hardware, implementation, and workload; modeled FLOPs and traffic are kept separate from measured runtime. The [code index](Vol0_Linear_Algebra_HPC/README.md) maps examples to topics.

## Background and Contributions

The project began with a mathematically trained friend's request for a route into physics, alongside an ambition inspired by Landau and Lifshitz's *Course of Theoretical Physics*. Its focus is computational fluid dynamics, computational electromagnetics, and plasma physics.

Contributions may address derivations, numerical verification, terminology, translations, or additional physical domains. Preserve the concise structure, state assumptions, and provide references for new technical material.

## Acknowledgement

Thanks to GPT for assistance in turning the author's ideas into a working manuscript.
