import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import numpy as np
from utils import get_supabase, getMatches, getCurrentLevel

def dashboard_page():
    # Get user
    supabase = get_supabase()
    user = supabase.auth.get_user().user

    # Header
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("assets/dashboard.png", width=100)
    with col2:
        st.title("Performance Dashboard")
    st.divider()

    # Load & preprocess
    df = getMatches(user.id)
    if df.empty:
        st.info("No match data available. Add some matches in the Match Log to see your performance analytics.")
        return
    df["match_date"] = pd.to_datetime(df["match_date"])

    # Date & type filters (unchanged)
    current_date = date.today()
    min_date, max_date = df["match_date"].dt.date.min(), df["match_date"].dt.date.max()
    col1, col2 = st.columns([1,3])
    with col1:
        period = st.selectbox("Time Period", ["All Time","Last 30 Days","Last 3 Months","Last 6 Months","Last Year","Custom"], index=0)
    if period == "Custom":
        with col2:
            start_date, end_date = st.date_input("Select Date Range", value=(min_date, current_date), min_value=min_date, max_value=current_date)
        df = df[(df["match_date"].dt.date>=start_date)&(df["match_date"].dt.date<=end_date)]
    else:
        days = {"Last 30 Days":30, "Last 3 Months":90, "Last 6 Months":180, "Last Year":365}.get(period, None)
        if days: df = df[df["match_date"].dt.date >= current_date - timedelta(days=days)]
    match_type = st.radio("Match Type", ["All","Singles","Doubles"], horizontal=True)
    if match_type!="All":
        df = df[df["match_type"]==match_type.lower()]
    if df.empty:
        st.warning(f"No {match_type.lower()} matches in the selected period.")
        return

    # Win/loss
    df["result"] = np.where(df["user_team_score"]>df["opponent_team_score"], "Win", "Loss")

    # Summary metrics
    st.header("Performance Summary")
    total, wins = len(df), (df["result"]=="Win").sum()
    losses = total-wins
    win_rate = wins/total*100
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Matches", total)
    c2.metric("Wins", wins)
    c3.metric("Losses", losses)
    c4.metric("Win Rate", f"{win_rate:.1f}%")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Performance Over Time",
        "Scoring Analysis",
        "Opponent Analysis",
        "Level Progression"
    ])

    # ─── Tab 1: Performance Over Time ─────────────────────────────────────────
    with tab1:
        st.subheader("Wins vs Losses per Month")

        # 1) Prepare month buckets
        df_time = df.copy()
        df_time["month"] = df_time["match_date"].dt.to_period("M").dt.to_timestamp()

        # 2) Pivot into wide form
        monthly_res = (
            df_time
            .groupby(["month", "result"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )

        # 3) Create a categorical label
        monthly_res["month_label"] = monthly_res["month"].dt.strftime("%B %Y")

        # 4) Plot stacked bar with custom colors
        fig1 = px.bar(
            monthly_res,
            x="month_label",
            y=["Win", "Loss"],
            barmode="stack",
            labels={"month_label": "Month", "value": "Count"},
            title="Wins vs Losses per Month",
            color_discrete_sequence=["#309bd4", "lightsalmon"]  # Win = light green, Loss = light orange
        )
        st.plotly_chart(fig1, use_container_width=True)
        # optional: keep your monthly total chart if desired
        st.subheader("Matches per Month")

        # 1) Aggregate by period
        df_time = df.copy()
        df_time["month"] = df_time["match_date"].dt.to_period("M").dt.to_timestamp()

        monthly_totals = (
            df_time
            .groupby("month")
            .size()
            .reset_index(name="matches")
        )

        # 2) Create a categorical month label
        monthly_totals["month_label"] = monthly_totals["month"].dt.strftime("%B %Y")

        # 3) Plot using that label
        fig2 = px.bar(
            monthly_totals,
            x="month_label",
            y="matches",
            labels={"month_label": "Month", "matches": "Matches"},
            title="Matches per Month",
            color_discrete_sequence=["#309bd4"]
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ─── Tab 2: Match Analysis ─────────────────────────────────────────────────
    with tab2:
        
        st.subheader("Average Points For vs. Against")

        # 1) Compute the means
        avg_scores = (
            df
            .groupby("match_type")
            .agg(
                Your_Score      = ("user_team_score",     "mean"),
                Opponent_Score  = ("opponent_team_score", "mean"),
            )
            .reset_index()
        )

        # 2) Melt into long form for Plotly
        avg_long = avg_scores.melt(
            id_vars="match_type",
            value_vars=["Your_Score", "Opponent_Score"],
            var_name="Team",
            value_name="Average Points"
        )

        # 3) Bar chart grouped by match type
        fig = px.bar(
            avg_long,
            x="match_type",
            y="Average Points",
            color="Team",
            barmode="group",
            labels={
                "match_type":    "Match Type",
                "Average Points":"Avg Points",
                "Team":          "Team"
            },
            title="Average Points Scored by Match Type"
        )
        st.plotly_chart(fig, use_container_width=True)



    # ─── Tab 3: Opponent Analysis ──────────────────────────────────────────────
    with tab3:
        st.subheader("Opponent Level Analysis")

        # Singles: Win rate vs. opponent level
        df_s = df[df["match_type"] == "singles"].copy()
        if df_s.empty:
            st.info("No singles matches to analyze.")
        else:
            st.markdown("**Singles**")
            singles_level = (
                df_s
                .groupby("opponent_1_level")
                .agg(
                    Wins   = ("result", lambda x: (x == "Win").sum()),
                    Losses = ("result", lambda x: (x == "Loss").sum()),
                    Total  = ("result", "count")
                )
                .reset_index()
            )
            singles_level["Win Rate"] = (singles_level["Wins"] / singles_level["Total"] * 100).round(1)
            singles_level = singles_level.sort_values("opponent_1_level")

            st.dataframe(
                singles_level.rename(columns={"opponent_1_level": "Opponent Level"}),
                use_container_width=True,
                hide_index=True
            )

            fig_s = px.bar(
                singles_level,
                x="opponent_1_level",
                y="Win Rate",
                labels={"opponent_1_level": "Opponent Level", "Win Rate": "Win Rate (%)"},
                title="Singles Win Rate by Opponent Level",
                text_auto=True
            )
            st.plotly_chart(fig_s, use_container_width=True)

        # Doubles: Win rate vs. average opponent team level
        df_d = df[df["match_type"] == "doubles"].copy()
        if df_d.empty:
            st.info("No doubles matches to analyze.")
        else:
            st.markdown("**Doubles**")
            # Calculate average opponent team level
            df_d["Opponent Team Level"] = ((df_d["opponent_1_level"] + df_d["opponent_2_level"]) / 2).round(2)
            doubles_level = (
                df_d
                .groupby("Opponent Team Level")
                .agg(
                    Wins   = ("result", lambda x: (x == "Win").sum()),
                    Losses = ("result", lambda x: (x == "Loss").sum()),
                    Total  = ("result", "count")
                )
                .reset_index()
            )
            doubles_level["Win Rate"] = (doubles_level["Wins"] / doubles_level["Total"] * 100).round(1)
            doubles_level = doubles_level.sort_values("Opponent Team Level")

            st.dataframe(
                doubles_level,
                use_container_width=True,
                hide_index=True
            )

            fig_d = px.bar(
                doubles_level,
                x="Opponent Team Level",
                y="Win Rate",
                labels={"Opponent Team Level": "Opponent Team Level", "Win Rate": "Win Rate (%)"},
                title="Doubles Win Rate by Opponent Team Level",
                text_auto=True
            )
            st.plotly_chart(fig_d, use_container_width=True)


    # ─── Tab 4: Level Progression ───────────────────────────────────────────────
    with tab4:
        st.subheader("Your Current Level")
        current_level = getCurrentLevel(user.id)
        if current_level is None:
            st.info("No level data found.")
        else:
            st.metric("Level", f"{current_level:.1f}")
            # gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=current_level,
                gauge={"axis":{"range":[1,5.5]}},
                title={"text":"Player Level"}
            ))
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    dashboard_page()
