# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')

# Add the src directory to the Python path
import sys
sys.path.insert(0, SRC_DIR)

# Now you can import your app
from ecommerce import app, db