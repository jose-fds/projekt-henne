---
name: fact-check-data
description: Systematically fact-check and validate a dataset before trusting or publishing it — provenance, control totals, type/missing-value/outlier checks, and verifying LLM-generated results against a hand-coded sample. Use when asked to validate, sanity-check, or fact-check data, or before analysis of an unfamiliar dataset.
---

# Fact-check a dataset

Work through these stages in order. Run checks with pandas (`uv run python`) and report findings with actual numbers. Preserve the original data. Report checks as passed, failed, unverified, or not applicable. Passing quality checks does not establish factual accuracy.

## 1. Learn about the data

Before running any checks, establish provenance:

- Who collected the data, how, when, and why?
- Find a data dictionary or documentation. Note the **stated row count** if published.
- Search for any known issues or caveats documented by the source.

## 2. Control totals

- Sum or count a key column and compare against a published figure.
- The match doesn't need to be exact (revisions, coverage windows), but it must be explainable. If it isn't, stop and investigate before proceeding.

## 3. Check every column against its expected type

Expected types: string (names, categories), integer, float, boolean (True/False, 0/1), date (`YYYY-MM-DD`, `DD-MM-YYYY`).

For each column verify:

- One data type per column — flag mixed types.
- Expected categories where applicable (list the values found vs. expected).
- Missing values: null, empty strings, `NaN` — count them per column.
- Weird/sentinel values: `-999`, placeholders, impossible zeros.
- Units: millions vs. billions, kg vs. m³ — confirm what the numbers actually represent.

## 4. Numeric columns

- Distribution: min, max, median, mean.
- Unrealistic outliers? Investigate, don't just delete.
- Check percentages against their expected range; percentage changes can exceed 100% or be negative.
- Values with thousand separators (`5,000`) parsed as strings, not numbers.

## 5. String columns

- Different spellings of the same name or category, including case variants (`USA` / `usa` / `U.S.`).
- Valid format where one exists (e.g. ZIP codes).
- Trailing or leading whitespace.

## 6. Rows

- Duplicate rows.
- Mostly empty rows.
- Actual row count vs. expected/stated count.

## 7. Columns

- Mostly empty columns.
- Sums of numeric columns (another form of control total).
- Logical rules between columns, e.g. start date ≤ end date.

## 8. Fact-checking LLM output on data

### 8.1. Manual testing
Instruct the user to verify the raw data or analysis **by hand**:

1. Prepare a **random subset** (about 100 rows) for checking against original sources, or select key analysis results for manual recalculation.
2. Give the user a short, concrete verification procedure: what to compare, which sources to use, and how to record discrepancies.
3. Ask the user to report their findings. Until then, mark the manual check as **pending**, not passed.

The agent's own review does not count as independent human verification.

### 8.2. Automated testing

Write the checks as code so they run on their own and fail loudly. Use the `pytest` library.

- **Data integrity tests**: turn the checks from sections 3–7 into assertions the dataset must pass
- **Unit tests**: test one part of your code at a time. Each function gets a known input and an expected output
- **Plant a known error** (mutation testing): deliberately break one number in a temporary copy of the dataset, run the tests, and confirm they fail.
