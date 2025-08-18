#!/usr/bin/env python3
import os
import json
import requests
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Configuration
SERVICE_PORT = int(os.getenv('SERVICE_PORT', 8000))
PRODUCER_URL = os.getenv('PRODUCER_URL', 'http://producer:8001')
CONSUMER_URL = os.getenv('CONSUMER_URL', 'http://consumer:8002')

# Benchmark log file (JSON Lines) inside the container filesystem
BENCHMARK_LOG_PATH = os.getenv('BENCHMARK_LOG_PATH', str(Path(__file__).parent / 'benchmark_results.jsonl'))

# Ensure the log directory exists at startup (works both in Docker and local runs)
try:
    Path(BENCHMARK_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Failed to ensure benchmark log directory exists: {e}")

def append_benchmark_log(record: dict):
    try:
        Path(BENCHMARK_LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
        with open(BENCHMARK_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')
    except Exception as e:
        # Non-fatal; surface in API responses when appropriate
        print(f"Failed to write benchmark log: {e}")

def check_service_health(service_name, url):
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{url}/status", timeout=3)
        return response.status_code == 200
    except:
        return False

@app.route('/')
def home():
    """Redirect to the Automation page by default"""
    return redirect(url_for('automation_page'))

@app.route('/automation')
def automation_page():
    return render_template('automation.html')

@app.route('/benchmark')
def benchmark_page():
    return render_template('benchmark.html')

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

# -----------------------------
# Benchmark orchestration APIs
# -----------------------------

@app.route('/api/benchmark/start', methods=['POST'])
def api_benchmark_start():
    """Enable consumer counters and start producer benchmark."""
    try:
        payload = request.get_json(force=True)
        duration = int(payload.get('duration_seconds', 15))
        payload_bytes = int(payload.get('payload_bytes', 512))
        workers = int(payload.get('workers', 4))

        # Enable consumer tracking
        try:
            requests.get(f"{CONSUMER_URL}/benchmark/enable", timeout=5)
        except requests.exceptions.RequestException:
            pass

        # Start producer benchmark
        resp = requests.post(
            f"{PRODUCER_URL}/benchmark/start",
            json={
                'duration_seconds': duration,
                'payload_bytes': payload_bytes,
                'workers': workers
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': f'Failed to start benchmark: {str(e)}'}), 400

@app.route('/api/benchmark/status')
def api_benchmark_status():
    """Return combined status from producer and consumer."""
    try:
        prod = requests.get(f"{PRODUCER_URL}/benchmark/status", timeout=5)
        cons = requests.get(f"{CONSUMER_URL}/benchmark/stats", timeout=5)
        return jsonify({
            'producer': prod.json() if prod.ok else {'error': 'producer status error'},
            'consumer': cons.json() if cons.ok else {'error': 'consumer status error'},
            'timestamp': datetime.now().isoformat()
        })
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error querying benchmark status: {str(e)}'}), 500

@app.route('/api/benchmark/stop', methods=['POST'])
def api_benchmark_stop():
    """Stop the producer benchmark and disable consumer tracking; log results."""
    try:
        prod = requests.get(f"{PRODUCER_URL}/benchmark/stop", timeout=5)
        cons_disable = requests.get(f"{CONSUMER_URL}/benchmark/disable", timeout=5)
        # Fetch final stats
        prod_status = requests.get(f"{PRODUCER_URL}/benchmark/status", timeout=5)
        cons_stats = requests.get(f"{CONSUMER_URL}/benchmark/stats", timeout=5)
        result = {
            'producer': prod_status.json() if prod_status.ok else {'error': 'producer status error'},
            'consumer': cons_stats.json() if cons_stats.ok else {'error': 'consumer stats error'},
            'timestamp': datetime.now().isoformat()
        }
        # Persist log entry
        append_benchmark_log(result)
        return jsonify(result)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error stopping benchmark: {str(e)}'}), 500

@app.route('/api/benchmark/logs')
def api_benchmark_logs():
    """Return last N benchmark log lines (default 10)."""
    try:
        n = int(request.args.get('n', 10))
        if not Path(BENCHMARK_LOG_PATH).exists():
            return jsonify({'logs': [], 'path': BENCHMARK_LOG_PATH})
        with open(BENCHMARK_LOG_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        tail = lines[-n:]
        # Parse JSONL
        logs = []
        for line in tail:
            try:
                logs.append(json.loads(line))
            except Exception:
                continue
        return jsonify({'logs': logs, 'path': BENCHMARK_LOG_PATH})
    except Exception as e:
        return jsonify({'error': f'Error reading logs: {str(e)}'}), 500

if __name__ == '__main__':
    print(f"WEB UI STARTED on port {SERVICE_PORT}")
    print(f"Producer URL: {PRODUCER_URL}")
    print(f"Consumer URL: {CONSUMER_URL}")
    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
