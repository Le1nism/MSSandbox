# Microservices Sandbox

A simple Docker-based microservices project for learning microservices architecture with data exchange, performance monitoring and a modern web interface.

## Project Structure

```
MSSandbox/
├── docker-compose.yml
├── producer/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── consumer/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── webui/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── templates/
│       └── index.html
└── README.md
```

## Services

- **Producer Service**: Generates sensor data and sends it to consumer
  - Port: 8001
  - Container name: producer-service
  - Endpoints:
    - `/` - Service info
    - `/generate-data` - Generate sensor data
    - `/send-data` - Generate and send data to consumer
    - `/status` - Service status

- **Consumer Service**: Receives and processes sensor data from producer
  - Port: 8002
  - Container name: consumer-service
  - Endpoints:
    - `/` - Service info
    - `/process-data` - Process incoming data (POST)
    - `/get-processed-data` - Get data from producer and process it
    - `/status` - Service status

- **Web UI Service**: Modern web interface for interacting with microservices
  - Port: 8000
  - Container name: webui-service
  - Features:
    - Real-time service health monitoring
    - Interactive data flow visualization
    - One-click data generation and processing
    - JSON result display
    - Manual data input capabilities

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the Services

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode (background):**
   ```bash
   docker-compose up -d --build
   ```

3. **Stop all services:**
   ```bash
   docker-compose down
   ```

4. **View logs:**
   ```bash
   # All services
   docker-compose logs
   
   # Specific service
   docker-compose logs producer
   docker-compose logs consumer
   docker-compose logs webui
   ```

### Using the Web Interface

Once all services are running, open your browser and navigate to:

**🌐 Web Dashboard: http://localhost:8000**

The web interface provides:

- **Service Health Monitoring**: Real-time status of Producer and Consumer services
- **Interactive Controls**: Buttons to trigger different microservices operations
- **Data Flow Visualization**: Clear diagram showing how data flows between services
- **Results Display**: Formatted JSON output showing the data exchange
- **Manual Data Processing**: Ability to send custom data for processing

### Web UI Features

1. **Generate Data**: Create new sensor data from the Producer service
2. **Send to Consumer**: Producer automatically sends data to Consumer for processing
3. **Get Processed Data**: Consumer fetches data from Producer and processes it
4. **Manual Processing**: Send custom data directly to Consumer for processing

### Testing the Services (Command Line)

You can also test the services directly via command line:

#### 1. Check Service Status
```bash
# Producer service
curl http://localhost:8001/status

# Consumer service
curl http://localhost:8002/status

# Web UI service
curl http://localhost:8000/api/status
```

#### 2. Generate Sensor Data
```bash
# Generate data from producer
curl http://localhost:8001/generate-data
```

#### 3. Send Data from Producer to Consumer
```bash
# Producer sends data to consumer
curl http://localhost:8001/send-data
```

#### 4. Consumer Gets and Processes Data
```bash
# Consumer fetches data from producer and processes it
curl http://localhost:8002/get-processed-data
```

#### 5. Direct Data Processing
```bash
# Send data directly to consumer for processing
curl -X POST http://localhost:8002/process-data \
  -H "Content-Type: application/json" \
  -d '{"temperature": 22.5, "humidity": 65.0, "pressure": 1012.5, "sensor_id": "TEST_SENSOR"}'
```

### Network Communication

All services are on the same Docker network (`microservices-network`) and can communicate using service names:
- Producer service is accessible at `http://producer:8001` from within the Docker network
- Consumer service is accessible at `http://consumer:8002` from within the Docker network
- Web UI service is accessible at `http://webui:8000` from within the Docker network

### Local Access

- **Web Dashboard**: `http://localhost:8000`
- Producer service: `http://localhost:8001`
- Consumer service: `http://localhost:8002`

## Data Flow

1. **Producer generates sensor data** (temperature, humidity, pressure, sensor ID)
2. **Producer sends data to consumer** via HTTP POST
3. **Consumer processes the data** and adds analysis:
   - Temperature status (COLD/COMFORTABLE/WARM)
   - Humidity status (DRY/NORMAL/HUMID)
   - Pressure trend (STABLE/VARIABLE)
   - Data quality score
4. **Consumer returns processed data** to producer

## Example Data

### Generated Sensor Data (Producer)
```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "temperature": 22.5,
  "humidity": 65.0,
  "pressure": 1012.5,
  "sensor_id": "SENSOR_1234"
}
```

### Processed Data (Consumer)
```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "temperature": 22.5,
  "humidity": 65.0,
  "pressure": 1012.5,
  "sensor_id": "SENSOR_1234",
  "processed_at": "2024-01-15T10:30:01.234567",
  "temperature_status": "COMFORTABLE",
  "humidity_status": "NORMAL",
  "pressure_trend": "STABLE",
  "data_quality_score": 95.5
}
```

## Troubleshooting

- If containers fail to start, check the logs: `docker-compose logs`
- Ensure ports 8000, 8001, and 8002 are not already in use on your system
- Make sure Docker and Docker Compose are properly installed and running
- Check that all services can communicate by testing the endpoints
- If the web UI doesn't load, check that all services are healthy in the status bar