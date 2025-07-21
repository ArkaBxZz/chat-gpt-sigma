from fastapi import FastAPI, Request, HTTPException
from templates.model import chatbot_response
import json
from datetime import datetime
import os

# Load API key
with open("keys.json") as f:
    api_keys = json.load(f)["valid_keys"]

# Logging path
LOG_FILE = "chat_log.json"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump([], f)

def log_chat(api_key, message, response):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "api_key": api_key,
        "message": message,
        "response": response
    }
    with open(LOG_FILE, "r+") as f:
        data = json.load(f)
        data.append(entry)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

app = FastAPI()

@app.middleware("http")
async def check_api_key(request: Request, call_next):
    api_key = request.headers.get("X-API-Key")
    if api_key not in api_keys:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    request.state.api_key = api_key
    return await call_next(request)

@app.post("/chat")
async def chat(request: Request, payload: dict):
    message = payload.get("message", "")
    response = chatbot_response(message)
    log_chat(request.state.api_key, message, response)
    return {"response": response.strip()}