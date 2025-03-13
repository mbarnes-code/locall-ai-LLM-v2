from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response
from loguru import logger
import chromadb
import requests
import uvicorn
import redis
from pydantic import BaseModel
import os

app = FastAPI()

# ✅ Setup structured logging
logger.add("logs/server.log", rotation="10 MB")

# ✅ Setup rate limiter (5 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)

# ✅ Prometheus metrics
api_requests_total = Counter("api_requests_total", "Total API requests")

# ✅ OAuth authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Store valid tokens (replace with a proper database or authentication provider)
VALID_TOKENS = {"super-secure-token"}  # Store real tokens securely!

def verify_token(token: str = Security(oauth2_scheme)):
    """Verifies OAuth token before processing API requests."""
    if token not in VALID_TOKENS:
        logger.warning(f"Unauthorized access attempt with token: {token}")
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return token

# ✅ Initialize Redis Client (with error handling)
try:
    redis_client = redis.Redis(host="redis", port=6379, db=0, decode_responses=True, socket_timeout=5)
    redis_client.ping()  # Check if Redis is reachable
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    redis_client = None  # Set to None to avoid crashes

# ✅ Initialize ChromaDB Client (with error handling)
try:
    chroma_client = chromadb.PersistentClient(path="/app/data/chroma")
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB client: {e}")
    chroma_client = None

# ✅ API Endpoints
OLLAMA_API_URL = "http://ollama:11434/generate"
CRAWL4AI_API_URL = "http://crawl4ai:5000/start"
UNSTRACT_API_URL = "http://unstract:8000/data"

# ✅ Request Model
class QueryRequest(BaseModel):
    query: str

# ✅ Health Check
@app.get("/health")
@limiter.limit("5/minute")  # Apply rate limiting
def health_check(request: Request):
    logger.info("Health check requested")
    api_requests_total.inc()  # Increment API request counter
    return {"status": "running"}

# ✅ Prometheus Metrics Endpoint
@app.get("/metrics")
def get_metrics():
    return Response(generate_latest(), media_type="text/plain")

# ✅ Query AI with OAuth & Caching
@app.post("/query")
@limiter.limit("5/minute")
def query_ai(request: QueryRequest, token: str = Depends(verify_token)):
    logger.info(f"Received AI query: {request.query}")
    cache_key = f"query:{request.query}"

    # Retrieve from cache if available
    if redis_client:
        cached_response = redis_client.get(cache_key)
        if cached_response:
            logger.info("Cache hit: Returning cached response")
            return {"response": cached_response}

    # Query ChromaDB
    context = ""
    if chroma_client:
        try:
            collection = chroma_client.get_collection(name="research_data")
            results = collection.query(query_texts=[request.query], n_results=5)
            context = "\n".join(results.get("documents", [[]])[0]) if results.get("documents") else ""
        except Exception as e:
            logger.error(f"ChromaDB query failed: {e}")
            raise HTTPException(status_code=500, detail=f"ChromaDB query failed: {e}")

    # Call Ollama API
    payload = {"prompt": f"{context}\n\n{request.query}"}
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        final_response = response.json()
        
        # Store response in cache (TTL: 1 hour)
        if redis_client:
            redis_client.setex(cache_key, 3600, final_response.get("response", ""))

        return {"response": final_response.get("response", "")}
    except requests.RequestException as e:
        logger.error(f"Ollama query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama query failed: {e}")

# ✅ Start Research Task
@app.post("/research")
@limiter.limit("5/minute")
def start_research(request: QueryRequest, token: str = Depends(verify_token)):
    logger.info(f"Starting research for query: {request.query}")
    try:
        response = requests.post(CRAWL4AI_API_URL, json={"query": request.query})
        response.raise_for_status()
        return {"message": "Research started", "task_id": response.json().get("task_id", "")}
    except requests.RequestException as e:
        logger.error(f"Crawl4AI request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Crawl4AI request failed: {e}")

# ✅ Fetch ETL Data
@app.get("/etl-data")
@limiter.limit("5/minute")
def get_etl_data(token: str = Depends(verify_token)):
    logger.info("Fetching ETL data")
    try:
        response = requests.get(UNSTRACT_API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Unstract data fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Unstract data fetch failed: {e}")

# ✅ Run API Server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
