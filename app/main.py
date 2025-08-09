from flask import Flask, render_template, jsonify, send_from_directory, request
from flask_cors import CORS
import os
from pathlib import Path
import logging
from data_manager import DataManager
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for development

# Initialize data manager
data_manager = DataManager()

def startup():
    """Start data collection service on first request"""
    try:
        logger.info("Starting data collection service...")
        data_manager.start_data_collection()
        logger.info("Data collection service started successfully")
    except Exception as e:
        logger.error(f"Failed to start data collection service: {e}")

# Use a more compatible approach for Flask 2.3+
def _start_collector_once():
    """Start data collection service on first request"""
    try:
        logger.info("Starting data collection service...")
        data_manager.start_data_collection()
        logger.info("Data collection service started successfully")
    except Exception as e:
        logger.error(f"Failed to start data collection service: {e}")

# Start the data collection when the app starts
startup()

# Serve React frontend
@app.route("/")
def index():
    return send_from_directory('frontend/dist', 'index.html')

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(f"frontend/dist/{path}"):
        return send_from_directory('frontend/dist', path)
    return send_from_directory('frontend/dist', 'index.html')

# API endpoints
@app.route("/api/dashboard")
def dashboard():
    """Return real dashboard data from Chrome history"""
    try:
        # Get days parameter from query string, default to 7
        days_back = request.args.get('days', 7, type=int)
        
        # Get real data from data manager
        dashboard_data = data_manager.get_dashboard_data(days_back=days_back)
        
        logger.info(f"Dashboard data requested for last {days_back} days")
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        # Return fallback data if there's an error
        return jsonify(data_manager._get_fallback_data())

@app.route("/api/refresh")
def refresh_data():
    """Force refresh of Chrome history data"""
    try:
        success = data_manager.force_refresh()
        if success:
            return jsonify({"status": "success", "message": "Data refreshed successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to refresh data"}), 500
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/status")
def status():
    """Get data collection status"""
    try:
        status_info = {
            "data_collection_running": data_manager.is_running,
            "last_collection_time": data_manager.last_collection_time.isoformat() if data_manager.last_collection_time else None,
            "influxdb_connected": data_manager.influx_service.client is not None
        }
        return jsonify(status_info)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "youknow-backend"})

@app.route("/api/chrome-test")
def chrome_test():
    """Test Chrome history access and get information"""
    try:
        # Test Chrome history access
        access_test = data_manager.test_chrome_history_access()
        
        # Get Chrome history information
        history_info = data_manager.get_chrome_history_info()
        
        # Get InfluxDB info
        influx_info = data_manager.influx_service.get_info() if data_manager.influx_service.client else None
        
        test_results = {
            "chrome_history": {
                "access_test": access_test,
                "info": history_info
            },
            "influxdb": influx_info,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(test_results)
        
    except Exception as e:
        logger.error(f"Error testing Chrome history: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
