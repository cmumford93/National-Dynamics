"""
National Dynamics Streamlit app.
A minimal dashboard scaffold for U.S. social, economic, religious, family,
crime, and mental health indicators.
"""

from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import streamlit as st
import plotly.express as px

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


def load_marriage_data() -> Tuple[Optional[pd.DataFrame], str]:
    """Load marriage rates, preferring the real CDC dataset when available."""

    real_df = load_dataset("marriage_rate_real.csv", "Marriage rate (CDC)")
    if real_df is not None and not real_df.empty:
        cleaned_real = real_df.rename(
            columns={"marriage_rate_per_1000_population": "marriage_rate_per_1000"}
        )
        return cleaned_real.sort_values("year"), "real"

    demo_df = load_dataset("marriage_rate_demo.csv", "Marriage rate (demo)")
    if demo_df is None:
        return None, "missing"
    return demo_df.sort_values("year"), "demo"


def render_overview() -> None:
    st.header("Overview")
    st.caption(
        "A concise, demo-based snapshot of national trends. Real datasets (Census, BLS, FBI, CDC) "
        "will replace these placeholders soon."
    )

    # Load demo datasets (replace with production loaders when real data is available)
    marriage_df = load_dataset("marriage_rate_demo.csv", "Marriage rate")
    income_df = load_dataset("median_income_demo.csv", "Median income")
    crime_df = load_dataset("violent_crime_demo.csv", "Violent crime rate")
    suicide_df = load_dataset("suicide_rate_demo.csv", "Suicide rate")

    palette = {
        "marriage": "#4C78A8",
        "income": "#59A14F",
        "unemployment": "#F28E2B",
        "crime": "#E15759",
        "suicide": "#B07AA1",
    }

    def kpi_card(column, label: str, value: str, description: str, accent: str) -> None:
        """Render a lightly styled KPI card within a column."""

        card_style = (
            f"background-color: {accent}15;"
            "padding: 16px;"
            "border-radius: 12px;"
            "border: 1px solid rgba(0,0,0,0.04);"
        )
        with column:
            st.markdown(
                f"""
                <div style="{card_style}">
                    <div style="font-size: 14px; color: #6b7280; margin-bottom: 6px;">{label}</div>
                    <div style="font-size: 26px; font-weight: 700; color: #111827;">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption(description)

    st.divider()
    st.subheader("Key indicators (latest demo year)")
    kpi_cols = st.columns(4)

    if marriage_df is not None and not marriage_df.empty:
        latest_marriage = marriage_df.sort_values("year").iloc[-1]
        kpi_card(
            kpi_cols[0],
            "Marriage rate (per 1,000)",
            f"{latest_marriage['marriage_rate_per_1000']:.2f}",
            "Demo value for the most recent year in the synthetic dataset.",
            palette["marriage"],
        )
    else:
        kpi_card(kpi_cols[0], "Marriage rate (per 1,000)", "—", "No data available.", palette["marriage"])

    if income_df is not None and not income_df.empty:
        latest_income = income_df.sort_values("year").iloc[-1]
        kpi_card(
            kpi_cols[1],
            "Median income",
            f"${latest_income['median_income']:,.0f}",
            "Demo value for the most recent year in the synthetic dataset.",
            palette["income"],
        )
    else:
        kpi_card(kpi_cols[1], "Median income", "—", "No data available.", palette["income"])

    if crime_df is not None and not crime_df.empty:
        latest_crime = crime_df.sort_values("year").iloc[-1]
        kpi_card(
            kpi_cols[2],
            "Violent crime (per 100k)",
            f"{latest_crime['violent_crime_rate_per_100k']:.1f}",
            "Demo value for the most recent year in the synthetic dataset.",
            palette["crime"],
        )
    else:
        kpi_card(
            kpi_cols[2],
            "Violent crime (per 100k)",
            "—",
            "No data available.",
            palette["crime"],
        )

    if suicide_df is not None and not suicide_df.empty:
        latest_suicide = suicide_df.sort_values("year").iloc[-1]
        kpi_card(
            kpi_cols[3],
            "Suicide rate (per 100k)",
            f"{latest_suicide['suicide_rate_per_100k']:.2f}",
            "Demo value for the most recent year in the synthetic dataset.",
            palette["suicide"],
        )
    else:
        kpi_card(
            kpi_cols[3],
            "Suicide rate (per 100k)",
            "—",
            "No data available.",
            palette["suicide"],
        )

    st.write(" ")
    st.divider()

    chart_ready = all(
        df is not None and not df.empty for df in [marriage_df, income_df, crime_df, suicide_df]
    )

    def line_chart(df: pd.DataFrame, y: str, color: str, title: str, y_label: str) -> None:
        fig = px.line(
            df.sort_values("year"),
            x="year",
            y=y,
            line_shape="spline",
            color_discrete_sequence=[color],
            hover_data={"year": True, y: True},
            markers=False,
        )
        fig.update_layout(
            title=title,
            margin=dict(l=10, r=10, t=40, b=10),
            height=340,
            yaxis_title=y_label,
            xaxis_title="Year",
            hovermode="x unified",
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)

    if chart_ready:
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            line_chart(
                marriage_df,
                "marriage_rate_per_1000",
                palette["marriage"],
                "Marriage rate over time",
                "Marriages per 1,000 people",
            )
            st.caption("Marriage rates remain a cornerstone demographic indicator, shown here year over year.")

        with row1_col2:
            line_chart(
                income_df,
                "median_income",
                palette["income"],
                "Median household income over time",
                "Median income (USD)",
            )
            st.caption("Income trends illustrate purchasing power shifts across the demo period.")

        st.write(" ")
        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            # Unemployment series is only available in the income dataset
            if "unemployment_rate_pct" in income_df.columns:
                line_chart(
                    income_df,
                    "unemployment_rate_pct",
                    palette["unemployment"],
                    "Unemployment rate over time",
                    "Unemployment (%)",
                )
                st.caption("Labor market softness is captured via demo unemployment rates by year.")
            else:
                st.info("Unemployment rate series is not available in the demo dataset.")

        with row2_col2:
            line_chart(
                suicide_df,
                "suicide_rate_per_100k",
                palette["suicide"],
                "Suicide rate over time",
                "Suicides per 100,000 people",
            )
            st.caption("Mental health strain appears as changes in the annual suicide rate.")
    else:
        st.info(
            "Charts will render once the demo CSVs are available. This helps "
            "ensure the app handles missing data gracefully."
        )


def render_placeholder(title: str, description: str) -> None:
    st.header(title)
    st.write(description)
    st.caption("More details and interactive charts are coming soon.")


def render_family_structure() -> None:
    st.header("Family Structure")
    st.write(
        "This page prioritizes real CDC National Vital Statistics marriage rates "
        "when available and falls back to demo data for development."
    )
    st.caption("(Using real CDC National Vital Statistics marriage rates if available.)")

    marriage_df, marriage_source = load_marriage_data()
    household_df = load_dataset("household_types_demo.csv", "Household types")

    if marriage_df is not None and not marriage_df.empty:
        st.subheader("Marriage rate (per 1,000) over time")
        st.line_chart(
            marriage_df.set_index("year")["marriage_rate_per_1000"],
            height=320,
        )
        if marriage_source == "real":
            st.success("Displaying real CDC/NCHS marriage rates.")
        else:
            st.info("Using demo marriage rates until the real dataset is available.")

    if household_df is not None and not household_df.empty:
        st.subheader("Household composition trends (demo)")
        st.area_chart(
            household_df.set_index("year"),
            height=360,
        )

    if (marriage_df is None or marriage_df.empty) or (
        household_df is None or household_df.empty
    ):
        st.info(
            "Charts will appear once the real CDC marriage data or fallback demo "
            "CSV and the household composition CSV are present."
        )


def render_religion_culture() -> None:
    st.header("Religion & Culture (Demo)")
    st.write(
        "Synthetic trends for Christian, Catholic, and unaffiliated identification. "
        "These values are placeholders until vetted sources (e.g., Pew Research, "
        "GSS, CARA) are integrated."
    )

    religion_df = load_dataset("religion_trends_demo.csv", "Religion & culture")
    if religion_df is None or religion_df.empty:
        st.info(
            "Religion & culture demo data will appear once the CSV is available. "
            "Real survey sources will replace these placeholders in future updates."
        )
        return

    religion_df = religion_df.sort_values("year")
    latest = religion_df.iloc[-1]

    kpi_cols = st.columns(3)
    kpi_cols[0].metric(
        "% Christian",
        f"{latest['christian_pct']:.1f}%",
        help="Demo share identifying as Christian in the most recent year.",
    )
    kpi_cols[1].metric(
        "% Catholic",
        f"{latest['catholic_pct']:.1f}%",
        help="Demo share identifying as Catholic in the most recent year.",
    )
    kpi_cols[2].metric(
        "% Unaffiliated",
        f"{latest['unaffiliated_pct']:.1f}%",
        help="Demo share identifying with no religion in the most recent year.",
    )

    st.subheader("Religious affiliation trends")
    trend_df = religion_df.rename(
        columns={
            "christian_pct": "Christian",
            "catholic_pct": "Catholic",
            "unaffiliated_pct": "Unaffiliated",
        }
    ).set_index("year")
    st.line_chart(trend_df, height=360)


def render_mental_health() -> None:
    st.header("Mental Health (Demo)")
    st.write(
        "This page uses synthetic placeholder values until CDC BRFSS and "
        "mortality statistics are integrated. Trends and levels are for demo "
        "illustration only."
    )

    mental_df = load_dataset("mental_health_demo.csv", "Mental health")
    if mental_df is None or mental_df.empty:
        st.info(
            "Mental health demo data will appear once the CSV is available. "
            "Real public health sources will replace these placeholders in future releases."
        )
        return

    mental_df = mental_df.sort_values("year")
    latest = mental_df.iloc[-1]

    kpi_cols = st.columns(3)
    kpi_cols[0].metric(
        "Depression rate",
        f"{latest['depression_rate_pct']:.2f}%",
        help="Demo estimate for the most recent year in the synthetic dataset.",
    )
    kpi_cols[1].metric(
        "Anxiety rate",
        f"{latest['anxiety_rate_pct']:.2f}%",
        help="Demo estimate for the most recent year in the synthetic dataset.",
    )
    kpi_cols[2].metric(
        "Suicide rate (per 100k)",
        f"{latest['suicide_rate_per_100k']:.2f}",
        help="Demo estimate for the most recent year in the synthetic dataset.",
    )

    st.subheader("Depression over time")
    st.line_chart(
        mental_df.set_index("year")["depression_rate_pct"],
        height=320,
    )

    st.subheader("Anxiety over time")
    st.line_chart(
        mental_df.set_index("year")["anxiety_rate_pct"],
        height=320,
    )

    st.subheader("Suicide rate over time")
    st.line_chart(
        mental_df.set_index("year")["suicide_rate_per_100k"],
        height=320,
    )


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
        "Religion & Culture",
        "Mental Health",
        "About",
    ]
    selected_section = st.sidebar.radio("Select a page", nav_options)

    st.sidebar.divider()
    page_link = getattr(st.sidebar, "page_link", None)
    if callable(page_link):
        page_link("pages/03_variable_comparison.py", label="Variable Comparison (Beta)")
    else:
        st.sidebar.caption("Variable Comparison (Beta) available from the Streamlit pages menu.")

    if selected_section == "Overview":
        render_overview()
    elif selected_section == "Family Structure":
        render_family_structure()
    elif selected_section == "Economics":
        render_placeholder(
            "Economics",
            "Placeholder content. Economic indicators (e.g., income, employment, inflation) "
            "will be wired to official data sources in future updates. Coming soon!",
        )
    elif selected_section == "Crime & Safety":
        render_placeholder(
            "Crime & Safety",
            "Placeholder content. Crime and public safety indicators will be connected to "
            "standardized datasets (e.g., FBI UCR/NCVS) in later releases. Coming soon!",
        )
    elif selected_section == "Religion & Culture":
        render_religion_culture()
    elif selected_section == "Mental Health":
        render_mental_health()
    elif selected_section == "About":
        render_placeholder(
            "About",
            "This dashboard is under active development. Demo data is used for now; future "
            "versions will feature reproducible pipelines, methods, and source documentation "
            "for all indicators. Coming soon!",
        )

    # Notes for future development
    st.info(
        "Demo data is currently loaded from synthetic CSVs in the data/ directory. "
        "Replace these with curated federal datasets and documented ETL pipelines as the platform matures."
    )


if __name__ == "__main__":
    main()
