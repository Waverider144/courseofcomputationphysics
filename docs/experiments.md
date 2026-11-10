# Computational Experiments

Run commands from the repository root. CPU examples require Python 3, NumPy, SciPy, and Matplotlib; CUDA and MPI examples additionally require their compilers and access to the corresponding execution resources.

## CPU Experiments

```sh
python -m pip install -r Vol0_Linear_Algebra_HPC/code_examples/requirements.txt
make vol0-examples
make check
```

The CPU target regenerates measurement JSON, figures, and Chinese and English result tables. Mathematical checks cover LU, Arnoldi, GMRES, CG, DG/FR equivalence, FEM operator action, lattice moments, mortar coupling, gyroaveraging, and Yee divergence and energy identities.

Full evolution examples include periodic Yee waves, DG transport, first-order upwind FVM, and periodic BGK--LBM. Manufactured algebraic right-hand sides test solvers; continuous exact solutions test PDE discretization error.

## CUDA and MPI

```sh
make vol0-hardware
```

The runner compiles CUDA and MPI sources, executes short validation cases, checks results, and writes hardware records. CUDA builds use an explicit native target. The MPI examples compare one and two ranks on the same host; cross-node scaling requires a separate experiment.

Configure compilers and runtime libraries in the shell environment. The runner locates nvcc and MPI tools through PATH. A recognized CUDA/glibc rsqrt declaration conflict triggers a retry with the recorded feature-test flags and the selected host compiler. The general-field CPU comparison checks numerical results after compilation.

For a remote session, choose an authorized parent directory and create a dedicated experiment folder beneath it. Keep source, binaries, temporary files, caches, and results inside that folder. Invoke the runner on that host with explicit boundaries:

```sh
python code_examples/run_accelerators.py \
  --remote --allowed-root "$AUTHORIZED_ROOT" \
  --workspace "$EXPERIMENT_DIR" --gpu-index 0
```

The supplied workspace must resolve strictly below the authorized root. Set TMPDIR and any toolchain-specific cache configuration consistently when preparing the session. No SSH endpoint is embedded in the source.

## Timing and Work Models

- CPU arrays use double precision and single-thread BLAS unless the record states otherwise.
- Setup, advancement, GPU transfers, and maximum-rank MPI times are separate fields.
- Verification and output are outside advance timings.
- Python Yee uses the explicit-difference count of 42 FLOPs per cell-step; fused constant-coefficient CUDA/MPI uses 30.
- Semantic traffic, ideal reuse, and measured time are separate quantities. DRAM-counter fields are null when counters were not used.
- The Roofline figure is a labeled schematic; hardware roofs require calibration.
- Fixed-degree-of-freedom throughput and fixed-error total time answer different questions.
- GPU records use a fixed step count at different final times, so their error ratio is interpreted separately from a convergence study.
- Published host and workspace identifiers are anonymized; numerical measurements and hardware/software characteristics are retained.

Refresh bilingual tables from existing data without rerunning benchmarks:

```sh
python Vol0_Linear_Algebra_HPC/code_examples/render_results.py
python verification/render_english_results.py
```

## Volume II Dispersion Example

The Python appendix uses NumPy to evaluate a one-dimensional semidiscrete Fourier--Bloch DG symbol. It reports modal frequency and phase errors. The tabulated symbol calculation and a time-evolving field simulation are distinct experiments.
