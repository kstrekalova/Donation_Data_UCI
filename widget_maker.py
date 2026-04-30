import plotly.express as px
import pandas as pd
from database import DonationDatabase

db = DonationDatabase()
df = db.get_all_donations()

df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.to_period('M').astype(str)

# Filter to housing communities only
housing = [
    'ACC',
    'Arroyo Vista',
    'Campus Village',
    'Mesa Court',
    'Middle Earth',
    'Palo Verde',
    'Verano Place'
]
df = df[df['location'].isin(housing)]

monthly_by_location = df.groupby(['month', 'location'])['weight_lbs'].sum().reset_index()

fig = px.line(monthly_by_location,
              x='month',
              y='weight_lbs',
              color='location',
              title='Donation Trends by Community',
              labels={'weight_lbs': 'Weight (lbs)', 'month': 'Month', 'location': 'Community'},
              markers=True)

fig.update_layout(xaxis_tickangle=-45, height=500)

# Export as standalone HTML
fig.update_xaxes(rangeslider_visible=True)
fig.write_html('donation_widget.html', include_plotlyjs='cdn')
print('✅ Exported!')