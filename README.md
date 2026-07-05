# Concentric Magic Squares — Mystimath

This folder contains experimental Python scripts related to **concentric magic squares**, also known in French as **carrés magiques concentriques** or **carrés magiques à enceintes**.

The goal is not to publish a complete editorial database of selected squares, but to document:

- the definition used in the Mystimath project;
- reproducible generation methods;
- validation rules;
- experimental counts for small orders;
- methodological limits.

The editorial JSON files used by the Mystimath website are not included in this public folder.

## 1. Definition used here

In this repository, a concentric magic square of odd order `n` is a normal magic square using all integers from `1` to `n²`, such that each central odd-order subsquare is also magic.

For example, an order `7` concentric magic square contains:

```text
7x7 square
└── 5x5 central magic subsquare
    └── 3x3 central magic subsquare
````

For an odd normal square of order `n`, the center is:

```text
center = (n² + 1) / 2
```

If a central subsquare of order `k` is magic and centered on the same pivot, its magic constant is:

```text
M_k = k × center
```

Example for order `7`:

```text
center = 25

3x3 constant = 3 × 25 = 75
5x5 constant = 5 × 25 = 125
7x7 constant = 7 × 25 = 175
```

## 2. Public and private data

This folder intentionally separates reproducible scripts from the editorial database.

Published:

```text
README.md
generate_concentric_odd_square.py
count_concentric_odd_squares.py
results/
notes/
```

Not published:

```text
generated/
private/
*.local.json
```

The generated JSON files are ignored by Git because they belong to the local editorial workflow of the Mystimath website.

## 3. Scripts

### `generate_concentric_odd_square.py`

Generates concentric magic squares of odd order using complementary borders.

Example:

```bash
python concentric-magic-squares/generate_concentric_odd_square.py --order 9
```

To print the generated square in the console:

```bash
python concentric-magic-squares/generate_concentric_odd_square.py --order 9 --print
```

To generate several orders:

```bash
python concentric-magic-squares/generate_concentric_odd_square.py --orders 7 9 11 13 15
```

To export private JSON files locally:

```bash
python concentric-magic-squares/generate_concentric_odd_square.py --orders 9 11 13 15 --out-dir concentric-magic-squares/generated
```

The `generated/` folder is ignored by Git.

### `count_concentric_odd_squares.py`

Counts a strict family of concentric magic squares built by complementary centered borders.

Example:

```bash
python concentric-magic-squares/count_concentric_odd_squares.py --orders 5 7
```

This count concerns the strict construction family implemented in the script. It should not be presented as the complete historical count of all possible concentric or bordered magic squares under every possible definition.

## 4. Validation rules

A generated square is considered valid if:

1. it uses all integers from `1` to `n²`;
2. it has no duplicate values;
3. its center is `(n² + 1) / 2`;
4. the full `n×n` square is magic;
5. each central odd-order subsquare is magic;
6. each central subsquare uses the expected centered interval.

Example for order `9`:

```text
1..81 full square
center = 41

3x3 values: 37..45, constant 123
5x5 values: 29..53, constant 205
7x7 values: 17..65, constant 287
9x9 values: 1..81, constant 369
```

## 5. Public results

The `results/` folder contains public summaries.

Recommended files:

```text
results/count-orders-5-7.txt
results/validation-summary-orders-7-15.txt
```

The validation summary should not include full generated grids if the editorial database is meant to remain private.

To generate a validation summary without printing grids:

```bash
python concentric-magic-squares/generate_concentric_odd_square.py --orders 7 9 11 13 15 > concentric-magic-squares/results/validation-summary-orders-7-15.txt
```

To generate count results:

```bash
python concentric-magic-squares/count_concentric_odd_squares.py --orders 5 7 > concentric-magic-squares/results/count-orders-5-7.txt
```

## 6. Historical note

Concentric magic squares are related to the historical family of **bordered magic squares** or **carrés magiques à enceintes**.

A method for constructing bordered magic squares of even and odd order is mentioned in the tradition associated with El-Bouni, who died in 1225, and was later analyzed by Carra de Vaux.

The present scripts are not claimed to reproduce a specific historical construction. They are experimental Mystimath scripts designed to generate and validate a strict modern family of concentric magic squares.

## 7. Limits

This project uses a precise computational definition.

The generated and counted family is based on:

* odd orders;
* normal entries `1..n²`;
* centered intervals for each subsquare;
* complementary pairs;
* successive borders.

Therefore, the counts produced here should be described as counts of this strict computational family, not as universal counts of every possible bordered or concentric magic square in the broad historical sense.

## 8. Mystimath objective

The purpose of this folder is to make the Mystimath work more transparent and reproducible.

The website may present selected visualizations, articles and editorial structures, while this repository documents the scripts and verification methods behind part of the work.


