# Project Hermes

## Overview

Project Hermes is a distributed data integration and synchronization system designed to automate the collection, transformation, and forwarding of business documents (invoices, import/export slips) between internal databases and external partner APIs. The system is built with Python, Celery, and Docker, leveraging Redis for task brokering and MongoDB/SQL Server for data storage.

### Architecture

- **Celery-based Microservices:** Each business document type (import slip, export slip, invoice) is handled by a dedicated Celery worker, each listening to its own queue.
- **API Client Abstraction:** All outbound API calls to partners are centralized in a single [`PartnerAPIClient`](app/clients/partner_api_client.py:15) class for maintainability and reuse.
- **Database Layer:** Supports both MongoDB and Microsoft SQL Server for flexible data storage and retrieval.
- **Configuration:** All environment-specific settings are managed via `.env` and Pydantic-based config classes.
- **Containerized Deployment:** All services are orchestrated via Docker Compose for easy local development and deployment.

## Required Environment Variables

Set these variables in your `.env` file at the project root:

- **Redis**
  - `REDIS_HOST`
  - `REDIS_PORT`
- **MongoDB**
  - `MONGO_URI`
  - `MONGO_DB_NAME`
- **Microsoft SQL Server**
  - `MSSQL_SERVER`
  - `MSSQL_DATABASE`
  - `MSSQL_USER`
  - `MSSQL_PASSWORD`
  - `MSSQL_DRIVER` (default: `{ODBC Driver 17 for SQL Server}`)
- **Partner API**
  - `API_BASE_URL`
  - `API_USERNAME`
  - `API_PASSWORD`

See [`app/core/config.py`](app/core/config.py:8) for details.

## Setup & Configuration

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd project-hermes
   ```

2. **Create and configure `.env`:**
   - Copy `.env.example` (if available) or create `.env` manually with all required variables.

3. **Install Docker and Docker Compose** (if not already installed).

4. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

   This will build and start:
   - Celery scheduler (beat)
   - `phieu_nhap_worker` (import slip worker)
   - `phieu_xuat_worker` (export slip worker)
   - `hoa_don_worker` (invoice worker)

5. **Install Python dependencies (for local development outside Docker):**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Project Locally

The recommended way is via Docker Compose:

```bash
docker-compose up --build
```

All services will be started and orchestrated automatically.

## Service Workers & Celery Queues

| Worker Service         | Celery Queue        | Description                        | Source File                                 |
|------------------------|--------------------|------------------------------------|---------------------------------------------|
| phieu_nhap_worker      | phieu_nhap_queue   | Handles import slip processing     | [`app/tasks/phieu_nhap_worker.py`](app/tasks/phieu_nhap_worker.py:1) |
| phieu_xuat_worker      | phieu_xuat_queue   | Handles export slip processing     | [`app/tasks/phieu_xuat_worker.py`](app/tasks/phieu_xuat_worker.py:1) |
| hoa_don_worker         | hoa_don_queue      | Handles invoice processing         | [`app/tasks/hoa_don_worker.py`](app/tasks/hoa_don_worker.py:1)       |
| scheduler (beat)       | -                  | Triggers periodic tasks            | -                                           |

Each worker uses the centralized [`PartnerAPIClient`](app/clients/partner_api_client.py:15) for outbound API calls.

## Additional Handover Notes

- **Configuration Management:** All settings are loaded via Pydantic classes in [`app/core/config.py`](app/core/config.py:8) and [`config/celery_config.py`](config/celery_config.py:3).
- **Extensibility:** To add new document types, create a new worker in `app/tasks/`, define its Celery queue in `docker-compose.yml`, and add corresponding models and API client methods.
- **Database Connections:** Connection details for Redis, MongoDB, and SQL Server must be valid and reachable from within Docker containers.
- **Logs & Monitoring:** All workers log to stdout. Use `docker-compose logs -f` for real-time monitoring.

## References

- [Detailed Phase 4 Plan](PLAN/phase_4_detailed_plan.md)
- [Full Project Plan](PLAN/plan_chi_tiet.md)
- [Celery Configuration](config/celery_config.py)
- [API Client](app/clients/partner_api_client.py)
