#!/usr/bin/env python3
import os
import time
import random
import json
import requests
import threading
from flask import Flask, jsonify, request
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

# Benchmark state
benchmark_running = False
benchmark_thread = None
benchmark_config = {
    'duration_seconds': 0,
    'payload_bytes': 0,
    'workers': 1
}
benchmark_stats = {
    'started_at': None,
    'ended_at': None,
    'attempted': 0,
    'succeeded': 0,
    'failed': 0,
    'bytes_sent': 0
}

def _approximate_payload_of_size(base_data, target_bytes):
    """Return a data dict whose JSON body is roughly target_bytes in size."""
    try:
        baseline = json.dumps(base_data)
        baseline_len = len(baseline.encode('utf-8'))
        extra_needed = max(0, target_bytes - baseline_len)
        if extra_needed > 0:
            base_data['padding'] = 'x' * extra_needed
        return base_data
    except Exception:
        return base_data

def _benchmark_worker(end_time):
    global benchmark_stats, benchmark_running
    session = requests.Session()
    while benchmark_running and time.time() < end_time:
        try:
            data = generate_sensor_data()
            # Apply payload size padding if configured
            target = max(0, int(benchmark_config.get('payload_bytes', 0)))
            if target > 0:
                data = _approximate_payload_of_size(data, target)
            payload = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            benchmark_stats['attempted'] += 1
            resp = session.post(f"{CONSUMER_URL}/process-data", data=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                benchmark_stats['succeeded'] += 1
                benchmark_stats['bytes_sent'] += len(payload.encode('utf-8'))
            else:
                benchmark_stats['failed'] += 1
        except Exception:
            benchmark_stats['failed'] += 1
            # small backoff to avoid tight error loops
            time.sleep(0.001)

def _reset_benchmark_stats():
    global benchmark_stats
    benchmark_stats = {
        'started_at': datetime.now().isoformat(),
        'ended_at': None,
        'attempted': 0,
        'succeeded': 0,
        'failed': 0,
        'bytes_sent': 0
    }

def start_benchmark(duration_seconds: int, payload_bytes: int, workers: int):
    global benchmark_running, benchmark_thread, benchmark_config
    if benchmark_running:
        return False
    benchmark_config = {
        'duration_seconds': max(1, int(duration_seconds)),
        'payload_bytes': max(0, int(payload_bytes)),
        'workers': max(1, int(workers))
    }
    _reset_benchmark_stats()
    benchmark_running = True
    end_time = time.time() + benchmark_config['duration_seconds']
    # Launch worker threads
    threads = []
    for _ in range(benchmark_config['workers']):
        t = threading.Thread(target=_benchmark_worker, args=(end_time,), daemon=True)
        t.start()
        threads.append(t)

    def joiner():
        global benchmark_running
        for t in threads:
            t.join()
        benchmark_running = False
        benchmark_stats['ended_at'] = datetime.now().isoformat()

    benchmark_thread = threading.Thread(target=joiner, daemon=True)
    benchmark_thread.start()
    return True

def stop_benchmark():
    global benchmark_running
    benchmark_running = False
    return True

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
        'last_data_sensor_id': last_generated_data['sensor_id'] if last_generated_data else None,
        'benchmark_running': benchmark_running
    })

# Benchmark endpoints
@app.route('/benchmark/start', methods=['POST'])
def benchmark_start():
    try:
        payload = request.get_json(force=True) if request.data else {}
        duration = int(payload.get('duration_seconds', 10))
        size_bytes = int(payload.get('payload_bytes', 0))
        workers = int(payload.get('workers', 1))
        started = start_benchmark(duration, size_bytes, workers)
        return jsonify({
            'started': started,
            'running': benchmark_running,
            'config': benchmark_config,
            'stats': benchmark_stats
        }), (200 if started else 409)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/benchmark/stop')
def benchmark_stop():
    stop_benchmark()
    return jsonify({
        'running': benchmark_running,
        'stats': benchmark_stats
    })

@app.route('/benchmark/status')
def benchmark_status():
    # add elapsed seconds and throughput estimates
    elapsed = None
    try:
        if benchmark_stats['started_at']:
            start_dt = datetime.fromisoformat(benchmark_stats['started_at'])
            end_dt = datetime.now() if benchmark_stats['ended_at'] is None else datetime.fromisoformat(benchmark_stats['ended_at'])
            elapsed = max(0.0, (end_dt - start_dt).total_seconds())
    except Exception:
        elapsed = None
    rps = (benchmark_stats['succeeded'] / elapsed) if elapsed and elapsed > 0 else None
    bps = (benchmark_stats['bytes_sent'] / elapsed) if elapsed and elapsed > 0 else None
    return jsonify({
        'running': benchmark_running,
        'config': benchmark_config,
        'stats': benchmark_stats,
        'elapsed_seconds': elapsed,
        'throughput': {
            'requests_per_second': rps,
            'bytes_per_second': bps
        }
    })

if __name__ == '__main__':
    print(f"PRODUCER SERVICE STARTED on port {SERVICE_PORT}")
    print(f"Consumer URL: {CONSUMER_URL}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
