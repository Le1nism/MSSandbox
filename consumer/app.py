#!/usr/bin/env python3
import os
import json
import requests
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Configuration
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8002))
PRODUCER_URL = os.getenv('PRODUCER_URL', 'http://producer:8001')

# Store the last received data
last_received_data = None

# Store all processed data for viewing
processed_data_history = []
max_history_size = 100  # Keep last 100 entries

def process_sensor_data(data):
    """Process sensor data and add analysis"""
    processed_data = data.copy()
    
    # Add processing timestamp
    processed_data['processed_at'] = datetime.now().isoformat()
    
    # Analyze temperature
    temp = data.get('temperature', 0)
    if temp < 20:
        processed_data['temperature_status'] = 'COLD'
    elif temp > 23:
        processed_data['temperature_status'] = 'WARM'
    else:
        processed_data['temperature_status'] = 'COMFORTABLE'
    
    # Analyze humidity
    humidity = data.get('humidity', 0)
    if humidity < 50:
        processed_data['humidity_status'] = 'DRY'
    elif humidity > 70:
        processed_data['humidity_status'] = 'HUMID'
    else:
        processed_data['humidity_status'] = 'NORMAL'
    
    # Calculate pressure trend (mock calculation)
    pressure = data.get('pressure', 0)
    processed_data['pressure_trend'] = 'STABLE' if 1010 <= pressure <= 1015 else 'VARIABLE'
    
    # Add data quality score
    processed_data['data_quality_score'] = 95.5
    
    return processed_data

def add_to_history(processed_data):
    """Add processed data to history"""
    global processed_data_history
    
    # Add to history
    processed_data_history.append(processed_data)
    
    # Keep only the last max_history_size entries
    if len(processed_data_history) > max_history_size:
        processed_data_history = processed_data_history[-max_history_size:]
    
    print(f"📊 Added to history: {processed_data.get('sensor_id', 'UNKNOWN')} - Total entries: {len(processed_data_history)}")

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'service': 'Consumer Service',
        'status': 'running',
        'port': SERVICE_PORT,
        'endpoints': {
            'process_data': '/process-data',
            'get_processed_data': '/get-processed-data',
            'view_all_data': '/view-all-data',
            'clear_history': '/clear-history',
            'status': '/status'
        }
    })

@app.route('/process-data', methods=['POST'])
def process_data():
    """Process incoming sensor data"""
    global last_received_data
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Store the received data
        last_received_data = data.copy()
        
        # Process the data
        processed_data = process_sensor_data(data)
        
        # Add to history
        add_to_history(processed_data)
        
        print(f"Processed data from sensor: {data.get('sensor_id', 'UNKNOWN')}")
        
        return jsonify({
            'message': 'Data processed successfully',
            'original_data': data,
            'processed_data': processed_data,
            'processing_timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error processing data: {str(e)}'
        }), 500

@app.route('/get-processed-data')
def get_processed_data():
    """Get data from producer and process it (or use last received data if available)"""
    global last_received_data
    
    try:
        # If we have previously received data, use that instead of fetching new data
        if last_received_data is not None:
            print(f"Using previously received data with sensor ID: {last_received_data.get('sensor_id', 'UNKNOWN')}")
            sensor_data = last_received_data
        else:
            # Get fresh data from producer
            print("No previous data available, fetching new data from producer")
            response = requests.get(f"{PRODUCER_URL}/generate-data", timeout=5)
            
            if response.status_code == 200:
                producer_data = response.json()
                sensor_data = producer_data.get('data', {})
                # Store the new data
                last_received_data = sensor_data.copy()
            else:
                return jsonify({
                    'error': 'Failed to get data from producer'
                }), 500
        
        # Process the data
        processed_data = process_sensor_data(sensor_data)
        
        # Add to history
        add_to_history(processed_data)
        
        return jsonify({
            'message': 'Data retrieved and processed successfully',
            'producer_data': sensor_data,
            'processed_data': processed_data,
            'timestamp': datetime.now().isoformat(),
            'data_source': 'cached' if last_received_data is not None else 'fresh'
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Error connecting to producer: {str(e)}'
        }), 500

@app.route('/view-all-data')
def view_all_data():
    """View all processed data in a formatted way"""
    return jsonify({
        'message': f'Retrieved {len(processed_data_history)} processed data entries',
        'total_entries': len(processed_data_history),
        'data': processed_data_history,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/clear-history')
def clear_history():
    """Clear the data history"""
    global processed_data_history
    count = len(processed_data_history)
    processed_data_history = []
    return jsonify({
        'message': f'Cleared {count} entries from history',
        'total_entries': 0
    })

@app.route('/status')
def status():
    """Service status"""
    return jsonify({
        'service': 'Consumer Service',
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'producer_url': PRODUCER_URL,
        'last_data_sensor_id': last_received_data.get('sensor_id') if last_received_data else None,
        'history_entries': len(processed_data_history),
        'max_history_size': max_history_size
    })

if __name__ == '__main__':
    print(f"CONSUMER SERVICE STARTED on port {SERVICE_PORT}")
    print(f"Producer URL: {PRODUCER_URL}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
