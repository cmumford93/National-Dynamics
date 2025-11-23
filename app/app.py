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


def load_unemployment_data() -> Tuple[Optional[pd.DataFrame], str]:
    """Load unemployment rates, preferring real data if present."""

    real_df = load_dataset("unemployment_rate_real.csv", "Unemployment rate (BLS)")
    if real_df is not None and not real_df.empty:
        return real_df.sort_values("year"), "real"

    demo_df = load_dataset("unemployment_rate_demo.csv", "Unemployment rate (demo)")
    if demo_df is None:
        return None, "missing"
    return demo_df.sort_values("year"), "demo"


def load_median_income_data() -> Tuple[Optional[pd.DataFrame], str]:
    demo_df = load_dataset("median_income_demo.csv", "Median income (demo)")
    if demo_df is None:
        return None, "missing"
    return demo_df.sort_values("year"), "demo"


def load_cpi_data() -> Tuple[Optional[pd.DataFrame], str]:
    demo_df = load_dataset("cpi_index_demo.csv", "CPI index (demo)")
    if demo_df is None:
        return None, "missing"
    return demo_df.sort_values("year"), "demo"


def load_crime_data() -> Tuple[Tuple[Optional[pd.DataFrame], str], Tuple[Optional[pd.DataFrame], str]]:
    violent_df = load_dataset("violent_crime_demo.csv", "Violent crime rate (demo)")
    mass_df = load_dataset("mass_shootings_demo.csv", "Mass incidents (demo)")

    violent_status = "demo" if violent_df is not None else "missing"
    mass_status = "demo" if mass_df is not None else "missing"

    return (violent_df.sort_values("year") if violent_df is not None else None, violent_status), (
        mass_df.sort_values("year") if mass_df is not None else None,
        mass_status,
    )


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


def render_economics() -> None:
    st.header("Economics")
    st.write(
        "Synthetic economics indicators (demo-only) covering unemployment, household income, "
        "and price levels. Real BLS/Census data will replace these placeholders in future releases."
    )

    unemployment_df, unemployment_source = load_unemployment_data()
    income_df, income_source = load_median_income_data()
    cpi_df, cpi_source = load_cpi_data()

    if any(df is None or df.empty for df in [unemployment_df, income_df, cpi_df]):
        st.info(
            "One or more economic demo CSVs are missing. Ensure unemployment_rate_demo.csv, "
            "median_income_demo.csv, and cpi_index_demo.csv are present in data/."
        )

    kpi_cols = st.columns(3)

    if unemployment_df is not None and not unemployment_df.empty:
        latest_unemp = unemployment_df.iloc[-1]
        source_note = "BLS (real)" if unemployment_source == "real" else "Demo"
        kpi_cols[0].metric(
            "Unemployment rate",
            f"{latest_unemp['unemployment_rate_pct']:.2f}%",
            help=f"Latest {source_note} unemployment rate in the dataset.",
        )

    if income_df is not None and not income_df.empty:
        latest_income = income_df.iloc[-1]
        kpi_cols[1].metric(
            "Median household income",
            f"${latest_income['median_income']:,.0f}",
            help="Latest synthetic estimate of median household income (demo).",
        )

    if cpi_df is not None and not cpi_df.empty:
        latest_cpi = cpi_df.iloc[-1]
        prev_cpi = cpi_df.iloc[-2]["cpi_index"] if len(cpi_df) > 1 else None
        yoy = None if prev_cpi is None else (latest_cpi["cpi_index"] - prev_cpi) / prev_cpi * 100
        delta = None if yoy is None else f"{yoy:.2f}%"
        kpi_cols[2].metric(
            "Price level (CPI index)",
            f"{latest_cpi['cpi_index']:.2f}",
            delta=delta,
            help="Synthetic CPI-style index (demo). Year-over-year change shown when available.",
        )

    st.caption("Charts below use synthetic demo-only values for illustration.")

    def line_chart(df: pd.DataFrame, y: str, title: str, color: str, y_label: str) -> None:
        fig = px.line(
            df,
            x="year",
            y=y,
            markers=True,
            color_discrete_sequence=[color],
            hover_data={"year": True, y: True},
        )
        fig.update_layout(title=title, template="plotly_white", height=350, yaxis_title=y_label, xaxis_title="Year")
        st.plotly_chart(fig, use_container_width=True)

    chart_row_1 = st.columns(2)
    with chart_row_1[0]:
        if unemployment_df is not None and not unemployment_df.empty:
            line_chart(
                unemployment_df,
                "unemployment_rate_pct",
                "Unemployment rate (demo)",
                "#F28E2B",
                "Unemployment rate (%)",
            )
    with chart_row_1[1]:
        if income_df is not None and not income_df.empty:
            line_chart(
                income_df,
                "median_income",
                "Median household income (demo)",
                "#59A14F",
                "Income (USD)",
            )

    chart_row_2 = st.columns(1)
    with chart_row_2[0]:
        if cpi_df is not None and not cpi_df.empty:
            line_chart(
                cpi_df,
                "cpi_index",
                "CPI index (demo)",
                "#4C78A8",
                "Index (base ~100)",
            )


def render_crime_safety() -> None:
    st.header("Crime & Safety")
    st.write(
        "Synthetic crime indicators (demo-only) focusing on violent crime rates and mass incidents. "
        "Real FBI and incident databases will replace these placeholder series." 
    )

    (violent_df, violent_source), (mass_df, mass_source) = load_crime_data()

    if (violent_df is None or violent_df.empty) or (mass_df is None or mass_df.empty):
        st.info(
            "Crime demo CSVs missing. Ensure violent_crime_demo.csv and mass_shootings_demo.csv are present in data/."
        )

    kpi_cols = st.columns(2)
    if violent_df is not None and not violent_df.empty:
        latest_violent = violent_df.iloc[-1]
        kpi_cols[0].metric(
            "Violent crime rate (per 100k)",
            f"{latest_violent['violent_crime_rate_per_100k']:.1f}",
            help="Synthetic violent crime rate for the most recent demo year.",
        )

    if mass_df is not None and not mass_df.empty:
        latest_incidents = mass_df.iloc[-1]
        kpi_cols[1].metric(
            "Mass incidents (count)",
            f"{latest_incidents['incidents']}",
            help="Synthetic count of mass incidents for the most recent demo year.",
        )

    st.caption("Charts use synthetic demo-only values for illustration; they are not real crime statistics.")

    def line_chart(df: pd.DataFrame, y: str, title: str, color: str, y_label: str) -> None:
        fig = px.line(
            df,
            x="year",
            y=y,
            markers=True,
            color_discrete_sequence=[color],
            hover_data={"year": True, y: True},
        )
        fig.update_layout(title=title, template="plotly_white", height=350, yaxis_title=y_label, xaxis_title="Year")
        st.plotly_chart(fig, use_container_width=True)

    chart_row = st.columns(2)
    with chart_row[0]:
        if violent_df is not None and not violent_df.empty:
            line_chart(
                violent_df,
                "violent_crime_rate_per_100k",
                "Violent crime rate (demo)",
                "#E15759",
                "Crimes per 100,000",
            )

    with chart_row[1]:
        if mass_df is not None and not mass_df.empty:
            line_chart(
                mass_df,
                "incidents",
                "Mass incidents (demo)",
                "#B07AA1",
                "Incident count",
            )


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
        render_economics()
    elif selected_section == "Crime & Safety":
        render_crime_safety()
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
