# 引入必要的零件
from fastapi import FastAPI               # 這是蓋房子的基礎：Web 伺服器框架
from fastapi.middleware.cors import CORSMiddleware # 處理「跨域問題」的保險絲
from pydantic import BaseModel             # 規定「資料格式」的模具
from agent_core import LoveAgent           # 引入我們寫好的 AI 軍師大腦

# 1. 初始化伺服器與大腦
app = FastAPI()          # 建立一個伺服器實體，取名叫 app
agent = LoveAgent()      # 喚醒 AI 軍師，準備工作

# 2. 設定 CORS (跨域資源共享)
# 【重要筆記】
# 因為你的網頁 (index.html) 是直接打開的，而伺服器跑在 8000 埠。
# 瀏覽器為了安全會擋住這種「跨地址」的通訊。
# 這段代碼就是告訴伺服器：「不管是誰來敲門，通通都讓他們進來！」
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 允許所有的網站來源連線
    allow_credentials=True,   # 允許傳送 Cookie 等認證資訊
    allow_methods=["*"],      # 允許所有的請求方式 (GET, POST 等)
    allow_headers=["*"],      # 允許所有的標頭資訊
)

# 3. 定義「點菜單」的格式
# 我們規定前端傳過來的資料必須長這樣：{"message": "內容"}
class ChatRequest(BaseModel):
    message: str # 必須包含一個叫 message 的字串

# 4. 定義「聊天」的服務視窗 (API Endpoint)
# 當前端執行 fetch(".../api/chat") 時，就會觸發這個函式
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """
    接收使用者傳來的文字，請 AI 軍師回覆。
    """
    # 在你的黑色視窗 (Terminal) 印出紀錄，方便除錯
    print(f"收到前端訊息: {req.message}")
    
    # 把文字丟給大腦處理，並等待大腦回傳結果
    response_text = agent.chat(req.message)
    
    # 回傳 JSON 格式給網頁，網頁收到後會顯示在畫面上
    return {"reply": response_text}

# 5. 定義「重置」的服務視窗
# 當前端點擊「重新開始」按鈕時會觸發這裡
@app.post("/api/reset")
async def reset_endpoint():
    """
    清除 AI 的短期記憶，讓對話重新開始。
    """
    print("收到重置請求...")
    msg = agent.reset() # 呼叫大腦的重置功能
    return {"reply": msg}