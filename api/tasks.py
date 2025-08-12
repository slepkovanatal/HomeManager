import json
import os

import requests

from celery import Celery

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@app.task
def process_suitable_products_task(user_id):
    from agents.product_info_collector import ProductInfoCollector
    result = ProductInfoCollector().execute()

    webhook_url = "http://bot:8080/task-callback"  # Internal Docker URL

    response = requests.post(webhook_url, json={
        "chat_id": user_id,
        "result": result  # You might want to simplify/format this
    })

    return {"status": "done", "forwarded": response.status_code}
