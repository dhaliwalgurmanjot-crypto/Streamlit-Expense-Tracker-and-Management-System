# Project 1: Streamlit Expense Analytics

A modern, interactive personal finance analytics dashboard built with Streamlit, SQLite, and Plotly. The app supports full CRUD for expenses, budgeting, savings goals, alerting, and exports while auto-saving visualizations for reports.

## Features
- Add expenses faster with quick-amount presets, pre-filled category/method, and “Save & add another”.
- Manage expenses via a selectable table (filters, multi-delete, single-row edit) instead of manual IDs.
- Dashboard charts with range selector (current month, last 30 days, YTD, all time), breakdown toggle (category/payment), and trend granularity (daily/weekly/monthly).
- Monthly dashboards with metrics, recent activity, and budget progress alerts (80% threshold configurable).
- Analytics tab shows interactive charts and renders all saved PNGs from `plots/` inline.
- Budgets and savings goals with synced sliders + numeric inputs, remaining calculations, and alerts.
- Custom date range summaries and CSV export; persistent settings stored in SQLite.

## Project Structure
- `app.py` – Streamlit UI with sidebar navigation.
- `db/database.py` – SQLite initialization and helpers.
- `services/expense_service.py` – CRUD and sample seed data.
- `services/analytics_service.py` – Aggregations and chart generation (saves to `plots/`).
- `services/budget_service.py` – Budget storage, progress, and alerting.
- `data/` – SQLite database and sample CSV (generated at runtime).
- `plots/` – Saved visualizations for reports.
- `screenshots/` – UI captures for documentation.
- `reports/main.tex` – Full academic-style report.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```
3. Use the sidebar to navigate between Dashboard, Analytics, Budgets & Goals, Settings, and Export.

## Database Schema
- `expenses(id, date, amount, category, payment_method, notes)`
- `budgets(id, month, budget, savings_goal, created_at)`
- `settings(key, value)`

## Saved Plots
- `plots/category_distribution.png`
- `plots/daily_trend.png`
- `plots/monthly_comparison.png`

These files refresh automatically when you view Analytics; they also appear inline under “Saved Plots.”

## Testing Quickstart
- Launch the app and add a few expenses across categories using quick presets.
- Set a budget and savings goal; confirm slider and numeric inputs stay in sync and alerts fire near 80%.
- Visit Analytics, switch ranges and breakdowns, and confirm interactive charts plus PNGs under “Saved Plots.”
- Download the CSV export to verify data persistence.

## Report
Compile the LaTeX report from `reports/main.tex` using `pdflatex` for a full project write-up with architecture, DFDs, schema, results, and screenshots.
