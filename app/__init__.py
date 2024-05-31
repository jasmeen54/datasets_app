from flask import Flask, render_template
import json
import logging
from app.fetch_datasets import fetch_blob_data
from app.process_household_data import process_data
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import os

app = Flask(__name__)

connection_string = os.environ.get('AZURE_CONNECTION_STRING')
container_name = os.environ.get('CONTAINER_NAME')

if not connection_string or not container_name:
    logger.error("Connection string or container name is missing in the config file.")
    raise ValueError("Connection string or container name is missing in the config file.")

df = None

def refresh_data():
    global df
    try:
        data = fetch_blob_data(connection_string, container_name)
        df = process_data(data)
        logger.debug(f"Data refreshed: {df.head()}")
    except Exception as e:
        logger.error(f"Error fetching or processing data: {e}")

# Fetch data initially
refresh_data()

# Schedule periodic refresh
scheduler = BackgroundScheduler()
scheduler.add_job(func=refresh_data, trigger="interval", minutes=5)
scheduler.start()

# Ensure the scheduler stops when the Flask app exits
atexit.register(lambda: scheduler.shutdown())

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the dashboard page (using Dash)
@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')

# Register dashboard routes
try:
    from app.dashboard import init_dashboard
    init_dashboard(app)
except ImportError as e:
    logger.error(f"Error importing dashboard module: {e}")
    raise


































