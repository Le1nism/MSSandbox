# Microservices Learning Project

A simple Docker-based microservices project for learning microservices architecture with real data exchange.

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
   ```

### Testing the Services

Once the services are running, you can test them:

#### 1. Check Service Status
```bash
# Producer service
curl http://localhost:8001/status

# Consumer service
curl http://localhost:8002/status
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

Both services are on the same Docker network (`microservices-network`) and can communicate using service names:
- Producer service is accessible at `http://producer:8001` from within the Docker network
- Consumer service is accessible at `http://consumer:8002` from within the Docker network

### Local Access

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
- Ensure ports 8001 and 8002 are not already in use on your system
- Make sure Docker and Docker Compose are properly installed and running
- Check that both services can communicate by testing the endpoints