# To run this worker: celery -A importer.celery_app worker -l info -Q import_queue
if __name__ == '__main__':
    print("To start the Import Worker, run the following command:")
    print("celery -A importer.celery_app worker -l info -Q import_queue")