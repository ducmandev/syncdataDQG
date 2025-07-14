from scheduler.celery_app import app, TaskQueues
from common.database.mssql_client import mssql_client
from common.database.mongo_client import mongo_client

@app.task(name='scheduler.tasks.scan_and_dispatch')
def scan_and_dispatch():
    """
    Scans the MSSQL database for pending records and dispatches them
    to the appropriate worker queues.
    """
    # 1. Process Sales
    print("Scanning for pending sales...")
    pending_sales = mssql_client.fetch_pending_sales()
    for sale in pending_sales:
        local_invoice_id, shop_id = sale
        print(f"Dispatching sale task for invoice: {local_invoice_id}")
        task = app.send_task(
            'sale.process_sale', # Name of the task in the 'saler' worker
            args=[local_invoice_id, shop_id],
            queue=TaskQueues.SALE
        )
        mongo_client.log_task_dispatch(task.id, local_invoice_id, TaskQueues.SALE)

    # 2. Process Imports
    print("Scanning for pending imports...")
    pending_imports = mssql_client.fetch_pending_imports()
    for imp in pending_imports:
        local_receipt_id, shop_id = imp
        print(f"Dispatching import task for receipt: {local_receipt_id}")
        task = app.send_task(
            'import.process_import',
            args=[local_receipt_id, shop_id],
            queue=TaskQueues.IMPORT
        )
        mongo_client.log_task_dispatch(task.id, local_receipt_id, TaskQueues.IMPORT)

    # 3. Process Cancellations
    print("Scanning for pending cancellations...")
    pending_cancellations = mssql_client.fetch_pending_cancellations()
    for canc in pending_cancellations:
        local_slip_id, shop_id = canc
        print(f"Dispatching cancellation task for slip: {local_slip_id}")
        task = app.send_task(
            'cancellation.process_cancellation',
            args=[local_slip_id, shop_id],
            queue=TaskQueues.CANCELLATION
        )
        mongo_client.log_task_dispatch(task.id, local_slip_id, TaskQueues.CANCELLATION)

    print("Scan complete.")