"""Scatter explorer for comparing any two numeric variables in the dataset collection."""

from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Variable Comparison (Beta)", page_icon="📊", layout="wide")

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
FRIENDLY_LABELS = {
    ("unemployment_rate_demo.csv", "unemployment_rate_pct"): "Unemployment rate (demo, %)",
    ("unemployment_rate_real.csv", "unemployment_rate_pct"): "Unemployment rate (BLS, %)",
    ("median_income_demo.csv", "median_income"): "Median household income (demo, $)",
    ("cpi_index_demo.csv", "cpi_index"): "CPI (price index, demo)",
    ("violent_crime_demo.csv", "violent_crime_rate_per_100k"): "Violent crime rate (demo, per 100,000)",
    ("mass_shootings_demo.csv", "incidents"): "Mass incidents (demo, count)",
    ("marriage_rate_demo.csv", "marriage_rate_per_1000"): "Marriage rate (demo, per 1,000)",
    ("marriage_rate_real.csv", "marriage_rate_per_1000_population"): "Marriage rate (CDC, per 1,000)",
    ("mental_health_demo.csv", "depression_rate_pct"): "Depression rate (demo, %)",
    ("mental_health_demo.csv", "anxiety_rate_pct"): "Anxiety rate (demo, %)",
    ("mental_health_demo.csv", "suicide_rate_per_100k"): "Suicide rate (demo, per 100,000)",
    ("household_types_demo.csv", "married_couple_households"): "Married couple households (demo)",
    ("household_types_demo.csv", "single_parent_households"): "Single parent households (demo)",
    ("household_types_demo.csv", "cohabiting_couple_households"): "Cohabiting couple households (demo)",
    ("household_types_demo.csv", "other_households"): "Other households (demo)",
    ("religion_trends_demo.csv", "christian_pct"): "Christian identification (demo, %)",
    ("religion_trends_demo.csv", "catholic_pct"): "Catholic identification (demo, %)",
    ("religion_trends_demo.csv", "unaffiliated_pct"): "Unaffiliated (demo, %)",
}


@st.cache_data(show_spinner=False)
def load_numeric_variables() -> Dict[str, Tuple[str, pd.DataFrame]]:
    """Load numeric columns from every CSV in the data directory."""

    variables: Dict[str, Tuple[str, pd.DataFrame]] = {}
    if not DATA_DIR.exists():
        st.warning(f"Data directory not found at `{DATA_DIR}`. Add CSV files to begin.")
        return variables

    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        try:
            df = pd.read_csv(csv_path, comment="#")
        except FileNotFoundError:
            st.warning(f"Dataset `{csv_path.name}` is missing.")
            continue
        except Exception as exc:  # pragma: no cover - user-facing notice only
            st.warning(f"Could not load `{csv_path.name}`: {exc}")
            continue

        if df.empty:
            continue

        numeric_df = df.select_dtypes(include=["number"]).copy()
        if numeric_df.empty:
            continue

        year_series: Optional[pd.Series] = None
        if "year" in df.columns and pd.api.types.is_numeric_dtype(df["year"]):
            year_series = df["year"]

        for column in numeric_df.columns:
            series = numeric_df[column].astype(float)
            variable_df = pd.DataFrame({"value": series})
            if year_series is not None:
                variable_df["year"] = year_series

            key = f"{csv_path.name}:{column}"
            label = FRIENDLY_LABELS.get((csv_path.name, column), f"{csv_path.name} — {column}")
            variables[key] = (label, variable_df.dropna(subset=["value"]))

    return variables


def align_variables(
    a_df: pd.DataFrame, b_df: pd.DataFrame, a_label: str, b_label: str
) -> Tuple[pd.DataFrame, Optional[Tuple[float, float]]]:
    """Align two variable series on year when possible, otherwise on index."""

    a_clean = a_df.copy()
    b_clean = b_df.copy()

    has_year_a = "year" in a_clean and a_clean["year"].notna().any()
    has_year_b = "year" in b_clean and b_clean["year"].notna().any()

    if has_year_a and has_year_b:
        merged = (
            a_clean.rename(columns={"value": a_label})[["year", a_label]]
            .merge(
                b_clean.rename(columns={"value": b_label})[["year", b_label]],
                on="year",
                how="inner",
            )
            .dropna()
        )
        year_range = (
            float(merged["year"].min()),
            float(merged["year"].max()),
        ) if not merged.empty else None
        return merged, year_range

    aligned = pd.DataFrame(
        {
            a_label: a_clean["value"].reset_index(drop=True),
            b_label: b_clean["value"].reset_index(drop=True),
        }
    ).dropna()
    return aligned, None


def describe_correlation(r_value: float) -> str:
    if np.isnan(r_value):
        return "no clear"

    magnitude = abs(r_value)
    if magnitude < 0.3:
        strength = "weak"
    elif magnitude < 0.6:
        strength = "moderate"
    else:
        strength = "strong"

    if r_value > 0:
        direction = "positive"
    elif r_value < 0:
        direction = "negative"
    else:
        direction = "no clear"

    if direction == "no clear":
        return "no clear"
    return f"{strength} {direction}"


st.title("Variable Comparison (Beta)")
st.write(
    "Select any two numeric indicators across the National Dynamics dataset collection to "
    "compare their relationship. Choose variables from the dropdowns below to explore a "
    "scatter plot, regression fit, and automated summary."
)

variables = load_numeric_variables()

if not variables:
    st.info("No numeric variables found. Add CSV files to the data directory to begin.")
    st.stop()

sorted_items = sorted(variables.items(), key=lambda kv: kv[1][0])
options = ["Select a variable"] + [key for key, _ in sorted_items]

col1, col2 = st.columns(2)
with col1:
    var_a_key = st.selectbox(
        "Variable A", options, index=0, format_func=lambda k: "Select a variable" if k == "Select a variable" else variables[k][0]
    )
with col2:
    var_b_key = st.selectbox(
        "Variable B", options, index=0, format_func=lambda k: "Select a variable" if k == "Select a variable" else variables[k][0]
    )

if var_a_key == "Select a variable" or var_b_key == "Select a variable":
    st.info("Pick two variables to generate the scatter plot and summary.")
    st.stop()

if var_a_key == var_b_key:
    st.warning("Please select two different variables.")
    st.stop()

var_a_meta = variables.get(var_a_key)
var_b_meta = variables.get(var_b_key)

if var_a_meta is None or var_b_meta is None:
    st.error("Selected variables could not be loaded. Please choose another combination.")
    st.stop()

var_a_label, var_a = var_a_meta
var_b_label, var_b = var_b_meta

aligned_df, year_range = align_variables(var_a, var_b, var_a_label, var_b_label)

if aligned_df.empty or len(aligned_df) < 2:
    st.info("Not enough overlapping data points to compute the correlation. Try another pair.")
    st.stop()

r_value = float(aligned_df[var_a_label].corr(aligned_df[var_b_label]))
correlation_label = describe_correlation(r_value)

# Linear regression (simple fit)
slope, intercept = np.polyfit(aligned_df[var_a_label], aligned_df[var_b_label], 1)
predicted = aligned_df[var_a_label] * slope + intercept
aligned_df["regression"] = predicted
aligned_df["residual"] = (aligned_df[var_b_label] - predicted).abs()

line_x = np.linspace(aligned_df[var_a_label].min(), aligned_df[var_a_label].max(), 100)
line_y = slope * line_x + intercept

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=aligned_df[var_a_label],
        y=aligned_df[var_b_label],
        mode="markers",
        name="Data points",
        marker=dict(color="#1f77b4", size=10, opacity=0.8),
        text=aligned_df.get("year"),
        hovertemplate="<b>%{x:.2f}</b>, %{y:.2f}<extra>%{text}</extra>",
    )
)

fig.add_trace(
    go.Scatter(
        x=line_x,
        y=line_y,
        mode="lines",
        name="Regression line",
        line=dict(color="#ff7f0e", width=3),
    )
)

outliers = aligned_df.nlargest(3, "residual") if not aligned_df.empty else pd.DataFrame()
if not outliers.empty:
    fig.add_trace(
        go.Scatter(
            x=outliers[var_a_label],
            y=outliers[var_b_label],
            mode="markers",
            name="Top outliers",
            marker=dict(color="#d62728", size=12, symbol="star"),
            text=outliers.get("year"),
            hovertemplate="Outlier: <b>%{x:.2f}</b>, %{y:.2f}<extra>%{text}</extra>",
        )
    )

fig.update_layout(
    xaxis_title=var_a_label,
    yaxis_title=var_b_label,
    margin=dict(l=10, r=10, t=10, b=10),
    height=500,
)

st.plotly_chart(fig, use_container_width=True)

metrics_col, summary_col = st.columns([1, 2])
with metrics_col:
    st.metric("Pearson r", f"{r_value:.2f}")
    st.caption(
        "Pearson correlation computed on overlapping records. Regression is a simple "
        "linear fit."
    )

with summary_col:
    if year_range is not None:
        start_year, end_year = year_range
        range_text = f"In year range {int(start_year)}–{int(end_year)}"
    else:
        range_text = "Across available records"

    descriptor = correlation_label if correlation_label != "no clear" else "no clear correlation"

    st.subheader("Automated summary")
    st.write(
        f"{range_text}, {var_a_label} and {var_b_label} show a {descriptor} "
        f"(r = {r_value:.2f})."
    )

if not outliers.empty:
    st.markdown("**Top outliers (by absolute residual):**")
    for _, row in outliers.iterrows():
        point_label = f"{row[var_a_label]:.2f}, {row[var_b_label]:.2f}"
        year_note = f" (year {int(row['year'])})" if "year" in row and not pd.isna(row["year"]) else ""
        st.markdown(f"- {point_label}{year_note}")
