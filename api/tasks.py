import json

from celery import Celery

app = Celery("tasks", broker="redis://redis:6379/0", backend="redis://redis:6379/0")

@app.task
def process_suitable_products_task(user_id):
    from agents.product_info_collector import ProductInfoCollector
    result = ProductInfoCollector().execute()
    return json.dumps(result)