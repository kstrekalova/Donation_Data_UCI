"""Streamlit app for donation tracking"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database import DonationDatabase
from add_donation import show_add_donation
import config

# Page configuration
st.set_page_config(
    page_title="UCI Donation Tracker",
    page_icon="📦",
    layout="wide"
)

# Initialize database
db = DonationDatabase()

# Sidebar navigation
st.sidebar.title("📦 UCI Donation Tracker")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Donation", "View Data", "Reports", "Community Analysis"]
)

# ============================================
# PAGE 1: DASHBOARD
# ============================================
if page == "Dashboard":
    st.title("📊 Donation Dashboard")
    
    # Load all data
    df = db.get_all_donations()
    
    if len(df) == 0:
        st.warning("No donations in database yet!")
    else:
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.to_period('M')
        
        # ========================================
        # FILTERS
        # ========================================
        st.subheader("🔍 Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            locations = ['All Locations'] + sorted(df['location'].dropna().unique().tolist())
            selected_location = st.selectbox("Filter by Location", locations)
        
        with col2:
            years = ['All Years'] + sorted(df['year'].unique().tolist(), reverse=True)
            selected_year = st.selectbox("Filter by Year", years)
        
        with col3:
            moveout_types = ['All Types'] + sorted(df['moveout'].dropna().unique().tolist())
            selected_moveout = st.selectbox("Filter by Move-out", moveout_types)
        
        # Apply filters
        filtered_df = df.copy()
        if selected_location != 'All Locations':
            filtered_df = filtered_df[filtered_df['location'] == selected_location]
        if selected_year != 'All Years':
            filtered_df = filtered_df[filtered_df['year'] == selected_year]
        if selected_moveout != 'All Types':
            filtered_df = filtered_df[filtered_df['moveout'] == selected_moveout]
        
        st.markdown("---")
        
        # ========================================
        # TOP METRICS
        # ========================================
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Donations", f"{len(filtered_df):,}")
        with col2:
            total_weight = filtered_df['weight_lbs'].sum()
            st.metric("Total Weight (lbs)", f"{total_weight:,.0f}")
        with col3:
            total_bins = filtered_df['bins'].sum()
            st.metric("Total Bins", f"{total_bins:,.0f}")
        with col4:
            locations_count = filtered_df['location'].nunique()
            st.metric("Locations", locations_count)
        
        st.markdown("---")
        
        # ========================================
        # CHARTS ROW 1
        # ========================================
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Donations Over Time")
            monthly = filtered_df.groupby('month')['weight_lbs'].sum().reset_index()
            monthly['month'] = monthly['month'].astype(str)
            fig = px.line(monthly, x='month', y='weight_lbs',
                         labels={'weight_lbs': 'Weight (lbs)', 'month': 'Month'},
                         markers=True)
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📍 Top 10 Locations")
            by_location = filtered_df.groupby('location')['weight_lbs'].sum().sort_values(ascending=False).head(10)
            fig = px.bar(by_location, orientation='h',
                        labels={'value': 'Weight (lbs)', 'location': 'Location'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # ========================================
        # COMMUNITY COMPARISON OVER TIME
        # ========================================
        st.subheader("🏘️ Donations Over Time by Community")

        all_locations = sorted(df['location'].dropna().unique().tolist())
        top_locations = df.groupby('location')['weight_lbs'].sum().nlargest(5).index.tolist()

        # Initialize session state
        if 'selected_communities' not in st.session_state:
            st.session_state.selected_communities = top_locations

        st.write("**Filter Communities:**")

        # Two-column layout for better organization
        left_col, right_col = st.columns([1, 3])

        with left_col:
            st.write("**Quick Actions:**")
            if st.button("🔝 Top 5 Only"):
                st.session_state.selected_communities = top_locations
                st.rerun()
            
            if st.button("✅ Select All"):
                st.session_state.selected_communities = all_locations
                st.rerun()
            
            if st.button("❌ Clear All"):
                st.session_state.selected_communities = []
                st.rerun()
            
            # Exclude specific communities
            st.write("")
            st.write("**Quick Exclude:**")
            common_excludes = ["Goodwill", "Salvation Army", "Other"]  # Add common ones
            for exclude_item in common_excludes:
                if exclude_item in all_locations:
                    if st.button(f"Hide {exclude_item}"):
                        if exclude_item in st.session_state.selected_communities:
                            st.session_state.selected_communities.remove(exclude_item)
                            st.rerun()

        with right_col:
            # Main multiselect (most user-friendly)
            selected_communities = st.multiselect(
                "Communities to display:",
                options=all_locations,
                default=st.session_state.selected_communities,
                help="💡 Tip: Start typing to search (e.g., type 'Mesa' to find 'Mesa Court')"
            )
            
            # Update session state
            st.session_state.selected_communities = selected_communities
            
            # Show count
            st.caption(f"Showing {len(selected_communities)} of {len(all_locations)} communities")

        if selected_communities:
            # Filter to selected communities
            community_df = df[df['location'].isin(selected_communities)].copy()
            
            # Group by month and location
            monthly_by_location = community_df.groupby(['month', 'location'])['weight_lbs'].sum().reset_index()
            monthly_by_location['month'] = monthly_by_location['month'].astype(str)
            
            # Create line chart
            fig = px.line(monthly_by_location, 
                        x='month', 
                        y='weight_lbs',
                        color='location',
                        labels={'weight_lbs': 'Weight (lbs)', 'month': 'Month', 'location': 'Location'},
                        markers=True,
                        title=f"Donation Trends for {len(selected_communities)} Communities")
            fig.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Stacked area chart
            st.subheader("📊 Stacked View")
            fig_area = px.area(monthly_by_location,
                            x='month',
                            y='weight_lbs',
                            color='location',
                            labels={'weight_lbs': 'Weight (lbs)', 'month': 'Month', 'location': 'Location'})
            fig_area.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig_area, use_container_width=True)
            
        else:
            st.info("👆 Select at least one community above to view comparison charts")

# ============================================
# PAGE 2: ADD DONATION
# ============================================
elif page == "Add Donation":
    show_add_donation()
    st.title("➕ Add New Donation")
    
    with st.form("donation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            year = st.number_input("Year*", min_value=2010, max_value=2030, 
                                  value=datetime.now().year)
            month = st.selectbox("Month*", 
                                options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                                format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
            location = st.text_input("Location*", placeholder="e.g., Mesa Court, Middle Earth")
        
        with col2:
            weight = st.number_input("Weight (lbs)", min_value=0.0, value=0.0, step=0.1)
            bins = st.number_input("Number of Bins", min_value=0, value=0, step=1)
            moveout = st.selectbox("Move-out Type", ['', 'Undergrad', 'Graduate', 'Other'])
        
        notes = st.text_area("Notes", placeholder="Additional information...")
        
        submitted = st.form_submit_button("💾 Save Donation")
        
        if submitted:
            # Validate required fields
            if not location:
                st.error("Please fill in all required fields (marked with *)")
            else:
                try:
                    record_id = db.add_donation(
                        year=year,
                        month=month,
                        location=location,
                        weight_lbs=float(weight) if weight > 0 else None,
                        bins=int(bins) if bins > 0 else None,
                        moveout=moveout if moveout else None,
                        notes=notes if notes else None
                    )
                    st.success(f"✅ Donation saved successfully! (ID: {record_id})")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error saving donation: {e}")

# ============================================
# PAGE 3: VIEW DATA
# ============================================
elif page == "View Data":
    st.title("📋 View All Donations")
    
    df = db.get_all_donations()
    
    if len(df) == 0:
        st.warning("No donations in database yet!")
    else:
        # Filters
        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            locations = ['All'] + sorted(df['location'].dropna().unique().tolist())
            selected_location = st.selectbox("Location", locations)
        
        with col2:
            df['date'] = pd.to_datetime(df['date'])
            years = ['All'] + sorted(df['date'].dt.year.unique().tolist(), reverse=True)
            selected_year = st.selectbox("Year", years)
        
        with col3:
            moveout_types = ['All'] + sorted(df['moveout'].dropna().unique().tolist())
            selected_moveout = st.selectbox("Move-out Type", moveout_types)
        
        # Apply filters
        filtered_df = df.copy()
        if selected_location != 'All':
            filtered_df = filtered_df[filtered_df['location'] == selected_location]
        if selected_year != 'All':
            filtered_df = filtered_df[filtered_df['date'].dt.year == selected_year]
        if selected_moveout != 'All':
            filtered_df = filtered_df[filtered_df['moveout'] == selected_moveout]
        
        st.write(f"Showing {len(filtered_df)} of {len(df)} records")
        
        # Display data
        display_cols = ['date', 'location', 'weight_lbs', 'bins', 'moveout', 'notes']
        display_df = filtered_df[display_cols].sort_values('date', ascending=False)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"donations_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ============================================
# PAGE 4: REPORTS
# ============================================
elif page == "Reports":
    st.title("📈 Reports")
    
    df = db.get_all_donations()
    
    if len(df) == 0:
        st.warning("No donations in database yet!")
    else:
        df['date'] = pd.to_datetime(df['date'])
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", df['date'].min())
        with col2:
            end_date = st.date_input("End Date", df['date'].max())
        
        # Filter by date range
        mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
        filtered_df = df[mask]
        
        st.markdown("---")
        
        # Summary stats
        st.subheader("Summary Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Donations", f"{len(filtered_df):,}")
        with col2:
            st.metric("Total Weight (lbs)", f"{filtered_df['weight_lbs'].sum():,.0f}")
        with col3:
            st.metric("Total Bins", f"{filtered_df['bins'].sum():,.0f}")
        
        # Monthly breakdown
        st.subheader("Monthly Breakdown")
        monthly = filtered_df.groupby(filtered_df['date'].dt.to_period('M')).agg({
            'id': 'count',
            'weight_lbs': 'sum',
            'bins': 'sum'
        }).rename(columns={
            'id': 'Count',
            'weight_lbs': 'Weight (lbs)',
            'bins': 'Bins'
        })
        monthly.index = monthly.index.astype(str)
        st.dataframe(monthly, use_container_width=True)
        
        # Breakdown by move-out type
        if 'moveout' in filtered_df.columns and filtered_df['moveout'].notna().any():
            st.subheader("Breakdown by Move-out Type")
            moveout_stats = filtered_df.groupby('moveout').agg({
                'id': 'count',
                'weight_lbs': 'sum',
                'bins': 'sum'
            }).rename(columns={
                'id': 'Count',
                'weight_lbs': 'Weight (lbs)',
                'bins': 'Bins'
            })
            st.dataframe(moveout_stats, use_container_width=True)
        
        # Download report
        st.markdown("---")
        report_csv = monthly.to_csv()
        st.download_button(
            label="📥 Download Report as CSV",
            data=report_csv,
            file_name=f"donation_report_{start_date}_{end_date}.csv",
            mime="text/csv"
        )

# ============================================
# PAGE 5: COMMUNITY ANALYSIS
# ============================================
elif page == "Community Analysis":
    st.title("🏘️ Community Analysis")
    
    df = db.get_all_donations()
    
    if len(df) == 0:
        st.warning("No donations in database yet!")
    else:
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.to_period('M')
        
        # Community selector
        st.subheader("Select a Community")
        all_locations = sorted(df['location'].dropna().unique().tolist())
        selected_community = st.selectbox("Choose community:", all_locations)
        
        # Filter to selected community
        community_df = df[df['location'] == selected_community]
        
        # Stats for this community
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Donations", f"{len(community_df):,}")
        with col2:
            st.metric("Total Weight (lbs)", f"{community_df['weight_lbs'].sum():,.0f}")
        with col3:
            st.metric("Total Bins", f"{community_df['bins'].sum():,.0f}")
        with col4:
            avg_weight = community_df['weight_lbs'].mean()
            st.metric("Avg Weight/Donation", f"{avg_weight:,.0f} lbs")
        
        st.markdown("---")
        
        # Timeline
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Timeline")
            monthly = community_df.groupby('month')['weight_lbs'].sum().reset_index()
            monthly['month'] = monthly['month'].astype(str)
            fig = px.bar(monthly, x='month', y='weight_lbs',
                        labels={'weight_lbs': 'Weight (lbs)', 'month': 'Month'})
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 By Year")
            yearly = community_df.groupby('year').agg({
                'id': 'count',
                'weight_lbs': 'sum',
                'bins': 'sum'
            }).rename(columns={
                'id': 'Donations',
                'weight_lbs': 'Weight (lbs)',
                'bins': 'Bins'
            })
            st.dataframe(yearly, use_container_width=True)
        
        # Compare to overall average
        st.subheader("🔍 How does this community compare?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # This community's average
            community_avg = community_df.groupby('year')['weight_lbs'].sum().mean()
            st.metric(
                f"{selected_community} - Avg lbs/year",
                f"{community_avg:,.0f}"
            )
        
        with col2:
            # Overall average per community per year
            overall_avg = df.groupby(['location', 'year'])['weight_lbs'].sum().mean()
            st.metric(
                "All Communities - Avg lbs/year",
                f"{overall_avg:,.0f}"
            )
        
        # Percentage of total
        community_total = community_df['weight_lbs'].sum()
        overall_total = df['weight_lbs'].sum()
        pct = (community_total / overall_total * 100)
        
        st.info(f"💡 {selected_community} represents **{pct:.1f}%** of total donations")
        
        # Recent donations table
        st.subheader("📋 Recent Donations")
        recent = community_df.sort_values('date', ascending=False).head(20)
        st.dataframe(
            recent[['date', 'weight_lbs', 'bins', 'moveout', 'notes']],
            use_container_width=True,
            hide_index=True
        )