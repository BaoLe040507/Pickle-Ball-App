import streamlit as st
import pandas as pd
import re
from datetime import date
from utils import (
    get_supabase,
    getMatches,
    deleteMatch,
    addSinglesMatch,
    addDoublesMatch,
    highlight_win_loss,
    get_distinct_players, 

)


def match_log_page():
    # Initialize edit mode
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # Auth & header
    supabase = get_supabase()
    user = supabase.auth.get_user().user

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("assets/tournament.png", width=100)
    with col2:
        st.title("Match Log")

    if st.session_state.edit_mode:
        st.info("Edit Mode: select rows and delete.")
    st.divider()
    st.markdown(
        "**The SmashTrack Match Log** is where you can view/update your match history."
    )

    # Fetch past names
    players = get_distinct_players(user.id)
    dropdown_options = ["Enter new name..."] + players

    # Add New Match
    with st.expander(":heavy_plus_sign: Add New Match", expanded=False):
        match_type = st.radio("Match Type", ["Singles", "Doubles"], horizontal=True)

        if match_type == "Singles":
            with st.form("singles_form"):
                st.subheader("Singles Match")
                m_date = st.date_input("Date", date.today(), key="s_date")

                # Opponent selection
                opp_choice = st.selectbox("Select Opponent", dropdown_options, key="s_opp_choice")
                if opp_choice == "Enter new name...":
                    opponent = st.text_input("Enter Opponent Name", key="s_opp_text", placeholder="Enter opponent's name")
                else:
                    opponent = opp_choice
                    st.text_input("Selected Opponent", value=opponent, disabled=True, key="s_opp_display")

                opp_level = st.selectbox(
                    "Opponent Level",
                    [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5],
                    key="s_opp_level"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    user_score = st.number_input("Your Score", min_value=0, step=1, key="s_usr_score")
                with col2:
                    opp_score = st.number_input("Opponent Score", min_value=0, step=1, key="s_opp_score")

                submitted = st.form_submit_button("Add Singles Match")
                if submitted:
                    errors = []
                    
                    # Validation
                    if m_date > date.today():
                        errors.append("Date cannot be in the future.")
                    
                    # Get the actual opponent name
                    final_opponent = opponent if opp_choice == "Enter new name..." else opp_choice
                    
                    if not final_opponent or not final_opponent.strip():
                        errors.append("Opponent name is required.")
                    elif not re.fullmatch(r"[A-Za-z ]+", final_opponent.strip()):
                        errors.append("Opponent name must contain only letters and spaces.")
                    
                    if user_score == opp_score:
                        errors.append("Scores cannot be tied. Please enter different scores.")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        if addSinglesMatch(
                            current_user_id=user.id,
                            match_date=m_date,
                            opponent=final_opponent.strip(),
                            opponent_level=opp_level,
                            user_score=user_score,
                            opponent_score=opp_score
                        ):
                            st.success("Singles match added successfully!")
                            st.cache_data.clear()
                            # Clear form fields
                            for key in ['s_date', 's_opp_choice', 's_opp_text', 's_opp_level', 's_usr_score', 's_opp_score']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()

        else:  # Doubles
            with st.form("doubles_form"):
                st.subheader("Doubles Match")
                d_date = st.date_input("Date", date.today(), key="d_date")

                # Partner selection
                st.write("**Your Partner**")
                partner_choice = st.selectbox("Select Partner", dropdown_options, key="d_partner_choice")
                if partner_choice == "Enter new name...":
                    partner = st.text_input("Enter Partner Name", key="d_partner_text", placeholder="Enter partner's name")
                else:
                    partner = partner_choice
                    st.text_input("Selected Partner", value=partner, disabled=True, key="d_partner_display")
                
                part_level = st.selectbox(
                    "Partner Level",
                    [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5],
                    key="d_part_level"
                )

                st.divider()
                st.write("**Opponents**")
                
                # Opponent 1 selection
                opp1_choice = st.selectbox("Select Opponent 1", dropdown_options, key="d_opp1_choice")
                if opp1_choice == "Enter new name...":
                    opp1 = st.text_input("Enter Opponent 1 Name", key="d_opp1_text", placeholder="Enter first opponent's name")
                else:
                    opp1 = opp1_choice
                    st.text_input("Selected Opponent 1", value=opp1, disabled=True, key="d_opp1_display")
                
                opp1_level = st.selectbox(
                    "Opponent 1 Level",
                    [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5],
                    key="d_opp1_level"
                )

                # Opponent 2 selection
                opp2_choice = st.selectbox("Select Opponent 2", dropdown_options, key="d_opp2_choice")
                if opp2_choice == "Enter new name...":
                    opp2 = st.text_input("Enter Opponent 2 Name", key="d_opp2_text", placeholder="Enter second opponent's name")
                else:
                    opp2 = opp2_choice
                    st.text_input("Selected Opponent 2", value=opp2, disabled=True, key="d_opp2_display")
                
                opp2_level = st.selectbox(
                    "Opponent 2 Level",
                    [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5],
                    key="d_opp2_level"
                )

                st.divider()
                st.write("**Match Score**")
                col1, col2 = st.columns(2)
                with col1:
                    user_score = st.number_input("Your Team Score", min_value=0, step=1, key="d_usr_score")
                with col2:
                    opp_score = st.number_input("Opponent Team Score", min_value=0, step=1, key="d_opp_score")

                submitted = st.form_submit_button("Add Doubles Match")
                if submitted:
                    errors = []
                    
                    # Validation
                    if d_date > date.today():
                        errors.append("Date cannot be in the future.")
                    
                    # Get the actual names
                    final_partner = partner if partner_choice == "Enter new name..." else partner_choice
                    final_opp1 = opp1 if opp1_choice == "Enter new name..." else opp1_choice
                    final_opp2 = opp2 if opp2_choice == "Enter new name..." else opp2_choice
                    
                    # Validate names
                    for name, label in [(final_partner, "Partner"), (final_opp1, "Opponent 1"), (final_opp2, "Opponent 2")]:
                        if not name or not name.strip():
                            errors.append(f"{label} name is required.")
                        elif not re.fullmatch(r"[A-Za-z ]+", name.strip()):
                            errors.append(f"{label} name must contain only letters and spaces.")
                    
                    # Check for duplicate names
                    names = [final_partner.strip(), final_opp1.strip(), final_opp2.strip()]
                    if len(set(names)) != len(names):
                        errors.append("All players must have different names.")
                    
                    if user_score == opp_score:
                        errors.append("Scores cannot be tied. Please enter different scores.")
                    
                    if errors:
                        for error in errors:
                            st.error(error)
                    else:
                        if addDoublesMatch(
                            current_user_id=user.id,
                            match_date=d_date,
                            partner=final_partner.strip(),
                            partner_level=part_level,
                            opp1=final_opp1.strip(),
                            opp1_level=opp1_level,
                            opp2=final_opp2.strip(),
                            opp2_level=opp2_level,
                            user_score=user_score,
                            opponent_score=opp_score
                        ):
                            st.success("Doubles match added successfully!")
                            st.cache_data.clear()
                            # Clear form fields
                            for key in ['d_date', 'd_partner_choice', 'd_partner_text', 'd_part_level', 
                                       'd_opp1_choice', 'd_opp1_text', 'd_opp1_level',
                                       'd_opp2_choice', 'd_opp2_text', 'd_opp2_level', 
                                       'd_usr_score', 'd_opp_score']:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()

    st.divider()

    # Match History & Edit Toggle
    st.markdown("## Match History")
    if st.button("✏️ " + ("Exit Edit Mode" if st.session_state.edit_mode else "Edit Match Log")):
        st.session_state.edit_mode = not st.session_state.edit_mode
        st.rerun()

    df = getMatches(user.id)
    if df.empty:
        st.info("No matches to show yet.")
        return

    # Initialize the view type in session state if not exists
    if 'match_log_view_type' not in st.session_state:
        st.session_state.match_log_view_type = "Singles"
    
    match_type_view = st.radio(
        "View", 
        ["Singles", "Doubles"], 
        horizontal=True, 
        key="match_log_type",
        index=0 if st.session_state.match_log_view_type == "Singles" else 1
    )
    
    # Update session state when radio changes
    if match_type_view != st.session_state.match_log_view_type:
        st.session_state.match_log_view_type = match_type_view

    if 'selected_matches' not in st.session_state:
        st.session_state.selected_matches = set()

    if match_type_view == "Singles":
        st.subheader("Your Singles Matches")
        df_s = df[df["match_type"] == "singles"].copy()
        
        if df_s.empty:
            st.info("No singles matches found.")
            return
            
        match_ids = df_s["id"].tolist()

        df_s["match_date"] = pd.to_datetime(df_s["match_date"]).dt.date
        df_s["match_date"] = pd.to_datetime(df_s["match_date"]).dt.strftime('%m/%d/%Y')
        df_s.rename(columns={
            "match_date": "Match Date",
            "user_team_score": "Your Score",
            "opponent_team_score": "Opponent Score",
            "opponent_1": "Opponent",
            "opponent_1_level": "Opponent Level",
        }, inplace=True)
        df_s["Win or Loss"] = df_s.apply(
            lambda r: "Win" if r["Your Score"] > r["Opponent Score"] else "Loss", axis=1
        )
        df_s = df_s[[
            "Match Date", "Win or Loss", "Your Score", "Opponent Score",
            "Opponent", "Opponent Level"
        ]].sort_values("Match Date", ascending=False)

        if st.session_state.edit_mode:
            selection_df = pd.DataFrame({
                "Select": [False] * len(df_s),
                "Match ID": match_ids
            })
            display_df = pd.concat( 
                [selection_df["Select"].reset_index(drop=True),
                 df_s.reset_index(drop=True)], axis=1
            )
            edited_df = st.data_editor(
                display_df,
                disabled=df_s.columns.tolist(),
                hide_index=True,
                use_container_width=True,
                key="singles_editor"
            )
            selected_indices = edited_df.index[edited_df["Select"]].tolist()
            selected_ids = [match_ids[i] for i in selected_indices]
            
            col_del, col_warn = st.columns([2, 8])
            with col_del:
                delete_button = st.button(
                    "🗑️ Delete Selected",
                    key="delete_singles",
                    disabled=not selected_ids
                )
            with col_warn:
                if selected_ids:
                    st.warning(f"{len(selected_ids)} match{'es' if len(selected_ids) > 1 else ''} selected")
                    
            if delete_button and selected_ids:
                for mid in selected_ids:
                    deleteMatch(mid, user.id)
                st.success(f"Deleted {len(selected_ids)} match{'es' if len(selected_ids) > 1 else ''}")
                st.cache_data.clear()
                st.rerun()
        else:
            styled = (
                df_s.style
                  .applymap(highlight_win_loss, subset=["Win or Loss"])
                  .set_properties(**{"font-weight": "bold"}, subset=["Win or Loss"])
                  .format({"Opponent Level": "{:.1f}"})
            )
            st.dataframe(styled, use_container_width=True, hide_index=True)

    else:
        st.subheader("Your Doubles Matches")
        df_d = df[df["match_type"] == "doubles"].copy()
        
        if df_d.empty:
            st.info("No doubles matches found.")
            return
            
        match_ids = df_d["id"].tolist()

        df_d["match_date"] = pd.to_datetime(df_d["match_date"]).dt.date
        df_d["match_date"] = pd.to_datetime(df_d["match_date"]).dt.strftime('%m/%d/%Y')
        df_d.rename(columns={
            "match_date": "Match Date",
            "user_team_score": "Your Score",
            "opponent_team_score": "Opponent Score",
            "player_partner": "Partner",
            "player_partner_level": "Partner Level",
            "opponent_1": "Opponent 1",
            "opponent_1_level": "Opponent 1 Level",
            "opponent_2": "Opponent 2",
            "opponent_2_level": "Opponent 2 Level",
        }, inplace=True)
        df_d["Win or Loss"] = df_d.apply(
            lambda r: "Win" if r["Your Score"] > r["Opponent Score"] else "Loss", axis=1
        )
        df_d = df_d[[
            "Match Date", "Win or Loss", "Your Score", "Opponent Score",
            "Partner", "Partner Level", "Opponent 1", "Opponent 1 Level",
            "Opponent 2", "Opponent 2 Level"
        ]].sort_values("Match Date", ascending=False)

        if st.session_state.edit_mode:
            selection_df = pd.DataFrame({
                "Select": [False] * len(df_d),
                "Match ID": match_ids
            })
            display_df = pd.concat(
                [selection_df["Select"].reset_index(drop=True),
                 df_d.reset_index(drop=True)], axis=1
            )
            edited_df = st.data_editor(
                display_df,
                disabled=df_d.columns.tolist(),
                hide_index=True,
                use_container_width=True,
                key="doubles_editor"
            )
            selected_indices = edited_df.index[edited_df["Select"]].tolist()
            selected_ids = [match_ids[i] for i in selected_indices]
            
            col_del, col_warn = st.columns([2, 8])
            with col_del:
                delete_button = st.button(
                    "🗑️ Delete Selected",
                    key="delete_doubles",
                    disabled=not selected_ids
                )
            with col_warn:
                if selected_ids:
                    st.warning(f"{len(selected_ids)} match{'es' if len(selected_ids) > 1 else ''} selected")
                    
            if delete_button and selected_ids:
                for mid in selected_ids:
                    deleteMatch(mid, user.id)
                st.success(f"Deleted {len(selected_ids)} match{'es' if len(selected_ids) > 1 else ''}")
                st.cache_data.clear()
                st.rerun()
        else:
            styled = (
                df_d.style
                  .applymap(highlight_win_loss, subset=["Win or Loss"])
                  .set_properties(**{"font-weight": "bold"}, subset=["Win or Loss"])
                  .format({
                      "Partner Level": "{:.1f}",
                      "Opponent 1 Level": "{:.1f}",
                      "Opponent 2 Level": "{:.1f}"
                  })
            )
            st.dataframe(styled, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    match_log_page()