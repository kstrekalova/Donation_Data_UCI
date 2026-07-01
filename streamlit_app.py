"""Streamlit app for donation tracking"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database import DonationDatabase
from database import get_connection
from add_donation import show_add_donation
from admin import show_admin
import config
import calendar

# Page configuration
st.set_page_config(
    page_title="UCI Donation Tracker",
    layout="wide"
)

# Define housing vs partner groups
HOUSING = ['ACC', 'Arroyo Vista', 'Campus Village', 'Mesa Court', 'Middle Earth', 'Palo Verde', 'Verano Place']
PARTNERS = ['AMVETS', 'ATRS', 'Basic Needs', 'Dept Freecycle', 'FRESH', 'Food', "Mary's Kitchen", 'Goodwill', 'Goodwill MO', 'One World', 'Tex Green', 'Unknown', 'Zot exchange']

# Initialize database
db = DonationDatabase()

# Sidebar navigation
st.sidebar.title("UCI Donation Tracker")
# Build page list — only show Admin tab if logged in as admin
pages = ["Dashboard - Housing", "Dashboard - Partners", "Add Donation", "View Data", "Reports", "Community Analysis"]
if st.session_state.get("role") == "admin":
    pages.append("Admin")
page = st.sidebar.radio("Navigation", pages)

# ============================================
# PAGE 1: DASHBOARD - HOUSING
# ============================================
if page == "Dashboard - Housing":
    st.title("Housing Donation Dashboard")

    df = db.get_all_donations()
    df['weight_lbs'] = df['weight_lbs'].fillna(0)
    df = df[df['location'].isin(HOUSING)]

    if len(df) == 0:
        st.warning("No housing donations in database yet!")
    else:
        highlight_year = 2025
        highlight_month = 6
        ay_start_year = 2024

        # Admin config for metrics: ===
        if st.session_state.get("role") == "admin":
            with st.expander("Configure Highlight Metrics"):
                col1, col2 = st.columns(2)
                with col1:
                    highlight_year = st.number_input("Highlight Month — Year", value=2025, min_value=2000, max_value=2040)
                    highlight_month = st.number_input("Highlight Month — Month", value=6, min_value=1, max_value=12)
                with col2:
                    ay_start_year = st.number_input("Academic Year Start", value=2024, min_value=2000, max_value=2040)
        # ===

        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.to_period('M')
        df['academic_year'] = df['date'].apply(lambda x: x.year if x.month >= 9 else x.year - 1)
        df['ay_label'] = df['academic_year'].astype(str) + '-' + (df['academic_year'] + 1).astype(str)

        # FILTERS
        st.subheader("Filters")
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

        filtered_df = df.copy()
        if selected_location != 'All Locations':
            filtered_df = filtered_df[filtered_df['location'] == selected_location]
        if selected_year != 'All Years':
            filtered_df = filtered_df[filtered_df['year'] == selected_year]
        if selected_moveout != 'All Types':
            filtered_df = filtered_df[filtered_df['moveout'] == selected_moveout]

        st.markdown("---")

        # TOP METRICS
        col1, col2 = st.columns(2)
        month_name = calendar.month_name[highlight_month]


        with col1:
            june_mask = (df['date'].dt.year == highlight_year) & (df['date'].dt.month == highlight_month)
            june_total = df.loc[june_mask, 'weight_lbs'].sum()
            st.metric(f"Pounds Donated — {month_name} {highlight_year}", f"{june_total:,.0f} lbs")

        with col2:
            ay_mask = (df['date'] >= f'{ay_start_year}-09-01') & (df['date'] <= f'{ay_start_year + 1}-08-31')
            ay_total = df.loc[ay_mask, 'weight_lbs'].sum()
            st.metric(f"Pounds Donated — {ay_start_year}-{str(ay_start_year + 1)[-2:]} Academic Year", f"{ay_total:,.0f} lbs")

        st.markdown("---")

        # CHARTS ROW 1
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Donations by Academic Year")
            ay_totals = filtered_df.groupby('ay_label')['weight_lbs'].sum().reset_index()
            ay_totals.columns = ['Academic Year', 'Total Weight (lbs)']
            fig = px.bar(ay_totals, x='Academic Year', y='Total Weight (lbs)')
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Weight by Housing Community")
            by_location = filtered_df.groupby('location')['weight_lbs'].sum().sort_values(ascending=True)
            fig = px.bar(by_location, orientation='h',
                        labels={'value': 'Weight (lbs)', 'location': 'Community'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        
        # CHARTS ROW 2
        st.subheader("Donations Over Time")
        monthly = filtered_df.groupby('month')['weight_lbs'].sum().reset_index()
        monthly['month'] = monthly['month'].astype(str)
        # Filter to start at 2017 to make up for lacking data
        monthly = monthly[monthly['month'] >= '2017-01']  
        fig = px.line(monthly, x='month', y='weight_lbs',
                    labels={'weight_lbs': 'Weight (lbs)', 'month': 'Month'},
                    markers=True)
        fig.update_layout(xaxis_tickangle=-45, height=400, font=dict(size=18),
                          xaxis=dict(tickfont=dict(size=16)),
                          yaxis=dict(tickfont=dict(size=16)),
                          xaxis_title_font=dict(size=18),
                          yaxis_title_font=dict(size=18))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")

        # COMMUNITY COMPARISON
        st.subheader("Donations Over Time by Community")
        all_locations = sorted(HOUSING)
        top_locations = df.groupby('location')['weight_lbs'].sum().nlargest(5).index.tolist()

        if 'selected_communities' not in st.session_state:
            st.session_state.selected_communities = top_locations

        st.write("**Filter Communities:**")
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

        with right_col:
            valid_defaults = [c for c in st.session_state.selected_communities if c in all_locations]
            if not valid_defaults:
                valid_defaults = top_locations

            selected_communities = st.multiselect(
                "Communities to display:",
                options=all_locations,
                default=valid_defaults,
                help="Start typing to search"
            )
            st.session_state.selected_communities = selected_communities
            st.caption(f"Showing {len(selected_communities)} of {len(all_locations)} communities")

        if selected_communities:
            community_df = df[df['location'].isin(selected_communities)].copy()
            monthly_by_location = community_df.groupby(['month', 'location'])['weight_lbs'].sum().reset_index()
            monthly_by_location['month'] = monthly_by_location['month'].astype(str)
            fig = px.line(monthly_by_location, x='month', y='weight_lbs', color='location',
                        labels={'weight_lbs': 'Weight (lbs)', 'month': 'Month', 'location': 'Location'},
                        markers=True,
                        title=f"Donation Trends for {len(selected_communities)} Communities")
            fig.update_layout(xaxis_tickangle=-45, height=500, font=dict(size=18),
                              xaxis=dict(tickfont=dict(size=16)),
                              yaxis=dict(tickfont=dict(size=16)),
                              xaxis_title_font=dict(size=18),
                              yaxis_title_font=dict(size=18))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select at least one community above to view comparison charts")
    

# ============================================
# PAGE 2: DASHBOARD - PARTNERS
# ============================================
elif page == "Dashboard - Partners":
    st.title("Partner Donations Dashboard")

    df = db.get_all_donations()
    df['weight_lbs'] = df['weight_lbs'].fillna(0)
    df = df[df['location'].isin(PARTNERS)]

    if len(df) == 0:
        st.warning("No partner donations in database yet!")
    else:
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.to_period('M')

        # CHARTS ROW 1
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Total Donations by Partner")
            partner_df = df.groupby('location')['weight_lbs'].sum().reset_index()
            partner_df.columns = ['Partner', 'Total Weight (lbs)']
            fig = px.pie(partner_df, values='Total Weight (lbs)', names='Partner')
            fig.update_traces(textposition='outside', textinfo='percent',
                              insidetextorientation='radial')
            fig.update_layout(height=400, uniformtext_minsize=16, uniformtext_mode='hide')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Weight by Partner")
            by_partner = df.groupby('location')['weight_lbs'].sum().sort_values(ascending=True)
            fig = px.bar(by_partner, orientation='h',
                        labels={'value': 'Weight (lbs)', 'location': 'Partner'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # FILTERS
        st.subheader("Filter Partners")
        all_partners = sorted(PARTNERS)

        if 'selected_partners' not in st.session_state:
            st.session_state.selected_partners = all_partners

        left_col, right_col = st.columns([1, 3])

        with left_col:
            st.write("**Quick Actions:**")
            if st.button("✅ Select All"):
                st.session_state.selected_partners = all_partners
                st.rerun()
            if st.button("❌ Clear All"):
                st.session_state.selected_partners = []
                st.rerun()
            st.write("")

        with right_col:
            selected_partners = st.multiselect(
                "Partners to display:",
                options=all_partners,
                default=[p for p in st.session_state.selected_partners if p in all_partners]
            )
            st.session_state.selected_partners = selected_partners
            st.caption(f"Showing {len(selected_partners)} of {len(all_partners)} partners")

        st.markdown("---")

        
        # TOP METRICS
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Donations", f"{len(df):,}")
        with col2:
            st.metric("Total Weight (lbs)", f"{df['weight_lbs'].sum():,.0f}")
        with col3:
            st.metric("Partner Organizations", df['location'].nunique())

############ Why is filter still at bottom????
        

# ============================================
# PAGE 3: ADD DONATION
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
# PAGE 4: VIEW DATA
# ============================================
elif page == "View Data":
    st.title("View All Donations")
    
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
        display_cols = ['id', 'date', 'location', 'weight_lbs', 'bins', 'moveout', 'notes']
        display_df = filtered_df[display_cols].sort_values('date', ascending=False)
        st.dataframe(
            display_df.drop(columns=['id']),
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
        
        # Allow admin to upload updated CSV
        if st.session_state.get("role") == "admin":
            st.subheader("Upload Updated CSV")
            uploaded_file = st.file_uploader("Upload modified CSV", type="csv")
            
            if uploaded_file:
                new_df = pd.read_csv(uploaded_file)
                
                # Validate columns
                required_cols = {'id', 'date', 'location', 'weight_lbs', 'bins', 'moveout', 'notes'}
                if not required_cols.issubset(new_df.columns):
                    st.error("CSV is missing required columns!")
                else:
                    if st.button("Confirm Upload & Update Database"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        updated = 0
                        for _, row in new_df.iterrows():
                            cursor.execute("""
                                UPDATE donations 
                                SET date=%s, location=%s, weight_lbs=%s, bins=%s, moveout=%s, notes=%s
                                WHERE id=%s
                            """, (row['date'], row['location'], row.get('weight_lbs'),
                                row.get('bins'), row.get('moveout'), row.get('notes'), row['id']))
                            updated += cursor.rowcount
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Updated {updated} records!")
                        st.rerun()

        # Allow by-row deletion of data for admin
        if st.session_state.get("role") == "admin":
            for _, row in display_df.iterrows():
                col1, col2 = st.columns([6, 1])
                col1.write(f"{row['date']} — {row['location']} — {row['weight_lbs']} lbs")
                if col2.button("🗑️ Delete", key=f"del_{row['id']}"):
                    db.delete_donation(row['id'])
                    st.success(f"Deleted record ID {row['id']}")
                    st.rerun()

# ============================================
# PAGE 5: REPORTS
# ============================================
elif page == "Reports":
    st.title("Reports")
    
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
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Donations", f"{len(filtered_df):,}")
        with col2:
            st.metric("Total Weight (lbs)", f"{filtered_df['weight_lbs'].sum():,.0f}")
        
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
# PAGE 6: COMMUNITY ANALYSIS
# ============================================
elif page == "Community Analysis":
    st.title("Community Analysis")
    
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
            st.subheader("Timeline")
            monthly = community_df.groupby('month')['weight_lbs'].sum().reset_index()
            monthly['month'] = monthly['month'].astype(str)
            fig = px.bar(monthly, x='month', y='weight_lbs',
                        labels={'weight_lbs': 'Weight (lbs)', 'month': 'Month'})
            fig.update_layout(xaxis_tickangle=-45,
                              font=dict(size=14))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("By Year")
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

    # ============================================
# PAGE 7: ADMIN PANEL
# ============================================
elif page == "Admin":
    show_admin()