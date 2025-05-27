import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import (
    get_supabase, getCurrentLevel_safe, set_player_level, 
    getMatches_safe, get_distinct_players_safe
)


def get_level_history(user_id):
    """Get player's level history"""
    supabase = get_supabase()
    try:
        response = supabase.table("player_levels") \
                          .select("level,effective_date,notes") \
                          .eq('user_id', user_id) \
                          .order('effective_date', desc=True) \
                          .execute()
        
        data = response.data or []
        if data:
            df = pd.DataFrame(data)
            df['effective_date'] = pd.to_datetime(df['effective_date'])
            return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()


def get_activity_summary(df):
    """Get basic activity summary"""
    if df.empty:
        return {
            'total_matches': 0,
            'first_match': None,
            'last_match': None,
            'total_opponents': 0
        }
    
    return {
        'total_matches': len(df),
        'first_match': df['match_date'].min(),
        'last_match': df['match_date'].max(),
        'total_opponents': len(set(
            list(df['opponent_1'].dropna()) + 
            list(df['opponent_2'].dropna())
        ))
    }


def profile_page():
    supabase = get_supabase()
    
    # Header section
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("assets/user.png", width=100)
    with col2:
        st.title("Profile Page")

    st.divider()

    st.markdown("""
       **The SmashTrack Profile Page** is where you can view and update your profile information, including your current level and account preferences.
    """)   

    # Get user info
    resp = supabase.auth.get_user()
    user = resp.user  

    if user:
        display_name = user.user_metadata.get("display_name", "Unknown User")
    else:
        display_name = "Unknown User"
        st.error("Unable to load user information")
        return

    st.markdown(f"""Welcome back, :green-background[**{display_name}**] !""")

    # Main profile sections
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Account Information
        with st.container(border=True):
            st.subheader("📧 Account Information")
            st.markdown(f"**Email:** {user.email}")
            st.markdown(f"**Account Created:** {pd.to_datetime(user.created_at).strftime('%B %d, %Y')}")
            
            # Activity Summary
            matches_df = getMatches_safe(user.id)
            activity = get_activity_summary(matches_df)
            
            st.markdown("**Activity Summary:**")
            st.markdown(f"• Total Matches: **{activity['total_matches']}**")
            if activity['first_match']:
                st.markdown(f"• First Match: **{activity['first_match'].strftime('%B %d, %Y')}**")
            if activity['last_match']:
                st.markdown(f"• Last Match: **{activity['last_match'].strftime('%B %d, %Y')}**")
            st.markdown(f"• Unique Opponents: **{activity['total_opponents']}**")

    with col2:
        # Current Level Section
        with st.container(border=True):
            st.subheader("💪 Your Current Level")
            current_level = getCurrentLevel_safe(user.id)
            st.markdown(f""" Current Level: :blue-background[**{current_level}**]""")

            # Level update form
            if "show_level_form" not in st.session_state:
                st.session_state.show_level_form = False

            if st.button("Update Level", key="toggle_form"):
                st.session_state.show_level_form = not st.session_state.show_level_form

            if st.session_state.show_level_form:
                with st.form("level_update_form"):
                    new_level = st.selectbox("Select New Level", 
                                           ["2.0","2.5","3.0","3.5","4.0","4.5","5.0", "5.5"])
                    effective_date = st.date_input("Effective Date")
                    notes = st.text_area("Notes (Optional)", 
                                       placeholder="e.g., Tournament result, coaching assessment...")

                    if st.form_submit_button("Update Level"):
                        resp = set_player_level(user.id, new_level, effective_date, notes)
                        if resp.data:
                            getCurrentLevel_safe.clear()
                            st.success("Level updated successfully!")
                            st.session_state.show_level_form = False
                            st.rerun()
                        else:
                            st.error("Failed to update level")

    # Level History Section
    st.subheader("📈 Level History")
    level_history = get_level_history(user.id)
    
    if not level_history.empty:
        with st.container(border=True):
            # Display as a table with proper headers
            display_df = level_history.copy()
            display_df['Date'] = display_df['effective_date'].dt.strftime('%m/%d/%Y')
            display_df['Level'] = display_df['level']
            display_df['Notes'] = display_df['notes'].fillna('No notes')
            
            # Select and reorder columns for display
            display_df = display_df[['Level', 'Date', 'Notes']]
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No level history found. Update your level above to start tracking your progress!")

    # Frequent Players Section
    st.subheader("🤝 Your Tennis Network")
    players = get_distinct_players_safe(user.id)
    
    if players:
        with st.container(border=True):
            st.markdown(f"**Players you've faced:** {len(players)} unique opponents")
            
            # Show frequent opponents (top 5)
            if not matches_df.empty:
                opponent_counts = {}
                for _, match in matches_df.iterrows():
                    if pd.notna(match['opponent_1']):
                        opponent_counts[match['opponent_1']] = opponent_counts.get(match['opponent_1'], 0) + 1
                    if pd.notna(match['opponent_2']):
                        opponent_counts[match['opponent_2']] = opponent_counts.get(match['opponent_2'], 0) + 1
                
                if opponent_counts:
                    top_opponents = sorted(opponent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                    st.markdown("**Most Frequent Opponents:**")
                    for opponent, count in top_opponents:
                        st.markdown(f"• {opponent}: **{count}** match{'es' if count > 1 else ''}")
            
            # Show all players in an expander
            with st.expander("View All Players"):
                cols = st.columns(3)
                for i, player in enumerate(players):
                    with cols[i % 3]:
                        st.markdown(f"• {player}")
    else:
        st.info("No players found. Add some matches to build your tennis network!")

    # Account Actions Section
    st.subheader("🔧 Account Actions")
    with st.container(border=True):
        if st.button("Export My Data", help="Download all your match data as CSV"):
            if not matches_df.empty:
                # Remove sensitive columns and timestamp columns before export
                export_df = matches_df.drop(columns=['id', 'user_id', 'created_at', 'updated_at'], errors='ignore')
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"smashtrack_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data to export")

    # Quick Stats Footer
    if not matches_df.empty:
        st.divider()
        st.markdown("### Quick Profile Stats")
        col1, col2, col3, col4 = st.columns(4)
        
        wins = len(matches_df[matches_df['user_team_score'] > matches_df['opponent_team_score']])
        win_rate = (wins / len(matches_df)) * 100 if len(matches_df) > 0 else 0
        
        with col1:
            st.metric("Total Matches", len(matches_df))
        with col2:
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col3:
            singles_matches = len(matches_df[matches_df['match_type'] == 'singles'])
            st.metric("Singles Matches", singles_matches)
        with col4:
            doubles_matches = len(matches_df[matches_df['match_type'] == 'doubles'])
            st.metric("Doubles Matches", doubles_matches)


if __name__ == "__main__":
    profile_page()