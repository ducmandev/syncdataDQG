# Phase 2 Detailed Development Plan: End-to-End Flow for "Phiếu Nhập"

**Objective:**  
Implement and successfully test a complete processing flow for "Phiếu Nhập" (Goods Receipt), covering detection in the database, processing, partner API integration, result updates, and logging.

---

## Task 2.1: Database Connection Management

- **Goal:**  
  Develop robust, reusable functions for connecting to SQL Server and MongoDB, with proper error handling.

- **Assignee:**  
  1 Developer

- **Instructions:**
  - **SQL Server:**
    - Edit [`app/db/mssql.py`](app/db/mssql.py).
    - Implement a connection string and a function to obtain a DB cursor, handling connection errors.
  - **MongoDB:**
    - Edit [`app/db/mongodb.py`](app/db/mongodb.py).
    - Implement connection management and a function to log data to MongoDB, with error handling.

---

## Task 2.2: Define Data Models for "Phiếu Nhập"

- **Goal:**  
  Create Pydantic models to validate the structure of `PhieuNhapHeader` and `PhieuNhapDetail` after reading from the database.

- **Assignee:**  
  1 Developer

- **Instructions:**
  - Create [`app/models/phieu_nhap.py`](app/models/phieu_nhap.py).
  - Define models mapping exactly to DB columns, supporting field aliasing for API payloads.

---

## Task 2.3: Implement Polling Service

- **Goal:**  
  Build a Celery periodic task to scan the database, fetch all required data, construct the full payload, and enqueue it for processing.

- **Assignee:**  
  1 Developer

- **Instructions:**
  - Create [`app/tasks/polling_service.py`](app/tasks/polling_service.py).
  - Implement logic to:
    - Periodically scan for pending "Phiếu Nhập".
    - Fetch headers and details in batch.
    - Build payloads and enqueue them for worker processing.

---

## Task 2.4: Build "Phiếu Nhập" Processing Worker

- **Goal:**  
  Develop a Celery worker that processes the payload: calls the partner API, updates results, and logs the process. The worker should not fetch data from the DB directly.

- **Assignee:**  
  1 Developer

- **Instructions:**
  - Create [`app/tasks/phieu_nhap_worker.py`](app/tasks/phieu_nhap_worker.py).
  - Implement logic to:
    - Receive the prepared payload.
    - Call the partner API.
    - Update the result in the database.
    - Log the process and handle errors/retries.

---

**Note:**  
Each task should include proper error handling, logging, and follow best practices for maintainability and scalability.