# Streamlit Expense Analytics: Project Overview

## 1. Introduction

**Streamlit Expense Analytics** is a personal finance dashboard designed to make expense tracking and budgeting fast, visual, and persistent without complex database servers. Built with **Python**, **Streamlit**, and **SQLite**, it offers a unified interface for data entry, management, analysis, and reporting.

## 2. Core Features

- **Effortless Data Entry**: "Add Expense" form with quick-amount presets (₹250, ₹500, etc.) and auto-filled categories/methods from recent history.
- **Visual Analytics**: Interactive charts (Plotly) and reporting-ready static plots (Matplotlib) for Category Distribution, Daily Trends, and Monthly Comparisons.
- **Smart Budgeting**: Set monthly budgets and savings goals using synchronized sliders. Real-time progress bars warn you when you approach limits (80% alert threshold).
- **Bulk Management**: A powerful data grid allows filtering, searching, multi-row editing (with ID protection), and bulk deletions.
- **Reporting**: Auto-generates high-quality PNG plots in `plots/` and supports CSV export for external analysis.

## 3. Technology Stack

- **Frontend/Backend**: [Streamlit](https://streamlit.io/) - Wraps UI and logic in pure Python.
- **Database**: [SQLite](https://www.sqlite.org/index.html) - Embedded relational DB, requiring no setup.
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/) - For aggregations, filtering, and time-series analysis.
- **Visualization**:
  - **Plotly Express**: For interactive dashboard charts.
  - **Matplotlib**: For generating static PNG assets for reports.

## 4. Workflows

### A. First Run & Data Seeding

The application is auto-seeding. On the first launch, if the database is empty, it generates **100 sample expense records** spanning from Jan 2025 to today. This ensures you immediately see a populated dashboard.
_To reset data_: Simply delete the `data/expenses.db` file.

### B. Daily Workflow

1.  **Add Expense**: Enter today's spend. Use "Save & add another" for batch entry.
2.  **Dashboard**: Check the "Remaining" metric to see if you are on track.

### C. Monthly Review

1.  **Analytics**: Select "Last 30 Days" or "Current Month".
2.  **Budgets**: Adjust next month's budget based on `suggested_budget` logic (1.2x previous spend).
3.  **Export**: Download CSV for long-term archiving.

## 5. Project Structure

```text
Project_1_Streamlit_Expense_Analytics/
├── app.py                  # Main application entry point
├── constants.py            # Shared categories and payment methods
├── requirements.txt        # Python dependencies
├── data/
│   └── expenses.db         # SQLite Database (created on run)
├── db/
│   └── database.py         # DB connection/initialization logic
├── services/
│   ├── expense_service.py  # CRUD operations
│   ├── budget_service.py   # Budget calculations
│   └── analytics_service.py# Chart generation & Aggregations
├── plots/                  # Generated PNG charts
└── reports/                # LaTeX report files
```

## 6. Key Implementation Details

- **Session Persistence**: Managing multi-row edits uses `st.session_state` to keep the UI stable during interactions.
- **Caching**: Heavy analytics queries are decorated with `@st.cache_data` to ensure instant dashboard loads.
- **Hybrid Visualization**: Uses Plotly for interaction in the browser and Matplotlib for high-DPI static images suitable for PDF reports.
