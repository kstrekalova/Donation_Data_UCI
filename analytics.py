"""Analytics and reporting functions"""

from database import DonationDatabase
import pandas as pd
import matplotlib.pyplot as plt

def print_summary():
    """Print overall summary statistics"""
    db = DonationDatabase()
    
    print("=== Donation Summary ===\n")
    
    # Overall stats
    all_data = db.get_all_donations()
    print(f"Total records: {len(all_data)}")
    
    # Summary by category
    summary = db.get_summary_stats()
    print("\nBy Category:")
    print(summary.to_string(index=False))
    
    # Monthly totals
    monthly = db.get_monthly_totals()
    print("\nMonthly Totals:")
    print(monthly.head(12).to_string(index=False))

def plot_trends():
    """Create trend visualizations"""
    db = DonationDatabase()
    
    monthly = db.get_monthly_totals()
    monthly['month'] = pd.to_datetime(monthly['month'])
    
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot weight over time
    axes[0].plot(monthly['month'], monthly['total_weight_lbs'], marker='o')
    axes[0].set_title('Total Weight Donated Over Time')
    axes[0].set_ylabel('Weight (lbs)')
    axes[0].grid(True)
    
    # Plot number of donations
    axes[1].plot(monthly['month'], monthly['num_donations'], marker='o', color='green')
    axes[1].set_title('Number of Donations Over Time')
    axes[1].set_ylabel('Count')
    axes[1].set_xlabel('Month')
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.savefig('donation_trends.png')
    print("✓ Saved chart to donation_trends.png")

if __name__ == "__main__":
    print_summary()
    plot_trends()