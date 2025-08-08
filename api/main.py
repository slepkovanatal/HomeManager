from fastapi import FastAPI, BackgroundTasks
from celery.result import AsyncResult
from pydantic import BaseModel

from tasks import process_suitable_products_task

app = FastAPI()

class ProcessRequest(BaseModel):
    user_id: int

@app.post("/process-products/")
def process_products(req: ProcessRequest):
    task = process_suitable_products_task.delay(req.user_id)
    return {"task_id": task.id}

@app.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    result = AsyncResult(task_id)
    if result.ready():
        return {"status": "done", "result": result.result}
    return {"status": "pending"}