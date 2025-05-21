import streamlit as st
import pandas as pd
from supabase import create_client, Client
import plotly.express as px 
import datetime
from datetime import date
from postgrest.exceptions import APIError  # <-- catch this


# Supabase Connection
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# Getting Match Data
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

# Getting unique players
def get_distinct_players(user_id):
    """
    Fetch every past opponent_1, opponent_2, and player_partner for this user,
    dedupe them, and return a sorted list of names.
    """
    supabase = get_supabase()
    resp = (
        supabase
        .table("matches")
        .select("opponent_1,opponent_2,player_partner")
        .eq("user_id", user_id)
        .execute()
    )
    rows = resp.data or []
    names = set()
    for r in rows:
        if r.get("opponent_1"):
            names.add(r["opponent_1"].strip())
        if r.get("opponent_2"):
            names.add(r["opponent_2"].strip())
        if r.get("player_partner"):
            names.add(r["player_partner"].strip())
    return sorted(names)

# Updating Match Data
def updateMatches(match_id, column, data):
    supabase = get_supabase()
    return supabase.table("matches").update({column: data}).eq('id', match_id).execute()

# Deleting Match Data
def deleteMatch(match_id, user_id):
    supabase = get_supabase()
    return supabase.table("matches").delete().eq('id', match_id).eq('user_id', user_id).execute()


# Adding Singles Match
def addSinglesMatch(current_user_id, match_date, opponent, opponent_level,
                    user_score, opponent_score):
    supabase = get_supabase()
    if isinstance(match_date, (date, datetime)):
        match_date = match_date.isoformat()

    payload = {
        "user_id":             current_user_id,
        "match_date":          match_date,
        "match_type":          "singles",
        "opponent_1":          opponent,
        "opponent_1_level":    float(opponent_level),
        "user_team_score":     int(user_score),
        "opponent_team_score": int(opponent_score),
    }

    try:
        response = supabase.table("matches").insert(payload).execute()
        return response.data
    except APIError as e:
        # Postgres/Supabase errors bubble up here
        st.error(f"Failed to add singles match: {e.message}")
        return None

# Adding Doubles Match
def addDoublesMatch(current_user_id, match_date,
                    partner, partner_level,
                    opp1, opp1_level,
                    opp2, opp2_level,
                    user_score, opponent_score):
    supabase = get_supabase()
    if isinstance(match_date, (date, datetime)):
        match_date = match_date.isoformat()

    payload = {
        "user_id":               current_user_id,
        "match_date":            match_date,
        "match_type":            "doubles",
        "player_partner":        partner,
        "player_partner_level":  float(partner_level),
        "opponent_1":            opp1,
        "opponent_1_level":      float(opp1_level),
        "opponent_2":            opp2,
        "opponent_2_level":      float(opp2_level),
        "user_team_score":       int(user_score),
        "opponent_team_score":   int(opponent_score),
    }

    try:
        response = supabase.table("matches").insert(payload).execute()
        return response.data
    except APIError as e:
        st.error(f"Failed to add doubles match: {e.message}")
        return None


# Getting Currrent Level
@st.cache_data(ttl=300)
def getCurrentLevel(current_user_id):
    supabase = get_supabase()
    response = supabase.rpc(
        'get_current_level', 
        {'p_user_id': current_user_id}
    ).execute()
    
    # Check if we have a result
    return response.data or "No current level found"

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

# Highlight  cells based on win loss
def highlight_win_loss(val):
    if val == "Win":
        return "background-color: lightgreen"
    elif val == "Loss":
        return "background-color: lightcoral"
    return ""

