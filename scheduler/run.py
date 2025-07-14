# To run this worker: celery -A scheduler.celery_app beat -l info
if __name__ == '__main__':
    print("To start the Scheduler, run the following command:")
    print("celery -A scheduler.celery_app beat -l info")