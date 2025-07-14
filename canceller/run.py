# To run this worker: celery -A canceller.celery_app worker -l info -Q cancellation_queue
if __name__ == '__main__':
    print("To start the Cancellation Worker, run the following command:")
    print("celery -A canceller.celery_app worker -l info -Q cancellation_queue")