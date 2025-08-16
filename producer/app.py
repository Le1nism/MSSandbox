#!/usr/bin/env python3
import os
import time
import random
import json
import requests
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Configuration
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8001))
CONSUMER_URL = os.getenv('CONSUMER_URL', 'http://consumer:8002')

def generate_sensor_data():
    """Generate random sensor data"""
    return {
        'timestamp': datetime.now().isoformat(),
        'temperature': round(random.uniform(18.0, 25.0), 2),
        'humidity': round(random.uniform(40.0, 80.0), 2),
        'pressure': round(random.uniform(1000.0, 1020.0), 2),
        'sensor_id': f"SENSOR_{random.randint(1000, 9999)}"
    }

def send_data_to_consumer(data):
    """Send data to consumer service"""
    try:
        response = requests.post(
            f"{CONSUMER_URL}/process-data",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to consumer: {e}")
        return None

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'service': 'Producer Service',
        'status': 'running',
        'port': SERVICE_PORT,
        'endpoints': {
            'generate_data': '/generate-data',
            'send_data': '/send-data',
            'status': '/status'
        }
    })

@app.route('/generate-data')
def generate_data():
    """Generate and return sensor data"""
    data = generate_sensor_data()
    return jsonify({
        'message': 'Data generated successfully',
        'data': data
    })

@app.route('/send-data')
def send_data():
    """Generate data and send it to consumer"""
    data = generate_sensor_data()
    result = send_data_to_consumer(data)
    
    if result:
        return jsonify({
            'message': 'Data sent to consumer successfully',
            'sent_data': data,
            'consumer_response': result
        })
    else:
        return jsonify({
            'message': 'Failed to send data to consumer',
            'sent_data': data,
            'error': 'Consumer service unavailable'
        }), 500

@app.route('/status')
def status():
    """Service status"""
    return jsonify({
        'service': 'Producer Service',
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'consumer_url': CONSUMER_URL
    })

if __name__ == '__main__':
    print(f"PRODUCER SERVICE STARTED on port {SERVICE_PORT}")
    print(f"Consumer URL: {CONSUMER_URL}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
