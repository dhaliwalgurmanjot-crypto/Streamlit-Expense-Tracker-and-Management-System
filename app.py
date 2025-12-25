import datetime
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st
import plotly.express as px

from db.database import init_db
from constants import CATEGORIES, PAYMENT_METHODS
from services.analytics_service import AnalyticsService
from services.budget_service import BudgetService
from services.expense_service import ExpenseService

PLOTS_DIR = Path(__file__).resolve().parent / "plots"
DATA_DIR = Path(__file__).resolve().parent / "data"


def init_app_state() -> None:
    init_db()
    ExpenseService.seed_sample_data()
    PLOTS_DIR.mkdir(exist_ok=True, parents=True)
    DATA_DIR.mkdir(exist_ok=True, parents=True)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
        .metric-row {margin-top: 0.5rem; margin-bottom: 0.5rem;}
        .metric-row .element-container {padding: 0.4rem 0.6rem;}
        .stDataFrame {border-radius: 6px; border: 1px solid #e0e0e0;}
        .pill {display: inline-block; padding: 4px 10px; border-radius: 16px; background: #eef3ff; color: #1f3c88; font-size: 12px; margin-right: 6px;}
        .section-card {padding: 1rem; border: 1px solid #e5e5e5; border-radius: 10px; background: #fafafa;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def add_expense_ui():
    st.header("Add Expense")
    last_df = ExpenseService.list_expenses().sort_values("date")
    last_expense = last_df.iloc[-1] if not last_df.empty else None

    if last_expense is not None:
        st.caption(
            f"Last: {pd.to_datetime(last_expense['date']).date()} • {last_expense['category']} • ₹{last_expense['amount']:.0f} • {last_expense['payment_method']}"
        )

    with st.form("add_expense"):
        c1, c2 = st.columns(2)
        with c1:
            date = st.date_input("Date", datetime.date.today())
        default_amount = float(last_expense["amount"]) if last_expense is not None else 0.0
        quick_amount = st.radio(
            "Quick amount (optional)",
            options=[0, 250, 500, 1000, 2000],
            index=0,
            horizontal=True,
            format_func=lambda x: "None" if x == 0 else f"₹{x}",
        )
        with c2:
            amount = st.number_input(
                "Amount", min_value=0.0, value=float(quick_amount or default_amount), format="%.2f"
            )

        c3, c4 = st.columns(2)
        with c3:
            category = st.selectbox(
                "Category",
                CATEGORIES,
                index=0 if last_expense is None else CATEGORIES.index(last_expense["category"]) if last_expense.get("category") in CATEGORIES else 0,
            )
        with c4:
            payment_method = st.selectbox(
                "Payment Method",
                PAYMENT_METHODS,
                index=0 if last_expense is None else PAYMENT_METHODS.index(last_expense["payment_method"]) if last_expense.get("payment_method") in PAYMENT_METHODS else 0,
            )

        notes = st.text_area("Notes", placeholder="Add a short description (optional)")
        col_btn1, col_btn2 = st.columns(2)
        save = col_btn1.form_submit_button("Save Expense", type="primary")
        save_add = col_btn2.form_submit_button("Save & add another")

    if save or save_add:
        if amount <= 0:
            st.warning("Amount must be greater than zero.")
            return
        ExpenseService.add_expense(
            {
                "date": str(date),
                "amount": amount,
                "category": category,
                "payment_method": payment_method,
                "notes": notes,
            }
        )
        st.success("Expense saved.")
        if save_add:
            st.rerun()


def manage_expenses_ui():
    st.header("Manage Expenses")
    df = ExpenseService.list_expenses()
    if df.empty:
        st.info("No expenses yet.")
        return
    df["date"] = pd.to_datetime(df["date"])
    min_date, max_date = df["date"].min().date(), df["date"].max().date()

    with st.expander("Filters", expanded=True):
        colf1, colf2 = st.columns(2)
        with colf1:
            start_date, end_date = st.date_input("Date range", value=(min_date, max_date))
        with colf2:
            search_text = st.text_input("Search notes or payee", placeholder="Type to filter")

        colf3, colf4 = st.columns(2)
        categories = sorted(df["category"].unique().tolist())
        selected_categories = st.multiselect("Categories", categories, default=categories)
        with colf4:
            methods = sorted(df["payment_method"].unique().tolist())
            selected_methods = st.multiselect("Payment methods", methods, default=methods)

        sort_choice = st.selectbox(
            "Sort by",
            ["Date (newest)", "Date (oldest)", "Amount (high to low)", "Amount (low to high)"],
            index=0,
        )

    filtered = df.copy()
    if start_date and end_date:
        filtered = filtered[(filtered["date"] >= pd.to_datetime(start_date)) & (filtered["date"] <= pd.to_datetime(end_date))]
    if selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]
    if selected_methods:
        filtered = filtered[filtered["payment_method"].isin(selected_methods)]
    if search_text:
        filtered = filtered[filtered["notes"].fillna("").str.contains(search_text, case=False, na=False)]

    if filtered.empty:
        st.info("No expenses match these filters.")
        return

    sort_map = {
        "Date (newest)": ("date", False),
        "Date (oldest)": ("date", True),
        "Amount (high to low)": ("amount", False),
        "Amount (low to high)": ("amount", True),
    }
    sort_col, ascending = sort_map[sort_choice]
    filtered = filtered.sort_values(sort_col, ascending=ascending)

    view_cols = ["id", "date", "category", "payment_method", "amount", "notes"]
    view_df = filtered[view_cols].copy()
    view_df["Select"] = False
    view_df = view_df[["Select"] + view_cols]

    edited_df = st.data_editor(
        view_df,
        hide_index=True,
        use_container_width=True,
        disabled=["id", "date", "category", "payment_method", "amount", "notes"],
        column_config={
            "Select": st.column_config.CheckboxColumn(required=False),
            "id": st.column_config.Column("ID", width="small"),
            "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "category": st.column_config.Column("Category"),
            "payment_method": st.column_config.Column("Payment"),
            "amount": st.column_config.NumberColumn("Amount", format="₹%.0f"),
            "notes": st.column_config.Column("Notes"),
        },
    )

    selected_rows = edited_df[edited_df["Select"]]
    selected_ids = selected_rows["id"].astype(int).tolist()

    act_col1, act_col2 = st.columns(2)
    with act_col1:
        if st.button("Delete selected", type="secondary"):
            if not selected_ids:
                st.warning("Pick at least one row to delete.")
            else:
                for eid in selected_ids:
                    ExpenseService.delete_expense(eid)
                st.success(f"Deleted {len(selected_ids)} expense(s).")
                st.rerun()

    with act_col2:
        if st.button("Edit selected", type="primary"):
            if not selected_ids:
                st.warning("Select at least one row to edit.")
            else:
                st.session_state["editing_ids"] = selected_ids
                st.rerun()

    if "editing_ids" in st.session_state:
        ids_to_edit = st.session_state["editing_ids"]
        to_edit = df[df["id"].isin(ids_to_edit)].copy()
        
        if to_edit.empty:
            del st.session_state["editing_ids"]
            st.rerun()

        st.subheader(f"Editing {len(to_edit)} Expense(s)")
        st.info("Modify rows below and click Save.")

        edited_data = st.data_editor(
            to_edit,
            hide_index=True,
            use_container_width=True,
            disabled=["id"],
            column_config={
                "id": st.column_config.Column("ID", disabled=True),
                "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD", required=True),
                "amount": st.column_config.NumberColumn("Amount", min_value=0.0, format="%.2f", required=True),
                "category": st.column_config.SelectboxColumn("Category", options=CATEGORIES, required=True),
                "payment_method": st.column_config.SelectboxColumn(
                    "Payment", options=PAYMENT_METHODS, required=True
                ),
                "notes": st.column_config.TextColumn("Notes"),
            },
            key="editor_multi",
        )

        ec1, ec2 = st.columns(2)
        with ec1:
            if st.button("Save Changes", type="primary"):
                for idx, row in edited_data.iterrows():
                    d_val = row["date"]
                    if hasattr(d_val, "date"):
                        d_str = str(d_val.date())
                    else:
                        d_str = str(d_val).split(" ")[0]

                    ExpenseService.update_expense(
                        int(row["id"]),
                        {
                            "date": d_str,
                            "amount": float(row["amount"]),
                            "category": row["category"],
                            "payment_method": row["payment_method"],
                            "notes": row["notes"],
                        },
                    )
                st.success(f"Updated {len(edited_data)} expenses.")
                del st.session_state["editing_ids"]
                st.rerun()
        
        with ec2:
            if st.button("Cancel"):
                del st.session_state["editing_ids"]
                st.rerun()


def analytics_ui():
    st.header("Analytics")
    df = ExpenseService.list_expenses()
    if df.empty:
        st.info("Add expenses to view analytics.")
        return
    df["date"] = pd.to_datetime(df["date"])
    min_date, max_date = df["date"].min(), df["date"].max()
    start, end = st.date_input("Date Range", value=(min_date.date(), max_date.date()))
    filtered = df[(df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))]
    if filtered.empty:
        st.warning("No data in selected range.")
        return

    col1, col2 = st.columns(2)
    with col1:
        fig_cat, breakdown = AnalyticsService.category_distribution(filtered)
        st.pyplot(fig_cat)
        st.download_button(
            "Download Category Chart",
            data=(PLOTS_DIR / "category_distribution.png").read_bytes(),
            file_name="category_distribution.png",
        )
    with col2:
        fig_daily, plotly_daily = AnalyticsService.daily_trend(filtered)
        if plotly_daily is not None:
            st.plotly_chart(plotly_daily, use_container_width=True)
        else:
            st.pyplot(fig_daily)

    fig_monthly, plotly_monthly = AnalyticsService.monthly_comparison(filtered)
    if plotly_monthly is not None:
        st.plotly_chart(plotly_monthly, use_container_width=True)
    else:
        st.pyplot(fig_monthly)

    st.subheader("Summary Table")
    summary = filtered.groupby("category")["amount"].agg(["sum", "mean", "count"]).reset_index()
    st.dataframe(summary)

    saved_plots = sorted(PLOTS_DIR.glob("*.png"))
    if saved_plots:
        st.subheader("Saved Plots")
        cols = st.columns(2)
        for idx, plot_path in enumerate(saved_plots):
            with cols[idx % 2]:
                if plot_path.exists():
                    st.image(str(plot_path), caption=plot_path.name, use_container_width=True)
    else:
        st.caption("No saved plots yet.")



def budget_ui():
    st.header("Budgets & Goals")
    today = datetime.date.today()
    default_month = today.strftime("%Y-%m")
    month = st.text_input("Month (YYYY-MM)", value=default_month)
    budget_row = BudgetService.get_budget(month)
    existing_budget = budget_row.get("budget", 0.0) if budget_row else 0.0
    existing_goal = budget_row.get("savings_goal", 0.0) if budget_row else 0.0
    df = ExpenseService.list_expenses()
    df["date"] = pd.to_datetime(df["date"]) if not df.empty else pd.to_datetime([])
    current_period = pd.to_datetime(f"{month}-01").to_period("M") if month else today.to_period("M")
    month_spent = df[df["date"].dt.to_period("M") == current_period]["amount"].sum() if not df.empty else 0.0

    suggested_budget = max(existing_budget, month_spent * 1.2 if month_spent else 5000)
    budget_ceiling = max(suggested_budget * 1.5, 5000)
    suggested_goal = max(existing_goal, budget_ceiling * 0.1)

    # Default values must be defined before use
    budget_default = float(existing_budget or suggested_budget)
    goal_default = float(existing_goal or suggested_goal)

    # Initialize session state for synced widgets if not present
    if "budget_slider" not in st.session_state:
        st.session_state["budget_slider"] = budget_default
    if "budget_input" not in st.session_state:
        st.session_state["budget_input"] = budget_default
    if "goal_slider" not in st.session_state:
        st.session_state["goal_slider"] = goal_default
    if "goal_input" not in st.session_state:
        st.session_state["goal_input"] = goal_default

    def sync_budget_from_slider():
        st.session_state["budget_input"] = st.session_state["budget_slider"]

    def sync_budget_from_input():
        st.session_state["budget_slider"] = st.session_state["budget_input"]

    def sync_goal_from_slider():
        st.session_state["goal_input"] = st.session_state["goal_slider"]

    def sync_goal_from_input():
        st.session_state["goal_slider"] = st.session_state["goal_input"]

    bc1, bc2 = st.columns(2)
    with bc1:
        st.slider(
            "Monthly Budget",
            min_value=0.0,
            max_value=float(budget_ceiling),
            step=100.0,
            key="budget_slider",
            on_change=sync_budget_from_slider,
        )
        st.number_input(
            "Monthly Budget (exact)",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key="budget_input",
            on_change=sync_budget_from_input,
        )
        budget = st.session_state["budget_input"]
        st.caption(f"Spent this month: ₹{month_spent:.0f}")
    with bc2:
        st.slider(
            "Savings Goal",
            min_value=0.0,
            max_value=float(budget_ceiling),
            step=100.0,
            key="goal_slider",
            on_change=sync_goal_from_slider,
        )
        st.number_input(
            "Savings Goal (exact)",
            min_value=0.0,
            step=100.0,
            format="%.2f",
            key="goal_input",
            on_change=sync_goal_from_input,
        )
        goal = st.session_state["goal_input"]
        st.caption("Tip: aim for 10-20% of budget.")

    if st.button("Save Budget", type="primary"):
        BudgetService.set_budget(month, budget, goal)
        st.success("Budget updated.")

    progress = BudgetService.monthly_progress(df, month)
    m1, m2, m3 = st.columns(3)
    m1.metric("Spent", f"₹{progress['spent']:.2f}")
    m2.metric("Budget", f"₹{progress['budget']:.2f}")
    m3.metric("Remaining", f"₹{progress['remaining']:.2f}")
    if progress["budget"] > 0:
        st.progress(min(progress["spent"] / progress["budget"], 1.0), text=f"{progress['spent'] / progress['budget'] * 100:.1f}% of budget used")

    alert = BudgetService.spending_alert(progress["spent"], progress["budget"])
    if alert:
        st.error(alert)



def settings_ui():
    st.header("Settings")
    current_threshold = float(BudgetService.get_setting("alert_threshold", str(BudgetService.DEFAULT_ALERT_THRESHOLD)))
    with st.form("settings_form"):
        threshold = st.slider("Alert Threshold (ratio of budget)", min_value=0.5, max_value=1.0, value=current_threshold, step=0.05)
        submitted = st.form_submit_button("Save Settings")
        if submitted:
            BudgetService.save_setting("alert_threshold", str(threshold))
            st.success("Settings saved.")
    st.caption("Spending alerts trigger when spending exceeds the configured threshold of your monthly budget.")


def export_ui():
    st.header("Export")
    df = ExpenseService.list_expenses()
    if df.empty:
        st.info("Nothing to export.")
        return
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv_bytes, file_name="expenses.csv", mime="text/csv")
    st.caption("Use the CSV in spreadsheets or BI tools for deeper analysis.")


def dashboard_ui():
    st.header("Dashboard")
    df = ExpenseService.list_expenses()
    if df.empty:
        st.info("Add expenses to view insights.")
        return
    df["date"] = pd.to_datetime(df["date"])
    current_month = datetime.date.today().strftime("%Y-%m")
    monthly_df = df[df["date"].dt.to_period("M") == pd.to_datetime(current_month + "-01").to_period("M")]
    total_spent = monthly_df["amount"].sum() if not monthly_df.empty else 0.0
    budget_row = BudgetService.get_budget(current_month)
    budget = budget_row.get("budget", 0.0) if budget_row else 0.0
    savings_goal = budget_row.get("savings_goal", 0.0) if budget_row else 0.0
    remaining = max(budget - total_spent, 0.0)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Month", current_month)
    col2.metric("Spent", f"₹{total_spent:.2f}")
    col3.metric("Budget", f"₹{budget:.2f}")
    col4.metric("Remaining", f"₹{remaining:.2f}")

    if alert_msg := BudgetService.spending_alert(total_spent, budget):
        st.error(alert_msg)

    # Dashboard highlights
    total_txns = len(monthly_df)
    avg_daily = monthly_df.groupby(monthly_df["date"].dt.date)["amount"].sum().mean() if not monthly_df.empty else 0.0
    top_cat_row = monthly_df.groupby("category")["amount"].sum().sort_values(ascending=False).reset_index().head(1)
    top_cat = f"{top_cat_row.iloc[0]['category']} (₹{top_cat_row.iloc[0]['amount']:.0f})" if not top_cat_row.empty else "-"

    highlights_col1, highlights_col2, highlights_col3 = st.columns(3)
    highlights_col1.metric("Transactions", total_txns)
    highlights_col2.metric("Avg Daily Spend", f"₹{avg_daily:.0f}")
    highlights_col3.metric("Top Category", top_cat)

    if budget > 0:
        usage = min(total_spent / budget, 1.0)
        st.progress(usage, text=f"{usage*100:.1f}% of budget used")

    overview_tab, charts_tab = st.tabs(["Overview", "Charts"])

    with overview_tab:
        st.subheader("Recent Expenses")
        st.dataframe(monthly_df.sort_values("date", ascending=False).head(10))

        st.subheader("Category Summary")
        cat_summary = monthly_df.groupby("category")["amount"].agg(["sum", "mean", "count"]).reset_index()
        st.dataframe(cat_summary)

    with charts_tab:
        # Dashboard charts can be widened beyond current month to avoid empty categories.
        chart_range = st.selectbox(
            "Chart range",
            ["Current Month", "Last 30 Days", "Year-to-date", "All Time"],
            index=0,
        )
        col_opts1, col_opts2 = st.columns(2)
        with col_opts1:
            breakdown = st.selectbox("Breakdown", ["Category", "Payment Method"], index=0)
        with col_opts2:
            agg_period = st.selectbox("Trend granularity", ["Daily", "Weekly", "Monthly"], index=0)

        if chart_range == "Current Month":
            chart_df = monthly_df
            range_label = "Current Month"
        elif chart_range == "Last 30 Days":
            start = pd.to_datetime(datetime.date.today() - datetime.timedelta(days=30))
            chart_df = df[df["date"] >= start]
            range_label = "Last 30 Days"
        elif chart_range == "Year-to-date":
            start = pd.to_datetime(datetime.date(datetime.date.today().year, 1, 1))
            chart_df = df[df["date"] >= start]
            range_label = "Year-to-date"
        else:
            chart_df = df
            range_label = "All Time"

        if chart_df.empty:
            st.info("No data for the selected range.")
        else:
            if breakdown == "Category":
                dim_col = "category"
                dims = CATEGORIES
            else:
                dim_col = "payment_method"
                dims = PAYMENT_METHODS

            cat_totals = (
                chart_df.groupby(dim_col)["amount"].sum()
                .reindex(dims, fill_value=0)
                .reset_index()
            )
            donut = px.pie(cat_totals, names=dim_col, values="amount", hole=0.45, title=f"{breakdown} Mix ({range_label})")

            freq_map = {"Daily": "D", "Weekly": "W-MON", "Monthly": "MS"}
            daily_totals = (
                chart_df.set_index("date")["amount"].resample(freq_map[agg_period]).sum().reset_index()
            )
            daily_line = px.line(daily_totals, x="date", y="amount", markers=True, title=f"Trend ({agg_period}, {range_label})")

            bar_all = px.bar(cat_totals.sort_values("amount", ascending=False), x=dim_col, y="amount", title=f"{breakdown} Totals ({range_label})")

            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                st.plotly_chart(donut, use_container_width=True)
            with chart_col2:
                st.plotly_chart(daily_line, use_container_width=True)

            st.plotly_chart(bar_all, use_container_width=True)



NAVIGATION = ["Dashboard", "Add Expense", "Manage Expenses", "Analytics", "Budgets & Goals", "Settings", "Export"]


def main():
    st.set_page_config(page_title="Expense Analytics", layout="wide")
    inject_css()
    init_app_state()
    st.sidebar.title("Expense Analytics")
    choice = st.sidebar.radio("Navigate", NAVIGATION, key="navigation_radio")

    if choice == "Dashboard":
        dashboard_ui()
    elif choice == "Add Expense":
        add_expense_ui()
    elif choice == "Manage Expenses":
        manage_expenses_ui()
    elif choice == "Analytics":
        analytics_ui()
    elif choice == "Budgets & Goals":
        budget_ui()
    elif choice == "Settings":
        settings_ui()
    elif choice == "Export":
        export_ui()


if __name__ == "__main__":
    main()
