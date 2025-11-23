"""
National Dynamics Streamlit app.
A minimal dashboard scaffold for U.S. social, economic, religious, family,
crime, and mental health indicators.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st

# Configure the page
st.set_page_config(
    page_title="National Dynamics",
    page_icon="🌎",
    layout="wide",
)

# Constants
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_dataset(filename: str, friendly_name: str) -> Optional[pd.DataFrame]:
    """
    Load a CSV from the data directory.

    Demo files include a comment header noting they are synthetic; the comment
    parameter skips those lines. Real federal datasets will replace these
    placeholders in future iterations.
    """

    path = DATA_DIR / filename
    try:
        return pd.read_csv(path, comment="#")
    except FileNotFoundError:
        st.warning(
            f"{friendly_name} dataset is missing (expected at `{path}`). "
            "Add the CSV to enable this chart."
        )
    except Exception as exc:  # pragma: no cover - surface friendly message
        st.warning(f"Could not load {friendly_name} data: {exc}")
    return None


def render_overview() -> None:
    st.header("Overview")
    st.caption(
        "Showing demo charts built from synthetic CSVs. These will be replaced "
        "with validated federal datasets (e.g., Census, BLS, FBI, CDC) in future updates."
    )

    # Load demo datasets (replace with production loaders when real data is available)
    marriage_df = load_dataset("marriage_rate_demo.csv", "Marriage rate")
    income_df = load_dataset("median_income_demo.csv", "Median income")
    crime_df = load_dataset("violent_crime_demo.csv", "Violent crime rate")
    suicide_df = load_dataset("suicide_rate_demo.csv", "Suicide rate")

    # KPI row using the most recent year in each dataset
    metrics = st.columns(4)
    if marriage_df is not None and not marriage_df.empty:
        latest_marriage = marriage_df.sort_values("year").iloc[-1]
        metrics[0].metric(
            "Marriage rate (per 1,000)",
            f"{latest_marriage['marriage_rate_per_1000']:.2f}",
            help="Demo value for the most recent year in the synthetic dataset.",
        )
    else:
        metrics[0].metric("Marriage rate (per 1,000)", "—")

    if income_df is not None and not income_df.empty:
        latest_income = income_df.sort_values("year").iloc[-1]
        metrics[1].metric(
            "Median income (USD)",
            f"${latest_income['median_income']:,.0f}",
            help="Demo value for the most recent year in the synthetic dataset.",
        )
    else:
        metrics[1].metric("Median income (USD)", "—")

    if crime_df is not None and not crime_df.empty:
        latest_crime = crime_df.sort_values("year").iloc[-1]
        metrics[2].metric(
            "Violent crime (per 100k)",
            f"{latest_crime['violent_crime_rate_per_100k']:.1f}",
            help="Demo value for the most recent year in the synthetic dataset.",
        )
    else:
        metrics[2].metric("Violent crime (per 100k)", "—")

    if suicide_df is not None and not suicide_df.empty:
        latest_suicide = suicide_df.sort_values("year").iloc[-1]
        metrics[3].metric(
            "Suicide rate (per 100k)",
            f"{latest_suicide['suicide_rate_per_100k']:.2f}",
            help="Demo value for the most recent year in the synthetic dataset.",
        )
    else:
        metrics[3].metric("Suicide rate (per 100k)", "—")

    # Line charts for trends
    chart_ready = all(
        df is not None and not df.empty for df in [marriage_df, income_df, crime_df, suicide_df]
    )

    if chart_ready:
        # Socio-economic chart
        socio_df = (
            marriage_df.merge(income_df, on="year", how="inner")
            .rename(
                columns={
                    "marriage_rate_per_1000": "Marriage rate (per 1,000)",
                    "median_income": "Median income (USD)",
                }
            )
            .set_index("year")
        )
        st.subheader("Socio-economic trends (demo)")
        st.line_chart(socio_df, height=340)

        # Safety and mental health chart
        safety_df = (
            crime_df.merge(suicide_df, on="year", how="inner")
            .rename(
                columns={
                    "violent_crime_rate_per_100k": "Violent crime (per 100k)",
                    "suicide_rate_per_100k": "Suicide rate (per 100k)",
                }
            )
            .set_index("year")
        )
        st.subheader("Crime and mental health trends (demo)")
        st.line_chart(safety_df, height=340)
    else:
        st.info(
            "Charts will render once the demo CSVs are available. This helps "
            "ensure the app handles missing data gracefully."
        )


def render_placeholder(title: str, description: str) -> None:
    st.header(title)
    st.write(description)


def main() -> None:
    # App title and description
    st.title("National Dynamics")
    st.write(
        "A U.S. social, economic, religious, family, crime, and mental health "
        "indicator viewer. This dashboard will evolve to provide neutral, "
        "data-driven insights across core societal domains."
    )

    # Sidebar navigation
    st.sidebar.title("Navigation")
    nav_options = [
        "Overview",
        "Family Structure",
        "Economics",
        "Crime & Safety",
        "Mental Health",
        "About",
    ]
    selected_section = st.sidebar.radio("Select a page", nav_options)

    if selected_section == "Overview":
        render_overview()
    elif selected_section == "Family Structure":
        render_placeholder(
            "Family Structure",
            "Placeholder content. Family-related indicators (e.g., marriage, divorce, "
            "household composition) will integrate validated datasets in upcoming iterations.",
        )
    elif selected_section == "Economics":
        render_placeholder(
            "Economics",
            "Placeholder content. Economic indicators (e.g., income, employment, inflation) "
            "will be wired to official data sources in future updates.",
        )
    elif selected_section == "Crime & Safety":
        render_placeholder(
            "Crime & Safety",
            "Placeholder content. Crime and public safety indicators will be connected to "
            "standardized datasets (e.g., FBI UCR/NCVS) in later releases.",
        )
    elif selected_section == "Mental Health":
        render_placeholder(
            "Mental Health",
            "Placeholder content. Mental and behavioral health indicators will be drawn from "
            "reputable public sources in subsequent updates.",
        )
    elif selected_section == "About":
        render_placeholder(
            "About",
            "This dashboard is under active development. Demo data is used for now; future "
            "versions will feature reproducible pipelines, methods, and source documentation "
            "for all indicators.",
        )

    # Notes for future development
    st.info(
        "Demo data is currently loaded from synthetic CSVs in the data/ directory. "
        "Replace these with curated federal datasets and documented ETL pipelines as the platform matures."
    )


if __name__ == "__main__":
    main()
