#!/usr/bin/env python3
import os
import json
import requests
from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Configuration
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8000))
PRODUCER_URL = os.getenv('PRODUCER_URL', 'http://producer:8001')
CONSUMER_URL = os.getenv('CONSUMER_URL', 'http://consumer:8002')

def check_service_health(service_name, url):
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{url}/status", timeout=3)
        return response.status_code == 200
    except:
        return False

@app.route('/')
def home():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """API endpoint to check service status"""
    producer_healthy = check_service_health('Producer', PRODUCER_URL)
    consumer_healthy = check_service_health('Consumer', CONSUMER_URL)
    
    return jsonify({
        'producer': {
            'healthy': producer_healthy,
            'url': PRODUCER_URL
        },
        'consumer': {
            'healthy': consumer_healthy,
            'url': CONSUMER_URL
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/generate-data')
def api_generate_data():
    """Generate data from producer"""
    try:
        response = requests.get(f"{PRODUCER_URL}/generate-data", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to generate data'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to producer: {str(e)}'}), 500

@app.route('/api/send-data')
def api_send_data():
    """Send data from producer to consumer"""
    try:
        response = requests.get(f"{PRODUCER_URL}/send-data", timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to send data'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to producer: {str(e)}'}), 500

@app.route('/api/process-data', methods=['POST'])
def api_process_data():
    """Process data through consumer"""
    try:
        data = request.get_json()
        response = requests.post(
            f"{CONSUMER_URL}/process-data",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to process data'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to consumer: {str(e)}'}), 500

@app.route('/api/get-processed-data')
def api_get_processed_data():
    """Get processed data from consumer"""
    try:
        response = requests.get(f"{CONSUMER_URL}/get-processed-data", timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to get processed data'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to consumer: {str(e)}'}), 500

@app.route('/api/start-automation')
def api_start_automation():
    """Start automated data generation"""
    try:
        response = requests.get(f"{PRODUCER_URL}/start-automation", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to start automation'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to producer: {str(e)}'}), 500

@app.route('/api/stop-automation')
def api_stop_automation():
    """Stop automated data generation"""
    try:
        response = requests.get(f"{PRODUCER_URL}/stop-automation", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to stop automation'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to producer: {str(e)}'}), 500

@app.route('/api/automation-status')
def api_automation_status():
    """Get automation status"""
    try:
        response = requests.get(f"{PRODUCER_URL}/automation-status", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to get automation status'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to producer: {str(e)}'}), 500

@app.route('/api/view-all-data')
def api_view_all_data():
    """View all processed data"""
    try:
        response = requests.get(f"{CONSUMER_URL}/view-all-data", timeout=10)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to get data history'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to consumer: {str(e)}'}), 500

@app.route('/api/clear-history')
def api_clear_history():
    """Clear data history"""
    try:
        response = requests.get(f"{CONSUMER_URL}/clear-history", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to clear history'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error connecting to consumer: {str(e)}'}), 500

if __name__ == '__main__':
    print(f"WEB UI STARTED on port {SERVICE_PORT}")
    print(f"Producer URL: {PRODUCER_URL}")
    print(f"Consumer URL: {CONSUMER_URL}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
