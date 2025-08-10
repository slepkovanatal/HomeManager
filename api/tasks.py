import json
import requests

from celery import Celery

app = Celery("tasks", broker="redis://redis:6379/0", backend="redis://redis:6379/0")

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
