# National Dynamics MVP Dashboard

Welcome to the National Dynamics MVP dashboard project. This repository will house the initial structure and documentation for building a streamlined dashboard that visualizes key metrics for National Dynamics.

## Project Structure
- `app/` – Application source for the dashboard and related services.
- `data/` – Data files or seeds used by the dashboard. Demo CSVs in this
  directory are synthetic placeholders marked "DEMO DATA – NOT REAL STATISTICS"
  and will be replaced with documented federal datasets.
- `data/` – Data files or seeds used by the dashboard.
- `docs/` – Project documentation, requirements, and reference materials.
- `scripts/` – Utility scripts for setup, deployment, or maintenance.
- `test_environment.md` – Verification note confirming repository access.

## Getting Started
- Add application code to the `app/` directory.
- Place any sample or input data in `data/`.
- Document workflows or architecture decisions in `docs/`.
- Keep automation and helper utilities in `scripts/`.

This layout establishes the foundation for the MVP dashboard and can be expanded as development progresses.

## Variable Comparison Explorer
The "Variable Comparison (Beta)" page lets you pick any two numeric indicators from the datasets in `data/` and visualize their relationship. After selecting variables, the tool produces a scatter plot with a linear regression line, reports the Pearson correlation coefficient, highlights the largest residual outliers, and auto-generates a short summary describing the strength and direction of the correlation over the available years.
