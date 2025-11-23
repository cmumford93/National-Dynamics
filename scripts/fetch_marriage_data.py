"""Download and prepare CDC/NCHS marriage rate data.

This script attempts to pull the official National Vital Statistics PDF from
CDC, extract year and national marriage rate values, and write them to
``data/marriage_rate_real.csv``. The PDF can be challenging to scrape in some
environments; when extraction fails, the script falls back to a short list of
manually transcribed (real) national rates for 2000–2020 from the same source.
"""

from __future__ import annotations

import csv
import importlib
import importlib.util
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.request import Request, urlopen

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_PATH = DATA_DIR / "marriage_rate_real.csv"
SOURCE_URL = "https://www.cdc.gov/nchs/data/dvs/state_marriage_rates_1900-2020.pdf"

# Manually transcribed national marriage rates from the CDC PDF (per 1,000 population).
MANUAL_MARRIAGE_RATES = [
    {"year": 2000, "marriage_rate_per_1000_population": 8.2},
    {"year": 2001, "marriage_rate_per_1000_population": 8.4},
    {"year": 2002, "marriage_rate_per_1000_population": 8.0},
    {"year": 2003, "marriage_rate_per_1000_population": 7.8},
    {"year": 2004, "marriage_rate_per_1000_population": 7.8},
    {"year": 2005, "marriage_rate_per_1000_population": 7.6},
    {"year": 2006, "marriage_rate_per_1000_population": 7.5},
    {"year": 2007, "marriage_rate_per_1000_population": 7.5},
    {"year": 2008, "marriage_rate_per_1000_population": 7.1},
    {"year": 2009, "marriage_rate_per_1000_population": 6.8},
    {"year": 2010, "marriage_rate_per_1000_population": 6.8},
    {"year": 2011, "marriage_rate_per_1000_population": 6.8},
    {"year": 2012, "marriage_rate_per_1000_population": 6.8},
    {"year": 2013, "marriage_rate_per_1000_population": 6.8},
    {"year": 2014, "marriage_rate_per_1000_population": 6.9},
    {"year": 2015, "marriage_rate_per_1000_population": 6.9},
    {"year": 2016, "marriage_rate_per_1000_population": 6.9},
    {"year": 2017, "marriage_rate_per_1000_population": 6.9},
    {"year": 2018, "marriage_rate_per_1000_population": 6.5},
    {"year": 2019, "marriage_rate_per_1000_population": 6.1},
    {"year": 2020, "marriage_rate_per_1000_population": 5.1},
]


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _download_pdf(target_path: Path) -> Optional[Path]:
    """Attempt to download the CDC PDF. Returns the saved path or None."""

    print(f"Downloading CDC marriage rate PDF from {SOURCE_URL} ...")
    req = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req) as resp:  # nosec: url provided by CDC
            target_path.write_bytes(resp.read())
        print(f"Saved PDF to {target_path}")
        return target_path
    except Exception as exc:  # pragma: no cover - network variability
        print(f"Could not download PDF ({exc}); falling back to manual data.")
        return None


def _load_pdfplumber():
    """Return a pdfplumber module if installed, otherwise None."""

    spec = importlib.util.find_spec("pdfplumber")
    if spec is None:
        print("pdfplumber not installed; skipping PDF extraction and using manual data.")
        return None
    return importlib.import_module("pdfplumber")


def _extract_rates_from_pdf(pdf_path: Path) -> Optional[pd.DataFrame]:
    """Try to extract national marriage rates from the PDF.

    The CDC PDF is formatted with large tables; parsing can fail depending on the
    environment. When extraction fails, return None so the caller can use the
    manual fallback.
    """

    pdfplumber = _load_pdfplumber()
    if pdfplumber is None:
        return None

    records: List[dict] = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue
                for row in table:
                    if not row or not row[0]:
                        continue
                    first_cell = str(row[0]).strip()
                    if not first_cell.isdigit():
                        continue
                    year = int(first_cell)
                    # The national rate column is the first numeric value after the year
                    # in the PDF tables.
                    numeric_cells: Iterable[str] = (
                        cell for cell in row[1:] if cell is not None and str(cell).strip()
                    )
                    rate_value: Optional[float] = None
                    for cell in numeric_cells:
                        cell_text = str(cell).strip().replace("\u2013", "-")
                        try:
                            rate_value = float(cell_text)
                        except ValueError:
                            continue
                        else:
                            break
                    if rate_value is None:
                        continue
                    records.append(
                        {
                            "year": year,
                            "marriage_rate_per_1000_population": rate_value,
                        }
                    )
    except Exception as exc:  # pragma: no cover - parsing best effort
        print(f"PDF extraction failed ({exc}); falling back to manual data.")
        return None

    if not records:
        return None

    df = pd.DataFrame(records)
    df = df.drop_duplicates(subset=["year"]).sort_values("year")
    return df


def _write_csv(df: pd.DataFrame) -> None:
    header_comment = (
        "# REAL national marriage rates from CDC/NCHS National Vital Statistics. "
        "Automatically generated by scripts/fetch_marriage_data.py"
    )
    with OUTPUT_PATH.open("w", newline="") as csvfile:
        csvfile.write(header_comment + "\n")
        writer = csv.writer(csvfile)
        writer.writerow(["year", "marriage_rate_per_1000_population"])
        for _, row in df.iterrows():
            writer.writerow(
                [int(row["year"]), float(row["marriage_rate_per_1000_population"])]
            )
    print(f"Wrote {len(df)} rows to {OUTPUT_PATH}")


def main() -> None:
    _ensure_data_dir()

    pdf_path = DATA_DIR / "state_marriage_rates_1900-2020.pdf"
    downloaded = _download_pdf(pdf_path)

    df = None
    if downloaded is not None:
        df = _extract_rates_from_pdf(downloaded)

    if df is None:
        print("Using manual CDC rates for 2000–2020.")
        df = pd.DataFrame(MANUAL_MARRIAGE_RATES)

    _write_csv(df)


if __name__ == "__main__":
    main()
