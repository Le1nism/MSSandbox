# Microservices Learning Project

A simple Docker-based microservices project for learning microservices architecture.

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

- **Producer Service**: Will generate or serve data (placeholder for now)
  - Port: 8001
  - Container name: producer-service

- **Consumer Service**: Will retrieve and display data from producer (placeholder for now)
  - Port: 8002
  - Container name: consumer-service

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

### Network Communication

Both services are on the same Docker network (`microservices-network`) and can communicate using service names:
- Producer service is accessible at `http://producer:8001` from within the Docker network
- Consumer service is accessible at `http://consumer:8002` from within the Docker network

### Local Access

- Producer service: `http://localhost:8001`
- Consumer service: `http://localhost:8002`

