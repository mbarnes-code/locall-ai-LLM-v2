from celery import Celery
import requests

app = Celery("tasks", broker="redis://redis:6379")

# Ollama AI Call (Worker LLM)
def run_worker_task(prompt):
    url = "http://localhost:11435/generate"  # Different LLM instance
    response = requests.post(url, json={"prompt": prompt})
    return response.json()["response"]

# Task: Work on AI-Generated Content
@app.task
def process_task(task_description):
    output = run_worker_task(task_description)
    return output
