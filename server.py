# server.py (不用動，確認內容即可)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_core import LoveAgent

app = FastAPI()
agent = LoveAgent()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

class ChatRequest(BaseModel):
  message: str

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
  print(f"收到前端訊息: {req.message}")
  response_text = agent.chat(req.message)
  return {"reply": response_text}

@app.post("/api/reset")
async def reset_endpoint():
  print("收到重置請求...")
  msg = agent.reset()
  return {"reply": msg}