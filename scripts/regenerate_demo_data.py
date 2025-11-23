import numpy as np
import pandas as pd
from pathlib import Path


np.random.seed(42)


def generate_drivers(years: np.ndarray) -> dict:
    year_centered = years - years.mean()

    economic_noise = np.random.normal(0, 0.15, size=len(years))
    recession_2008 = 1.4 * np.exp(-0.5 * ((years - 2009) / 1.2) ** 2)
    recession_2020 = 1.6 * np.exp(-0.5 * ((years - 2020) / 0.9) ** 2)
    economic_stress = 0.1 * year_centered / year_centered.std() + recession_2008 + recession_2020 + economic_noise

    social_trend = -0.012 * (years - years[0])
    post_2010_accel = -0.0015 * np.maximum(0, years - 2010) ** 1.2
    social_noise = np.random.normal(0, 0.02, size=len(years))
    social_cohesion = 1.0 + social_trend + post_2010_accel + social_noise

    secular_curve = 1 / (1 + np.exp(-0.25 * (years - 2012)))
    secularization = 0.3 + 0.6 * secular_curve + np.random.normal(0, 0.02, size=len(years))

    return {
        "economic_stress": economic_stress,
        "social_cohesion": social_cohesion,
        "secularization": secularization,
    }


def generate_marriage_rate(years: np.ndarray, drivers: dict) -> pd.DataFrame:
    decline = 8.6 - 0.1 * (years - years[0])
    curvature = -0.08 * ((years - 2012) / 8) ** 2
    stress_effect = -0.25 * drivers["economic_stress"]
    noise = np.random.normal(0, 0.05, size=len(years))
    marriage_rate = decline + curvature + stress_effect + noise
    return pd.DataFrame({"year": years, "marriage_rate_per_1000": marriage_rate.round(2)})


def generate_median_income(years: np.ndarray, drivers: dict) -> pd.DataFrame:
    base = 45000 + (years - years[0]) * (72000 - 45000) / (years[-1] - years[0])
    mid_accel = 1400 * np.maximum(0, years - 2013) / (years[-1] - 2013)
    stress_dents = -2500 * drivers["economic_stress"]
    noise = np.random.normal(0, 900, size=len(years))
    median_income = base + mid_accel + stress_dents + noise
    median_income = np.maximum(median_income, 30000)
    return pd.DataFrame({"year": years, "median_income": median_income.round(0).astype(int)})


def generate_unemployment(years: np.ndarray, drivers: dict) -> pd.DataFrame:
    base = 4.6 + 0.05 * np.sin(0.5 * (years - years[0]))
    spikes = 3.8 * np.exp(-0.5 * ((years - 2009) / 1.0) ** 2) + 3.5 * np.exp(-0.5 * ((years - 2020) / 0.8) ** 2)
    noise = np.random.normal(0, 0.25, size=len(years))
    unemployment = base + spikes + 0.6 * drivers["economic_stress"] + noise
    unemployment = np.clip(unemployment, 3.2, None)
    return pd.DataFrame({"year": years, "unemployment_rate_pct": unemployment.round(2)})


def generate_cpi(years: np.ndarray) -> pd.DataFrame:
    base_growth = 1.7 + 0.03 * (years - years[0]) / (years[-1] - years[0])
    inflation_bump = np.where(years >= 2020, 0.8, 0)
    noise = np.random.normal(0.05, 0.03, size=len(years))
    annual_growth = base_growth + inflation_bump + noise
    annual_growth = np.maximum(annual_growth, 0.5)
    cpi_index = 100 + np.cumsum(annual_growth)
    return pd.DataFrame({"year": years, "cpi_index": cpi_index.round(2)})


def generate_violent_crime(years: np.ndarray, drivers: dict) -> pd.DataFrame:
    baseline_decline = 500 - (years - years[0]) * (140 / (years[-1] - years[0]))
    slowdown = 8 * np.log1p(np.maximum(0, years - 2010))
    post_2015_leveling = 6 * np.maximum(0, years - 2015)
    noise = np.random.normal(0, 8, size=len(years))
    violent_crime = baseline_decline + slowdown + 0.8 * drivers["economic_stress"] * 10 + post_2015_leveling ** 0.5 + noise
    return pd.DataFrame({"year": years, "violent_crime_rate_per_100k": violent_crime.round(1)})


def generate_mass_shootings(years: np.ndarray, drivers: dict) -> pd.DataFrame:
    base = 6 + 1.9 * (years - years[0]) ** 1.05 / 10
    stress_pull = 4 * drivers["economic_stress"]
    secular_pull = 5 * (drivers["secularization"] - drivers["secularization"].min())
    noise = np.random.normal(0, 3.0, size=len(years))
    incidents = base + stress_pull + secular_pull + noise
    incidents = np.clip(np.round(incidents), 2, None).astype(int)
    return pd.DataFrame({"year": years, "incidents": incidents})


def generate_mental_health(years: np.ndarray, drivers: dict) -> pd.DataFrame:
    depression_base = 6.2 + 0.22 * (years - years[0]) / 1.2
    depression_jump = 0.9 * drivers["economic_stress"] + 1.1 * (drivers["secularization"] - 0.3)
    depression_noise = np.random.normal(0, 0.2, size=len(years))
    depression = depression_base + depression_jump + depression_noise

    anxiety_base = 8.5 + 0.32 * (years - years[0]) / 1.15
    anxiety_jump = 1.0 * drivers["economic_stress"] + 1.4 * (drivers["secularization"] - 0.35)
    anxiety_noise = np.random.normal(0, 0.25, size=len(years))
    anxiety = anxiety_base + anxiety_jump + anxiety_noise

    suicide_base = 10.2 + 0.18 * (years - years[0])
    suicide_effect = 0.55 * drivers["economic_stress"] + 0.25 * (drivers["secularization"] - 0.3)
    suicide_noise = np.random.normal(0, 0.3, size=len(years))
    suicide = suicide_base + suicide_effect + suicide_noise

    return pd.DataFrame(
        {
            "year": years,
            "depression_rate_pct": depression.round(2),
            "anxiety_rate_pct": anxiety.round(2),
            "suicide_rate_per_100k": suicide.round(2),
        }
    )


def generate_household_types(years: np.ndarray, drivers: dict) -> pd.DataFrame:
    total_households = 79_500_000 + 480_000 * (years - years[0]) + 120_000 * np.sin(0.3 * (years - years[0]))

    married_share = 0.56 - 0.005 * (years - years[0]) + -0.0002 * (years - 2010) ** 2 / 100
    single_parent_share = 0.15 + 0.0018 * (years - years[0]) + 0.0006 * (years - 2010) ** 2 / 150
    cohabiting_share = 0.06 + 0.0025 * (years - years[0]) + 0.0008 * (years - 2012)

    raw_other = 1 - (married_share + single_parent_share + cohabiting_share)
    adjustment = raw_other.mean() - raw_other
    married_share += 0.25 * adjustment
    single_parent_share += 0.15 * adjustment
    cohabiting_share += 0.15 * adjustment
    other_share = 1 - (married_share + single_parent_share + cohabiting_share)

    married = np.round(total_households * married_share).astype(int)
    single_parent = np.round(total_households * single_parent_share).astype(int)
    cohabiting = np.round(total_households * cohabiting_share).astype(int)
    other = np.maximum(total_households - (married + single_parent + cohabiting), 0).astype(int)

    return pd.DataFrame(
        {
            "year": years,
            "married_couple_households": married,
            "single_parent_households": single_parent,
            "cohabiting_couple_households": cohabiting,
            "other_households": other,
        }
    )


def generate_religion_trends(years: np.ndarray, drivers: dict) -> pd.DataFrame:
    christian_trend = 78 - 0.55 * (years - years[0]) + -0.08 * (years - 2010) ** 2 / 50
    catholic_trend = 24 - 0.1 * (years - years[0]) + np.sin(0.15 * (years - years[0]))
    unaffiliated_curve = 12 + 16 * (1 / (1 + np.exp(-0.2 * (years - 2012))))

    christian_pct = christian_trend - 0.8 * (drivers["secularization"] - 0.3) * 10
    catholic_pct = catholic_trend - 0.1 * (drivers["secularization"] - 0.3) * 5
    unaffiliated_pct = unaffiliated_curve + 1.2 * (drivers["secularization"] - 0.3) * 10

    christian_pct = np.clip(christian_pct, 50, 90)
    catholic_pct = np.clip(catholic_pct, 15, 30)
    unaffiliated_pct = np.clip(unaffiliated_pct, 5, 40)

    return pd.DataFrame(
        {
            "year": years,
            "christian_pct": christian_pct.round(2),
            "catholic_pct": catholic_pct.round(2),
            "unaffiliated_pct": unaffiliated_pct.round(2),
        }
    )


def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False)
    print(f"Wrote demo data to {path}")


def main() -> None:
    years = np.arange(2000, 2025)
    drivers = generate_drivers(years)

    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    write_csv(generate_marriage_rate(years, drivers), data_dir / "marriage_rate_demo.csv")
    write_csv(generate_median_income(years, drivers), data_dir / "median_income_demo.csv")
    write_csv(generate_unemployment(years, drivers), data_dir / "unemployment_rate_demo.csv")
    write_csv(generate_cpi(years), data_dir / "cpi_index_demo.csv")
    write_csv(generate_violent_crime(years, drivers), data_dir / "violent_crime_demo.csv")
    write_csv(generate_mass_shootings(years, drivers), data_dir / "mass_shootings_demo.csv")
    write_csv(generate_mental_health(years, drivers), data_dir / "mental_health_demo.csv")
    write_csv(generate_household_types(years, drivers), data_dir / "household_types_demo.csv")
    write_csv(generate_religion_trends(years, drivers), data_dir / "religion_trends_demo.csv")


if __name__ == "__main__":
    main()
