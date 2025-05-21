import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px 
import datetime
from datetime import date

# Supabase Connection
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# Getting Match Data
@st.cache_data(ttl=300)
def getMatches(user_id) -> pd.DataFrame:
    supabase = get_supabase()
    response = supabase.table("matches") \
                      .select("*") \
                      .eq('user_id', user_id) \
                      .order('match_date', desc=True) \
                      .execute()
    
    data = response.data or []
    df = pd.DataFrame(data)
    
    # Convert date columns if data exists
    if not df.empty and 'match_date' in df.columns:
        df['match_date'] = pd.to_datetime(df['match_date'])
        
    return df

# Updating Match Data
def updateMatches(match_id, column, data):
    supabase = get_supabase()
    return supabase.table("matches").update({column: data}).eq('id', match_id).execute()

# Deleting Match Data
def deleteMatch(match_id, user_id):
    supabase = get_supabase()
    return supabase.table("matches").delete().eq('id', match_id).eq('user_id', user_id).execute()


# Adding Singles Match
def addSinglesMatch(current_user_id, date, match_type, opponent, user_score, opponent_score):
    supabase = get_supabase()

    if isinstance(date, (datetime.date, datetime.datetime)):
        date = date.isoformat()

    response = supabase.table("matches").insert({'user_id': current_user_id, 'match_date': date, 'match_type' : match_type, 'opponent_1': opponent,'user_team_score': user_score, 'opponent_team_score': opponent_score}).execute()

    if response.error:
        st.error(f"Failed to update match: {response.error.message}")
        return None

    return response.data

# Adding Doubles Match
def addDoublesMatch(current_user_id, date, match_type ,opponent_1, opponent_2, user_score, opponent_score):
    supabase = get_supabase()

    if isinstance(date, (datetime.date, datetime.datetime)):
        date = date.isoformat()

    response = supabase.table("matches").insert({'user_id': current_user_id, 'match_date': date, 'match_type' : match_type, 'opponent_1': opponent_1, 'opponent_2': opponent_2,'user_team_score': user_score, 'opponent_team_score': opponent_score}).execute()

    if response.error:
        st.error(f"Failed to update match: {response.error.message}")
        return None
    
    return response.data

# Geting Currrent Level
@st.cache_data(ttl=300)
def getCurrentLevel(current_user_id):
    supabase = get_supabase()
    response = supabase.rpc(
        'get_current_level', 
        {'p_user_id': current_user_id}
    ).execute()
    
    # Check if we have a result
    if response.data:
        return response.data[0] if response.data else None
    else:
        return "No level found"

# Updating Current Level
def set_player_level(user_id, new_level, effective_date, notes):
    
    if isinstance(effective_date, date):
        effective_date = effective_date.isoformat()

    supabase = get_supabase()
    response = (
        supabase
        .from_("player_levels")
        .insert({
            "user_id": user_id,
            "level": new_level,
            "effective_date": effective_date,
            "notes": notes
        })
        .execute()
    )
    return response

# Navigation Pages
def register_nav_pages(PAGE_DEFS):
    pages = []
    for defn in PAGE_DEFS:
        pages.append(
            st.Page(
                defn["page"],             
                title=defn["title"],
                icon=defn.get("icon"),
                default=defn.get("default", False),
            )
        )
    return pages

# Get profile data
@st.cache_data(ttl=300)
def getName(user_id):
    supabase = get_supabase()
    display_name = supabase.user_meta_data(user_id).get("display_name")
    st.write(f"Display Name: {display_name}")
    return display_name