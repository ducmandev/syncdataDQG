# run_verification.py
import time
from src.tasks.process_records import add

if __name__ == "__main__":
    # Send a test task to Celery
    result = add.delay(5, 5)
    print(f"Task sent with ID: {result.id}")
    # Wait for the result (timeout after 10 seconds)
    try:
        final_result = result.get(timeout=10)
        print(f"Result received: {final_result}")
    except Exception as e:
        print(f"Failed to get result: {e}")