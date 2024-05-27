from flask import Flask, render_template
import json
import logging
from app.fetch_datasets import fetch_blob_data
from app.process_household_data import process_data
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load configuration from config.json
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except FileNotFoundError as e:
    logger.error(f"Error loading configuration file: {e}")
    raise

connection_string = config.get('connection_string')
container_name = config.get('container_name')

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

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
































