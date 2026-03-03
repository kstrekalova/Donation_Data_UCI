"""Configuration settings for the donation tracking system"""

# Database configuration

import os

# Get the directory where config.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database will always be in the same folder as config.py
DATABASE_PATH = os.path.join(BASE_DIR, 'donation_data.db')
# DATABASE_PATH = 'donation_data.db'

# Date format
DATE_FORMAT = '%Y-%m-%d'



### Optional, if there's a need to store this info:

# # Valid item categories
# ITEM_CATEGORIES = [
#     'Furniture',
#     'Electronics',
#     'Office Supplies',
#     'Textiles',
#     'Books',
#     'Lab Equipment',
#     'Other'
# ]

# # Valid conditions
# VALID_CONDITIONS = ['excellent', 'good', 'fair', 'needs repair']

# # Valid units
# VALID_UNITS = ['items', 'pounds', 'boxes', 'bags']
