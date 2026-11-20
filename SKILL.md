---
name: tobacco-membership-information-extractor
description: 
  Reproducibly reconstruct scientific literature tables and extract
  standardized tobacco soil suitability membership-function information.
metadata:
  author: Xinkai Yu
  version: "1.1.0"
---

# Tobacco Membership Information Extractor

##  Objective

- Extract reproducible and traceable tobacco soil suitability information from scientific literature tables.

- The workflow contains two separate stages:
  1. Table structure reconstruction.
  2. Target membership-information extraction and standardization.

- Do not infer information that is not explicitly supported by the source.

---


##  Required inputs

Each input table should include:

- a cropped table image,
- a paper ID,

Input images should contain only the target table whenever possible.

The original input files must never be modified.

---
## Framework
### 1. Table reconstruction

#### 1.1 Responsibility

Reconstruct the original structure and content of the literature table.

#### 1.2 Requirements

Preserve:

- column headers,
- row headers,
- hierarchical headers,
- merged-cell relationships,
- original cell text,
- blank or unreadable cells.

#### 1.3 Restrictions

During Stage 1:

- do not normalize indicator names,
- do not normalize units,
- do not classify membership-function types,
- do not infer missing values,
- do not add information that is absent from the table.

Missing or unreadable information must be represented as `null`.

#### 1.4 Output

Save the reconstructed table as structured JSON in:

`outputs/stage1_reconstruction/`

The output must conform to:

`schemas/table_reconstruction.schema.json`

### 2. Target field extraction

#### 2.1 Responsibility

Extract and standardize tobacco soil suitability membership-function
information from the reconstructed Stage 1 JSON.

#### 2.2 Indicator standardization

Extract only records relevant to the following indicators:

- pH
- OM
- TN
- AP
- AK

Use:

`references/indicator_mapping.yaml`

Do not create new indicator categories.

#### 2.3 Function-type standardization

Standardize membership-function types to:

- parabolic
- S-type

Use:

`references/function_mapping.yaml`

First, standardize the function type using the mapping rules.

If no valid mapping can be found, use the extracted threshold pattern as an auxiliary rule:

- If `X1`, `X2`, `X3`, and `X4` are all available, classify the function type as `parabolic`.
- If only two threshold values are available and are standardized as `X1` and `X4`, with `X2` and `X3` set to `null`, classify the function type as `S-type`.

Do not use the threshold pattern to overwrite a function type that has already been successfully standardized by the mapping rules.

If the function type still cannot be determined, mark the record for manual review.

#### 2.4 Unit standardization

Standardize units only according to:

`references/unit_mapping.yaml`

Do not convert numerical values unless an explicit conversion rule exists.

If the Unit cannot be determined from the source, mark the record for manual review.

#### 2.5 Threshold extraction

Extract x1, x2, x3, and x4 only when they are supported by the source.

If four threshold values are explicitly provided, extract them as `x1`, `x2`, `x3`, and `x4` and require:

`x1 < x2 < x3 < x4`

If the source provides exactly two thresholds that are clearly defined as the lower and upper thresholds of a two threshold function, assign them to `x1` and `x4`, set `x2` and `x3` to `null`, and require:

`x1 < x4`

Do not infer additional threshold values.

If the threshold assignment or ordering is uncertain, do not modify the extracted values. Mark the record for manual review.

#### 2.6 Evidence requirement

Every extracted record must retain source evidence that supports the
indicator, function type, and threshold information.

Do not generate evidence text that does not exist in the source.

#### 2.7 Output

Save Stage 2 records in:

`outputs/stage2_extraction/`

The output must conform to:

`schemas/target_extraction.schema.json`

Each input table must be processed independently.

Use a one-input-one-output workflow.

Do not merge outputs from different input tables.

Preserve the input filename stem for the corresponding Stage 1 and Stage 2 output files.

---

### 3. Convert, check and review extracted records

Convert all Stage 2 JSON files to a draft workbook:

`python scripts/josn_to_excel.py`

Input:

`outputs/stage2_extraction/`

Output:

`outputs/extracted_records_draft.xlsx`

Run quality control before manual review:

`python "scripts/Extraction Quality Control.py"`

Input:

`outputs/extracted_records_draft.xlsx`

Output:

`outputs/manual_review_records.xlsx`

Review the flagged records, correct the draft workbook using source evidence only, and verify `table_id`, indicator, function type, thresholds, and units.

After all flagged items are resolved, save the corrected workbook as:

`outputs/extracted_records_approved.xlsx`

Use only the approved workbook for statistical analysis.

---

### 4. Threshold statistics

Review the `final_functions` mapping in `scripts/threshold_statistics.py` and keep only approved indicator–function combinations.

Use:

* `parabolic`: `x1`-`x4`
* `S-type`: `x1` and `x4`

Input:

`outputs/extracted_records_approved.xlsx`

Run:

`python scripts/threshold_statistics.py`

Using `table_id` as the paper-grouping field, the script calculates within-paper medians and reports `N_papers`, median, `Q1`, `Q3`, `IQR`, and bootstrap 95% confidence intervals (5,000 resamples; seed = 42).

Output:

`outputs/threshold_statistics.xlsx`

---

### 5. Core operating rules

Always follow these rules:

1. Preserve source information and literature traceability.
2. Do not infer or silently correct unsupported information.
3. Keep Stage 1 reconstruction separate from Stage 2 standardization.
4. Process each input independently through Stage 1 and Stage 2.
5. Resolve flagged records from source evidence during manual review.
6. Run quality control before manual review and threshold statistics.
7. Use only the corrected, approved workbook for threshold statistics.
8. Do not run JSON-to-Excel conversion, quality control, or threshold statistics unless explicitly requested.


