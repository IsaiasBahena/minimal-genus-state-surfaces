# Usage

## Command-Line Interface

The package can be executed directly from the command line.

---

# Gauss Code Input

Compute invariants from a Gauss code:

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

---

# DT Code Input

Compute invariants from a DT code:

```bash
python -m state_surfaces --dt "[[4,6,2]]" --pretty
```

---

# File Input

Read input from a file:

```bash
python -m state_surfaces --file examples/trefoil_gauss.txt --as gauss --pretty
```

or:

```bash
python -m state_surfaces --file examples/trefoil_dt.txt --as dt --pretty
```

---

# Python API

## Using `run_pipeline`

```python
from state_surfaces import run_pipeline

result = run_pipeline(gauss_code=[1, 2, 3, 1, 2, 3])

print(result)
```

Returns a dictionary.

---

## Using `analyze`

```python
from state_surfaces import analyze

result = analyze(gauss_code=[1, 2, 3, 1, 2, 3])

print(result.unoriented_genus)
print(result.crosscap)
```

Returns a structured `StateSurfaceResult` object.

---

# Accepted Input Formats

## Single-component Gauss code

```python
[1, 2, 3, 1, 2, 3]
```

---

## Multi-component Gauss code

```python
[[1, 2], [1, 2]]
```

---

## String notation

```python
"[[1,2],[1,2]]"
```

---

## Single-component DT code

```python
[[4, 6, 2]]
```

or:

```python
[4, 6, 2]
```

---

# Testing

Run the test suite:

```bash
python -m pytest
```

Run regression validation against reference datasets:

```bash
python scripts/compare_against_original.py
```

---

# Examples

Example files are provided in:

```text
examples/
```

including:

```text
trefoil_dt.txt
trefoil_gauss.txt
two_component_link.txt
```
