# To run this worker: celery -A saler.celery_app worker -l info -Q sale_queue
if __name__ == '__main__':
    print("To start the Sale Worker, run the following command:")
    print("celery -A saler.celery_app worker -l info -Q sale_queue")