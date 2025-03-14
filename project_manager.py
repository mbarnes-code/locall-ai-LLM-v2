from celery import Celery
import requests

app = Celery("tasks", broker="redis://redis:6379")

# Ollama AI Call (Project Manager)
def ask_llm(prompt):
    url = "http://localhost:11434/generate"
    response = requests.post(url, json={"prompt": prompt})
    return response.json()["response"]

# Task: Ask user clarifying project questions
@app.task
def define_project(user_input):
    prompt = f"You are a Project Manager AI. Clarify the project with the user: {user_input}"
    questions = ask_llm(prompt)
    return questions

# Task: Assign work to Worker LLM
@app.task
def assign_task(task_description):
    prompt = f"You are a Project Manager AI. Delegate this task: {task_description}"
    worker_response = ask_llm(prompt)
    return worker_response

@app.task
def generate_daily_report():
    prompt = "Summarize today's completed tasks and progress updates."
    report = ask_llm(prompt)
    return report
