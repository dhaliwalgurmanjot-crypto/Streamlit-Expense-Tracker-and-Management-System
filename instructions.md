# How to Use: Streamlit Expense Analytics

## Prerequisites
- Python 3.11+ recommended.
- From the repo root, activate your environment (conda example):
  ```bash
  conda create -n expense-streamlit python=3.11 -y
  conda activate expense-streamlit
  ```

## Install Dependencies
```bash
pip install -r requirements.txt
```

## Run the App
```bash
streamlit run app.py
```
- Open the Local URL shown in the console (default http://localhost:8501).

## Using the App
- **Dashboard:** Monthly metrics, budget usage bar, recent expenses, and charts with range selector (Current Month, Last 30 Days, YTD, All Time), breakdown toggle (Category/Payment), and trend granularity (Daily/Weekly/Monthly). Alerts appear near 80% of budget.
- **Add Expense:** Two-column form with quick amount presets, prefilled category/payment from last entry, and “Save & add another”.
- **Manage Expenses:** Filter by date, category, payment, and notes; select rows via checkboxes for multi-delete or single-row edit (no manual IDs).
- **Analytics:** Pick a date range; view pie/line/bar (Plotly + Matplotlib). Saved PNGs appear inline under “Saved Plots.”
- **Budgets & Goals:** Sliders and numeric inputs stay in sync for budget and savings goal; alert threshold configurable under Settings.
- **Settings:** Adjust alert threshold ratio (default 0.8).
- **Export:** Download all expenses as CSV.

## Data and Files
- SQLite DB: `data/expenses.db`
- Saved plots: `plots/` (auto-refreshed when charts render; shown inline in Analytics)
- Screenshots: `screenshots/streamlit_dashboard.png`
- Report: `reports/main.tex` (compile with `pdflatex reports/main.tex`)

## Seeding Data
The app seeds 100 sample expenses (Jan 2025–today) scaled to INR on first run. Delete the DB (`data/expenses.db`) to reseed.

## Troubleshooting
- If charts fail, ensure all dependencies installed and reload the page.
- For a clean state, stop Streamlit, delete `data/expenses.db`, then rerun `streamlit run app.py`.
