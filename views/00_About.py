import streamlit as st


def about_page():
    """
    Display the About page for SmashTrack using native Streamlit components
    """
    # Page header with logo and title
    col1, col2 = st.columns([1, 4])
    with col1:
        # Emoji logo
        st.image("assets/logo.png", width=100)
    with col2:
        st.title("SmashTrack")
        st.markdown("#### *Your Personal Pickleball Performance Tracker*")
    
    # Separator
    st.divider()

    
    # Introduction
    st.markdown("""
    **SmashTrack** is the ultimate companion for pickleball enthusiasts looking to track their progress, 
    analyze their performance, and improve their game. Whether you're a casual player or a competitive athlete, 
    SmashTrack provides the insights you need to elevate your pickleball journey.
    """)
    
    # Key Features section
    st.header("Key Features")
    
    # Create a 2x2 grid of features using columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Feature 1
        st.subheader("📊 Match Tracking")
        st.markdown("""
        Record singles and doubles matches with detailed information including scores, opponent levels, 
        and match notes. Never lose track of your pickleball history again.
        """)
        
        # Feature 3
        st.subheader("🏅 Skill Level Tracking")
        st.markdown("""
        Monitor your skill development with our level tracking system. Record changes to your 
        official level and see how your performance correlates with your progression.
        """)
    
    with col2:
        # Feature 2
        st.subheader("📈 Performance Analytics")
        st.markdown("""
        Gain valuable insights with interactive visualizations of your win/loss record, 
        performance against players of different levels, and progression over time.
        """)
        
        # Feature 4
        st.subheader("🔍 Opponent Analysis")
        st.markdown("""
        Track your performance against specific opponents and opponent levels. Identify patterns 
        and adapt your strategy to improve your game against challenging competitors.
        """)
    
    # How It Works section
    st.header("How It Works")
    
    # Create steps with Streamlit markdown
    st.markdown("""
    1. **Log In** - Securely access your personal SmashTrack account
    2. **Record Matches** - Input details about your singles or doubles matches
    3. **Track Your Level** - Update your skill level as you improve
    4. **Analyze Performance** - View statistics and visualizations of your pickleball journey
    5. **Improve Your Game** - Use insights to focus your practice and elevate your play
    """)
    
    # Call to Action
    st.divider()
    cta_col1, cta_col2, cta_col3 = st.columns([1.5, 3, 1.5])
        
    # FAQ Section
    st.header("Frequently Asked Questions")
    
    faq_1 = st.expander("What is a 'level' in pickleball?")
    with faq_1:
        st.markdown("""
        Pickleball skill levels typically range from 1.0 to 5.5, with each increment representing 
        advancement in skills, strategy, and overall gameplay. This standardized rating system helps players 
        find appropriate competition and track their progression.
        """)
    
    faq_2 = st.expander("Can I track both singles and doubles matches?")
    with faq_2:
        st.markdown("""
        Absolutely! SmashTrack is designed to record both singles and doubles matches, including 
        information about your partner and opponents' levels.
        """)
    
    faq_3 = st.expander("Is my data secure?")
    with faq_3:
        st.markdown("""
        Yes, SmashTrack uses Supabase's robust security features including row-level security policies
        to ensure that your match data is private and only accessible to you.
        """)
    
    faq_4 = st.expander("How do I update my skill level?")
    with faq_4:
        st.markdown("""
        Simply navigate to the Profile section and update your current level. The system will maintain 
        a history of your level progression, allowing you to see how you've improved over time.
        """)
    
    # Contact & Support section
    st.header("Contact & Support")
    
    # Create a 3-column layout for contact info
    contact_col1, contact_col2, contact_col3 = st.columns(3)
    
    with contact_col1:
        st.subheader("📧 Email")
        st.markdown("support@smashtrack.com")
    
    with contact_col2:
        st.subheader("🌐 Social Media")
        st.markdown("Twitter | Instagram | Facebook")
    
    with contact_col3:
        st.subheader("💬 Feedback")
        st.markdown("Have suggestions? Let us know!")
    
    # Footer
    st.divider()
    st.caption("© 2025 SmashTrack - Elevate your pickleball game with data-driven insights")

# For testing the about page directly
if __name__ == "__main__":
    about_page()