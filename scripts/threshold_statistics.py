import pandas as pd
import numpy as np

FILE = "outputs/extracted_records_approved.xlsx"
SHEET = "Sheet1"
PAPER_COL = "table_id"

N_BOOTSTRAP = 5000
RANDOM_SEED = 42

df = pd.read_excel(FILE, sheet_name=SHEET)

final_functions = {
    "pH": "parabolic",
    "OM": "parabolic",
    "TN": "parabolic",
    "AP": "S-type",
    "AK": "S-type",
}

function_parameters = {
    "parabolic": ["x1", "x2", "x3", "x4"],
    "S-type": ["x1", "x4"],
}

rng = np.random.default_rng(RANDOM_SEED)

results = []

for indicator, function_type in final_functions.items():

    parameters = function_parameters[function_type]

    for parameter in parameters:

        sub = df[
            (df["indicator_std"] == indicator) &
            (df["function_type_std"] == function_type)
        ].copy()

        sub[parameter] = pd.to_numeric(
            sub[parameter],
            errors="coerce"
        )

        sub = sub.dropna(
            subset=[PAPER_COL, parameter]
        )

        paper_values = (
            sub.groupby(PAPER_COL)[parameter]
               .median()
               .dropna()
               .to_numpy()
        )

        n = len(paper_values)

        if n == 0:
            continue

        median_value = np.median(paper_values)
        q1 = np.percentile(paper_values, 25)
        q3 = np.percentile(paper_values, 75)
        iqr = q3 - q1

        bootstrap_medians = np.empty(N_BOOTSTRAP)

        for i in range(N_BOOTSTRAP):

            bootstrap_sample = rng.choice(
                paper_values,
                size=n,
                replace=True
            )

            bootstrap_medians[i] = np.median(
                bootstrap_sample
            )

        ci_lower, ci_upper = np.percentile(
            bootstrap_medians,
            [2.5, 97.5]
        )

        results.append({
            "Indicator": indicator,
            "Function": function_type,
            "Parameter": parameter.upper(),
            "N_papers": n,
            "Median": median_value,
            "Q1": q1,
            "Q3": q3,
            "IQR": iqr,
            "Bootstrap_95CI_Lower": ci_lower,
            "Bootstrap_95CI_Upper": ci_upper
        })


results_df = pd.DataFrame(results)

print(results_df)


results_df.to_excel(
    "outputs/threshold_statistics.xlsx",
    index=False
)
