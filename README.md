# Tobacco Membership Information Extractor

This repository supports the reconstruction of literature-derived tables and the standardized extraction of tobacco soil suitability membership-function data. Each table is processed independently, extracted records are converted from JSON to Excel for manual verification, and summary statistics are calculated from the approved workbook.

## Prerequisites

- Python 3
- `pandas`
- `numpy`
- `openpyxl`

Install the Python dependencies with:

```bash
python -m pip install pandas numpy openpyxl
```

Run all commands from the repository root.

## Workflow and directories

```text
data/input/                              # Source table images

outputs/stage1_reconstruction/          # Reconstructed tables (JSON)

outputs/stage2_extraction/               # Standardized records (JSON)

outputs/extracted_records_draft.xlsx     # JSON-to-Excel output

outputs/extracted_records_approved.xlsx  # Reviewed input for statistics

outputs/threshold_statistics.xlsx        # Statistical results

scripts/json_to_excel.py                 # Convert extracted JSON to Excel

scripts/threshold_statistics.py          # Generate final rule statistics

examples/                                # Example workflow files
```

The workflow is:

```text
Table image → Stage 1 reconstruction → Stage 2 extraction → Draft Excel → Human review → Approved Excel → Statistics
```

Do not run the JSON-to-Excel conversion or threshold statistics until the preceding stage has been completed and checked.

## 1. Prepare the input tables

Place cropped table images in `data/input/`. Each file must have a unique filename stem (e.g., `D001.png`).

Input files are read-only and must not be modified during extraction. Each image is processed independently, and results must remain separate in both Stage 1 and Stage 2.

## 2. Run the extraction Skill

Invoke the `tobacco-membership-information-extractor` Skill with the following prompt:

```text
Use the `tobacco-membership-information-extractor` Skill.

Process all table images in:

data/input/

Run Stage 1 and Stage 2 sequentially for each input file.

Requirements:

- Follow all Stage 1 and Stage 2 rules defined in `SKILL.md`.
- Use the schemas and mapping files referenced by the Skill.
- Process each input independently.
- Use a strict one-input-one-output workflow.
- Preserve the original input filename stem for the corresponding Stage 1 and Stage 2 outputs.
- Do not merge results from different input files.
- Use each Stage 1 reconstructed JSON as the only input for its corresponding Stage 2 extraction.
- If any information is uncertain or ambiguous, do not infer or silently correct it; mark it for manual review.
- Do not run the JSON-to-Excel conversion or threshold statistics unless explicitly requested.
- Do not modify input files, SKILL.md, schemas, mapping files, or few-shot examples.

After processing, report for each input file:

- input image
- Stage 1 output file
- Stage 2 output file
- whether manual review is required
```

For an input named `data/input/D001.png`, the required one-to-one file flow is:

```text
data/input/D001.png
outputs/stage1_reconstruction/D001.json
outputs/stage2_extraction/D001.json
```

Stage 1 reconstructs each source table without interpretation or standardization. Stage 2 uses only the corresponding Stage 1 JSON to standardize supported indicators, function types, units, and thresholds. Both stages retain the original filename stem.

Unsupported or ambiguous information must not be inferred or silently corrected. Leave unresolved values as specified in `SKILL.md` and the schemas, and flag them for manual review.


## 3. Convert the extracted JSON and review it

After completing Stage 2, convert all JSON files in `outputs/stage2_extraction/` to a draft Excel workbook:

```bash
python scripts/json_to_excel.py
```

The script combines all Stage 2 records and writes:

```text
outputs/extracted_records_draft.xlsx
```

> **Warning:** Rerunning the script will overwrite outputs/extracted_records_draft.xlsx

Review each record against the Stage 2 JSON, Stage 1 JSON, and source table image. Verify that:

* `table_id` matches the source paper.
* `indicator_std` is correctly standardized as `pH`, `OM`, `TN`, `AP`, or `AK`.
* `function_type_std` is correctly assigned as `parabolic` or `S-type`.
* `x1`–`x4` contain source-supported thresholds in the correct order.
* `unit` matches the source and the mapping defined in `SKILL.md`.
* Flagged items are resolved from source evidence only.

The statistics script requires:

```text
table_id
indicator_std
function_type_std
x1
x2
x3
x4
unit
```

After review, save the approved workbook as:

```text
outputs/extracted_records_approved.xlsx
```

## 4. Calculate threshold statistics

Before running the statistics script, review the `final_functions` mapping in `scripts/threshold_statistics.py` and keep only approved indicator–function combinations:

```python
final_functions = {
    "pH": "parabolic",
    "OM": "parabolic",
    "TN": "parabolic",
    "AP": "S-type",
    "AK": "S-type",
}
```

Supported function types are:

* `parabolic`: `x1`–`x4`
* `S-type`: `x1` and `x4`

Ensure that `outputs/extracted_records_approved.xlsx` contains the approved records. Then run:

```bash
python scripts/threshold_statistics.py
```

For each indicator, function type, and parameter, the script first calculates the within-paper median using `table_id` as the grouping field, then reports `N_papers`, median, `Q1`, `Q3`, `IQR`, and the bootstrap 95% confidence interval of the median (5,000 resamples; seed = 42).

Results are written to:

```text
outputs/threshold_statistics.xlsx
```

> **Warning:** Rerunning the script will overwrite the existing statistics file.

📧 If you have any questions, please contact: xinkaiyu@webmail.hzau.edu.cn
