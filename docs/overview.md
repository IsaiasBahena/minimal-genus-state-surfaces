# Overview

## Introduction

`minimal-genus-state-surfaces` is a Python package for computing state surfaces and related topological invariants from Gauss codes and Dowker–Thistlethwaite (DT) codes.

The repository implements a recursive smoothing algorithm based on:

- 1-gon smoothings,
- 2-gon smoothings,
- triangle smoothings,
- anti-triangle smoothings,

with the goal of constructing state codes corresponding to minimal genus state surfaces of knots and links.

The package supports:

- single-component knots,
- multi-component links,
- cyclic Gauss-code processing,
- recursive branch evaluation,
- DT-to-Gauss conversion,
- command-line usage,
- and reproducible regression testing.

---

# Core Concepts

## Gauss Codes

A Gauss code records the order in which crossings are encountered while traversing a knot or link diagram.

Example:

```python
[1, 2, 3, 1, 2, 3]
```

represents a single-component knot.

Multiple components are represented as:

```python
[[1, 2], [1, 2]]
```

---

## State Codes

A state code is the output produced by the recursive smoothing algorithm.

Each tuple represents a state circle.

Example:

```python
[(1, 2), (3, 2), (3, 1)]
```

---

## Recursive Smoothing

The algorithm recursively simplifies Gauss codes using:

1. 1-gon smoothings,
2. 2-gon smoothings,
3. triangle smoothings,
4. anti-triangle smoothings.

When a 3-gon is detected, the algorithm evaluates both smoothing branches recursively and selects the branch with minimal unoriented genus.

---

# Computed Invariants

The package computes:

## Unoriented Genus

Computed using:

```text
g = 1 + c - s
```

where:

- `c` = number of crossings,
- `s` = number of state circles.

---

## Crosscap Number

Computed from:

- unoriented genus,
- simplicity,
- and two-sidedness.

---

## Simplicity

A state surface is considered simple if no unordered pair of crossings appears in more than one distinct state circle.

---

## Two-Sidedness

Two-sidedness is determined using a bipartite-style condition on state circles.

---

# Repository Goals

This repository focuses on:

- reproducibility,
- exact regression agreement,
- modular implementation,
- and research-oriented clarity.
