import json
import pandas as pd
from pathlib import Path

root = Path(__file__).resolve().parents[1]
input_dir = root / "outputs" / "stage2_extraction"
output_excel = root / "outputs" / "extracted_records_draft.xlsx"

json_files = sorted(input_dir.glob("*.json"))

all_rows = []

for file in json_files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    for table_obj in data:
        table_id = table_obj.get("table_id", "")
        records = table_obj.get("records", [])

        for record in records:
            row = {
                "table_id": table_id,
                "indicator_std": record.get("indicator_std", ""),
                "function_type_std": record.get("function_type_std", ""),
                "x1": record.get("x1", None),
                "x2": record.get("x2", None),
                "x3": record.get("x3", None),
                "x4": record.get("x4", None),
                "unit": record.get("unit", "")
            }
            all_rows.append(row)

df = pd.DataFrame(all_rows, columns=[
    "table_id",
    "indicator_std",
    "function_type_std",
    "x1",
    "x2",
    "x3",
    "x4",
    "unit"
])


df.to_excel(output_excel, index=False)

