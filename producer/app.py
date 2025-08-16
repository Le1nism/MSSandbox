#!/usr/bin/env python3
import os
import time
import random
import json
import requests
import threading
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Configuration
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8001))
CONSUMER_URL = os.getenv('CONSUMER_URL', 'http://consumer:8002')

# Store the last generated data
last_generated_data = None

# Automation control
automation_running = False
automation_thread = None
automation_interval = 5  # seconds between data generation

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

def automation_worker():
    """Background worker for automated data generation and sending"""
    global automation_running, last_generated_data
    
    while automation_running:
        try:
            # Generate new data
            data = generate_sensor_data()
            last_generated_data = data
            
            print(f"🤖 Automated: Generated data for sensor {data['sensor_id']}")
            
            # Send to consumer
            result = send_data_to_consumer(data)
            if result:
                print(f"✅ Automated: Data sent to consumer successfully")
            else:
                print(f"❌ Automated: Failed to send data to consumer")
            
            # Wait for next cycle
            time.sleep(automation_interval)
            
        except Exception as e:
            print(f"❌ Automation error: {e}")
            time.sleep(automation_interval)

def start_automation():
    """Start the automated data generation"""
    global automation_running, automation_thread
    
    if not automation_running:
        automation_running = True
        automation_thread = threading.Thread(target=automation_worker, daemon=True)
        automation_thread.start()
        print("🚀 Automation started")
        return True
    return False

def stop_automation():
    """Stop the automated data generation"""
    global automation_running
    
    if automation_running:
        automation_running = False
        print("🛑 Automation stopped")
        return True
    return False

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'service': 'Producer Service',
        'status': 'running',
        'port': SERVICE_PORT,
        'automation': {
            'running': automation_running,
            'interval': automation_interval
        },
        'endpoints': {
            'generate_data': '/generate-data',
            'send_data': '/send-data',
            'start_automation': '/start-automation',
            'stop_automation': '/stop-automation',
            'automation_status': '/automation-status',
            'status': '/status'
        }
    })

@app.route('/generate-data')
def generate_data():
    """Generate and return sensor data"""
    global last_generated_data
    last_generated_data = generate_sensor_data()
    return jsonify({
        'message': 'Data generated successfully',
        'data': last_generated_data
    })

@app.route('/send-data')
def send_data():
    """Send data to consumer (uses last generated data or generates new if none exists)"""
    global last_generated_data
    
    # If no data was previously generated, generate new data
    if last_generated_data is None:
        last_generated_data = generate_sensor_data()
        print("No previous data found, generating new data for sending")
    else:
        print(f"Using previously generated data with sensor ID: {last_generated_data['sensor_id']}")
    
    result = send_data_to_consumer(last_generated_data)
    
    if result:
        return jsonify({
            'message': 'Data sent to consumer successfully',
            'sent_data': last_generated_data,
            'consumer_response': result
        })
    else:
        return jsonify({
            'message': 'Failed to send data to consumer',
            'sent_data': last_generated_data,
            'error': 'Consumer service unavailable'
        }), 500

@app.route('/start-automation')
def start_auto():
    """Start automated data generation"""
    success = start_automation()
    return jsonify({
        'message': 'Automation started successfully' if success else 'Automation already running',
        'automation_running': automation_running
    })

@app.route('/stop-automation')
def stop_auto():
    """Stop automated data generation"""
    success = stop_automation()
    return jsonify({
        'message': 'Automation stopped successfully' if success else 'Automation not running',
        'automation_running': automation_running
    })

@app.route('/automation-status')
def automation_status():
    """Get automation status"""
    return jsonify({
        'automation_running': automation_running,
        'interval_seconds': automation_interval,
        'last_data_sensor_id': last_generated_data['sensor_id'] if last_generated_data else None
    })

@app.route('/status')
def status():
    """Service status"""
    return jsonify({
        'service': 'Producer Service',
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'consumer_url': CONSUMER_URL,
        'automation_running': automation_running,
        'last_data_sensor_id': last_generated_data['sensor_id'] if last_generated_data else None
    })

if __name__ == '__main__':
    print(f"PRODUCER SERVICE STARTED on port {SERVICE_PORT}")
    print(f"Consumer URL: {CONSUMER_URL}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
