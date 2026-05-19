# Internals

## Package Structure

The package follows a modular `src/` layout:

```text
src/state_surfaces/
```

Main modules:

```text
core.py
pipeline.py
gauss_io.py
dt_to_gauss.py
genus.py
nonorientable.py
```

Recursive smoothing logic is implemented in:

```text
smoothing/
```

---

# High-Level Pipeline

The primary workflow is:

```text
Input
  ↓
Normalization
  ↓
Recursive smoothing
  ↓
State code generation
  ↓
Invariant computation
```

The main entry point is:

```python
run_pipeline(...)
```

implemented in:

```text
pipeline.py
```

---

# Input Normalization

Gauss-code normalization is handled by:

```text
gauss_io.py
```

Responsibilities:

- parsing string representations,
- converting flat lists into component form,
- normalizing crossing labels,
- validating supported formats.

DT-code conversion is implemented in:

```text
dt_to_gauss.py
```

---

# Recursive Smoothing

The recursive algorithm is implemented in:

```text
pipeline._process_branch(...)
```

The algorithm repeatedly searches for:

1. 1-gons,
2. 2-gons,
3. 3-gons.

When a 3-gon is found:

- the triangle smoothing branch is evaluated,
- the anti-triangle smoothing branch is evaluated,
- both branches recurse independently,
- the branch with minimal unoriented genus is selected.

---

# Smoothing Modules

## one_gon.py

Implements:

- 1-gon detection,
- 1-gon smoothing.

---

## two_gon.py

Implements:

- 2-gon detection,
- 2-gon smoothing,
- single-component and multi-component cases.

---

## three_gon.py

Implements:

- 3-gon detection only.

Triangle and anti-triangle smoothing logic are separated intentionally.

---

## three_gon_triangle.py

Implements:

- triangle smoothing,
- triangle-pair construction,
- triangle state-circle construction.

---

## three_gon_anti_triangle.py

Implements:

- anti-triangle smoothing,
- anti-triangle pair chaining,
- usage-count constraints,
- consecutive same-component restrictions.

---

# State Codes

State codes are represented as:

```python
list[tuple[int, ...]]
```

Each tuple represents a single state circle.

Example:

```python
[(1, 2), (3, 2), (3, 1)]
```

---

# Invariant Computation

## genus.py

Computes unoriented genus using:

```text
g = 1 + c - s
```

where:

- `c` = crossing count,
- `s` = number of state circles.

---

## nonorientable.py

Computes:

- simplicity,
- two-sidedness,
- crosscap number.

---

# Testing Philosophy

The repository emphasizes regression stability.

Regression validation is performed using:

```text
scripts/compare_against_original.py
```

which compares current outputs against large precomputed reference CSV datasets stored in:

```text
data/
```

This ensures that refactoring preserves exact algorithm behavior.
