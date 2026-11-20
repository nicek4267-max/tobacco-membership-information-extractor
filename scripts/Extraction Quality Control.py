import pandas as pd
from pathlib import Path

root = Path(__file__).resolve().parents[1]
INPUT = root / "outputs" / "extracted_records_draft.xlsx"
OUTPUT = root / "outputs" / "manual_review_records.xlsx"

# Read extraction results; an absent unit column is treated as missing units.
df = pd.read_excel(INPUT)
unit_col = next((c for c in df if str(c).strip().lower()
                 in {"unit", "unit_std", "measurement_unit"}), None)
expected = {"OM": "g/kg", "TN": "g/kg", "AP": "mg/kg", "AK": "mg/kg"}
flagged = []

for idx, row in df.iterrows():
    indicator = str(row["indicator_std"]).strip()
    function = str(row["function_type_std"]).strip()
    unit = row[unit_col] if unit_col else None
    reasons = []

    if indicator in expected:
        if pd.isna(unit) or not str(unit).strip():
            reasons.append("Missing unit")
        elif str(unit).strip() != expected[indicator]:
            reasons.append(f"Unit mismatch (expected {expected[indicator]})")

    values = pd.to_numeric(row[["x1", "x2", "x3", "x4"]], errors="coerce")
    x1, x2, x3, x4 = values.tolist()
    if function == "parabolic":
        valid = x1 < x2 <= x3 < x4
    elif function == "S-type":
        valid = x1 < x4
    else:
        valid = False
    if not valid:
        reasons.append("Invalid threshold values or order")

    if reasons:
        flagged.append([idx + 2, row["table_id"], indicator, function,
                        x1, x2, x3, x4, unit, "; ".join(reasons)])

columns = ["Source Row", "Table ID", "Indicator", "Function",
           "X1", "X2", "X3", "X4", "Unit", "Review Reason"]
pd.DataFrame(flagged, columns=columns).to_excel(
    OUTPUT, index=False, sheet_name="Manual Review", engine="openpyxl")
print(f"{len(flagged)} records flagged for manual review. Saved: {OUTPUT}")
