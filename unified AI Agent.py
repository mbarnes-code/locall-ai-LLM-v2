from fastapi import FastAPI, HTTPException
import chromadb
import requests
import uvicorn
import redis
from pydantic import BaseModel

app = FastAPI()

# Initialize Redis Client
try:
    redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Redis client: {e}")

# Initialize ChromaDB Client
try:
    chroma_client = chromadb.PersistentClient(path="/app/data/chroma")
except Exception as e:
    raise RuntimeError(f"Failed to initialize ChromaDB client: {e}")

# API Endpoints
OLLAMA_API_URL = "http://ollama:11434/generate"
CRAWL4AI_API_URL = "http://crawl4ai:5000/start"
UNSTRACT_API_URL = "http://unstract:8000/data"

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
def query_ai(request: QueryRequest):
    cache_key = f"query:{request.query}"
    cached_response = redis_client.get(cache_key)
    if cached_response:
        return {"response": cached_response}
    
    try:
        collection = chroma_client.get_collection(name="research_data")
        results = collection.query(query_texts=[request.query], n_results=5)
        context = "\n".join(results.get("documents", [[]])[0]) if results.get("documents") else ""
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ChromaDB query failed: {e}")
    
    payload = {"prompt": f"{context}\n\n{request.query}"}
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        final_response = response.json()
        redis_client.setex(cache_key, 3600, final_response.get("response", ""))
        return {"response": final_response.get("response", "")}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ollama query failed: {e}")

@app.post("/research")
def start_research(request: QueryRequest):
    try:
        response = requests.post(CRAWL4AI_API_URL, json={"query": request.query})
        response.raise_for_status()
        return {"message": "Research started", "task_id": response.json().get("task_id", "")}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Crawl4AI request failed: {e}")

@app.get("/etl-data")
def get_etl_data():
    try:
        response = requests.get(UNSTRACT_API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Unstract data fetch failed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
