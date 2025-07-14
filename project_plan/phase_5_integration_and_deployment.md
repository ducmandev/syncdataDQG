### **Phase 5: Integration, Testing, and Deployment**
### **Giai đoạn 5: Tích hợp, Kiểm thử và Triển khai**

**Objective:** To ensure all individual services work together as a cohesive system, to validate the system's correctness through testing, and to prepare the application for a production-like environment using Docker.
**Mục tiêu:** Đảm bảo tất cả các dịch vụ riêng lẻ hoạt động cùng nhau như một hệ thống gắn kết, xác thực tính đúng đắn của hệ thống thông qua kiểm thử và chuẩn bị ứng dụng cho một môi trường giống như sản xuất bằng Docker.

---

#### **Task 5.1: Create `run.py` Scripts for Each Service**

*   **Description:** Create simple entry-point scripts to easily start each service's Celery worker or the Beat scheduler from the command line.
*   **Files to Create:** `scheduler/run.py`, `saler/run.py`, `importer/run.py`, `canceller/run.py`
*   **Code (Example for `saler/run.py`):**
    ```python
    # To run this worker: celery -A saler.celery_app worker --loglevel=info
    from saler.celery_app import app

    if __name__ == '__main__':
        # This allows running the worker directly for development,
        # but the `celery` command is preferred.
        # Example: celery -A saler.celery_app worker -l info -Q sale_queue
        print("To start the Sale Worker, run the following command:")
        print("celery -A saler.celery_app worker -l info -Q sale_queue")

    ```
    *   *(The other `run.py` files will be similar, pointing to their respective Celery apps. The scheduler's run command will use `beat` instead of `worker`.)*
*   **Output:** Executable scripts that provide clear instructions for starting each service.

---

#### **Task 5.2: Create `docker-compose.yml` for Local Development**

*   **Description:** Create a Docker Compose file to orchestrate all the services (Redis, MongoDB, and our four Python applications) for easy local setup and testing.
*   **File to Create:** `docker-compose.yml`
*   **Code (`docker-compose.yml`):**
    ```yaml
    version: '3.8'

    services:
      redis:
        image: redis:7-alpine
        ports:
          - "6379:6379"

      mongo:
        image: mongo:7
        ports:
          - "27017:27017"
        environment:
          - MONGO_INITDB_DATABASE=${MONGO_DB_NAME:-sync_data_logs}

      scheduler:
        build:
          context: .
          dockerfile: scheduler/Dockerfile
        command: celery -A scheduler.celery_app beat -l info
        depends_on:
          - redis
        volumes:
          - .:/app
        env_file: .env

      saler:
        build:
          context: .
          dockerfile: saler/Dockerfile
        command: celery -A saler.celery_app worker -l info -Q sale_queue
        depends_on:
          - redis
          - mongo
        volumes:
          - .:/app
        env_file: .env

      importer:
        build:
          context: .
          dockerfile: importer/Dockerfile
        command: celery -A importer.celery_app worker -l info -Q import_queue
        depends_on:
          - redis
          - mongo
        volumes:
          - .:/app
        env_file: .env

      canceller:
        build:
          context: .
          dockerfile: canceller/Dockerfile
        command: celery -A canceller.celery_app worker -l info -Q cancellation_queue
        depends_on:
          - redis
          - mongo
        volumes:
          - .:/app
        env_file: .env

    volumes:
      redis-data:
      mongo-data:
    ```
*   **Input:** Requires `Dockerfile` for each service (Task 5.3).
*   **Output:** A single command (`docker-compose up`) can start the entire application stack.

---

#### **Task 5.3: Create `Dockerfile` for Each Service**

*   **Description:** Create a `Dockerfile` for each of the four Python services to containerize them.
*   **Files to Create:** `scheduler/Dockerfile`, `saler/Dockerfile`, `importer/Dockerfile`, `canceller/Dockerfile`
*   **Code (Example for `saler/Dockerfile`):**
    ```dockerfile
    FROM python:3.10-slim

    WORKDIR /app

    # Copy only requirements to leverage Docker cache
    COPY requirements.txt requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the entire project context
    COPY . .

    # The command to run the service will be provided by docker-compose.yml
    ```
*   **Output:** Container images for each service, ready to be used by Docker Compose.

---

#### **Task 5.4: Write Unit and Integration Tests**

*   **Description:** Create a `tests/` directory and write tests to validate the functionality of the `common` library and the end-to-end flow of each worker.
*   **Files to Create:** `tests/test_api_client.py`, `tests/test_sale_pipeline.py`, etc.
*   **Example Test (`tests/test_api_client.py`):**
    ```python
    import pytest
    from unittest.mock import MagicMock, patch
    from common.services.api_client import ApiClient

    @patch('common.services.api_client.httpx.Client')
    def test_login_success(mock_client):
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "fake_token", "token_type": "bearer"}
        mock_client.return_value.post.return_value = mock_response

        api_client = ApiClient()

        # Act
        token = api_client._login("test_shop")

        # Assert
        assert token == "fake_token"
    ```
*   **Output:** A suite of tests that can be run to ensure the application is working correctly.