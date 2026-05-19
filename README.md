# minimal-genus-state-surfaces

Algorithms for computing minimal genus state surfaces from Gauss codes and Dowker–Thistlethwaite (DT) codes.

This repository implements the recursive smoothing algorithm developed for studying state surfaces of knots and links using Gauss codes. The package computes:

- Kauffman state codes,
- unoriented genus,
- crosscap number,
- simplicity,
- and two-sidedness.

The implementation supports:

- single-component knots,
- multi-component links,
- recursive 1-gon, 2-gon, and 3-gon smoothings,
- triangle and anti-triangle smoothing branches,
- DT-to-Gauss conversion,
- command-line usage,
- and regression testing against precomputed datasets.

---

# Installation

Clone the repository:

```bash
git clone https://github.com/IsaiasBahena/minimal-genus-state-surfaces.git
cd minimal-genus-state-surfaces
```

Install in editable mode:

```bash
pip install -e .
```

Install test dependencies:

```bash
pip install -r requirements.txt
```

---

# Quick Start

## Run from the command line

Compute invariants directly from a Gauss code:

```bash
python -m state_surfaces --gauss "[1,2,3,1,2,3]" --pretty
```

Example output:

```json
{
  "gauss_code": [[1, 2, 3, 1, 2, 3]],
  "state_code": [(1, 2), (3, 2), (3, 1)],
  "unoriented_genus": 1,
  "crosscap": 1,
  "simple": true,
  "two_sided": false
}
```

Run from a DT code:

```bash
python -m state_surfaces --dt "[[4,6,2]]" --pretty
```

Read from a file:

```bash
python -m state_surfaces --file examples/trefoil_gauss.txt --as gauss --pretty
```

---

# Python API

## High-level pipeline

```python
from state_surfaces import run_pipeline

result = run_pipeline(gauss_code=[1, 2, 3, 1, 2, 3])

print(result)
```

## Structured API

```python
from state_surfaces import analyze

result = analyze(gauss_code=[1, 2, 3, 1, 2, 3])

print(result.unoriented_genus)
print(result.crosscap)
```

---

# Input Formats

## Gauss Codes

Single-component knot:

```python
[1, 2, 3, 1, 2, 3]
```

Multi-component link:

```python
[[1, 2], [1, 2]]
```

String notation is also accepted:

```python
"[[1,2],[1,2]]"
```

Negative labels are normalized automatically using absolute values.

---

## DT Codes

Single-component DT code:

```python
[[4, 6, 2]]
```

Flat single-component notation is also accepted:

```python
[4, 6, 2]
```

Multi-component DT codes:

```python
[[6, 10], [8, 2, 4]]
```

---

# Algorithm Overview

The smoothing algorithm recursively simplifies Gauss codes using:

1. 1-gon smoothings,
2. 2-gon smoothings,
3. triangle smoothings,
4. anti-triangle smoothings.

At each recursive 3-gon branch, the algorithm evaluates both triangle and anti-triangle smoothing outcomes and selects the branch producing minimal unoriented genus.

The final state code is then used to compute:

- unoriented genus,
- crosscap number,
- simplicity,
- and two-sidedness.

---

# Repository Structure

```text
.github/workflows/     GitHub Actions CI
data/                  Reference CSV datasets
docs/                  Additional documentation
examples/              Example input files
scripts/               Utility and validation scripts
src/state_surfaces/    Main package source code
tests/                 Regression and unit tests
```

Important modules:

```text
pipeline.py            High-level orchestration
core.py                Public Python API
gauss_io.py            Gauss-code normalization
dt_to_gauss.py         DT-to-Gauss conversion
genus.py               Genus computations
nonorientable.py       Crosscap / sidedness / simplicity
smoothing/             Recursive smoothing routines
```

---

# Testing

Run all tests:

```bash
python -m pytest
```

Run regression verification against reference datasets:

```bash
python scripts/compare_against_original.py
```

The comparison script validates the current implementation against precomputed CSV outputs for knots and links.

---

# Example Files

The `examples/` directory contains:

```text
trefoil_dt.txt
trefoil_gauss.txt
two_component_link.txt
```

These can be used directly with the CLI.

---

# Research Context

This repository accompanies ongoing research on state surfaces, Gauss codes, and minimal genus algorithms in knot theory.

The implementation focuses on reproducibility and exact agreement with previously verified state-code datasets.

---

# Citation

If you use this software in academic work, please cite the associated paper once available.

Citation metadata is provided in:

```text
CITATION.cff
```

---

# License

This project is licensed under the MIT License.

See:

```text
LICENSE
```

---

# Authors

- Isaias Bahena
- Thomas Kindred
- Jason Parsley