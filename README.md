# Catalogue Service

gRPC-based microservice for managing auction item catalogues with search and item creation capabilities.

## Quick Start

### 1. Setup Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration (database credentials, etc.)

### 2. Running with CLI

**Install dependencies:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Generate gRPC stubs:**
```bash
./generate_grpc.sh
```

**Run the service:**
```bash
python -m app.grpc.server
```

Service will start on `localhost:50051`

### 3. Running with Docker

```bash
docker compose up
```

This starts both the catalogue service and PostgreSQL database.

Service will be available on `localhost:50052`

## Features

- **GetAllItems** - Retrieve all auction items with real-time remaining time
- **SearchItems** - Search items by keyword in title
- **CreateItem** - Create new auction items with validation

## Tech Stack

- gRPC / Protocol Buffers
- SQLAlchemy (PostgreSQL)
- FastAPI for REST endpoints
- Pydantic for data validation