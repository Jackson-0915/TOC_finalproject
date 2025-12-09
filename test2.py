import yfinance as yf
import requests
import json

# ==========================================
# 第一部分：工具箱 (Tools / Retrieval)
# 這就是 RAG 的 "R" (Retrieval)
# ==========================================
def get_stock_data(symbol):
    """
    輸入股票代號 (如 NVDA)，回傳即時股價與基本面資訊
    """
    print(f"[System] 正在檢索 {symbol} 的資料...") #用來Demo時顯示你在做事
    try:
        stock = yf.Ticker(symbol)
        # 取得最新收盤價
        history = stock.history(period="1d")
        if history.empty:
            return None
        current_price = history['Close'].iloc[-1]
        
        # 取得基本資訊 (這裡可以依你喜好增加，如 PE Ratio)
        info = stock.info
        
        # 整理成乾淨的文字，準備餵給 LLM
        stock_context = (
            f"Stock Symbol: {symbol}\n"
            f"Current Price: {current_price:.2f} USD\n"
            f"Company Name: {info.get('longName', 'Unknown')}\n"
            f"Sector: {info.get('sector', 'Unknown')}\n"
            f"Previous Close: {info.get('previousClose', 'N/A')}\n"
        )
        return stock_context
    except Exception as e:
        return f"Error retrieving data: {str(e)}"

# ==========================================
# 第二部分：LLM API 介面
# 這是作業要求的核心 [cite: 5]
# ==========================================
def call_ta_llm_api(prompt):
    """
    呼叫助教提供的 LLM API
    """
    API_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/chat" # 記得換成助教給的網址
    API_KEY = "b2756e656fb26fd9e42017c159087853f35416014d0be4f4ed94a09bb751ca9f"            # 記得換成助教給的 Key
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "gemma3:4b", # 依助教文件填寫
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    # 模擬 API 回傳 (等你拿到 Key 後，把下面這段解開)
    # response = requests.post(API_URL, headers=headers, json=payload)
    # return response.json()['message']['content']
    
    # 暫時的假回傳 (為了讓你現在能跑 code)
    return f"[LLM 模擬回應] 根據資料，該股票表現不錯... (這是假的回應)"

# ==========================================
# 第三部分：Agent 主邏輯 (The Brain)
# 這就是 RAG 的 "A" (Augment) + "G" (Generate)
# ==========================================
def run_stock_agent(user_query):
    
    # 1. 意圖識別 (簡單版：直接用關鍵字判斷)
    # 進階版可以用 LLM 判斷是否需要查股價，但作業用簡單版即可
    target_symbol = None
    if "NVDA" in user_query.upper():
        target_symbol = "NVDA"
    elif "TSM" in user_query.upper(): # 台積電
        target_symbol = "TSM"
    # 你可以寫一個簡單的 parser 抓取英文代號
    
    context_data = ""
    
    # 2. 執行檢索 (Retrieval)
    if target_symbol:
        context_data = get_stock_data(target_symbol)
    
    # 3. 增強 Prompt (Augmentation)
    # 這是 RAG 最關鍵的一步：把查到的資料 "塞" 進 Prompt
    if context_data:
        final_prompt = (
            f"你是一個專業的股票分析師。\n"
            f"以下是從資料庫檢索到的最新數據：\n"
            f"---------------------\n"
            f"{context_data}\n"
            f"---------------------\n"
            f"使用者問題：{user_query}\n"
            f"請根據上述數據回答使用者的問題，如果數據顯示股價上漲，請給予正面的評論。"
        )
    else:
        # 如果沒查到資料，就當普通聊天
        final_prompt = user_query

    print(f"\n[System] 發送給 LLM 的 Prompt:\n{final_prompt}\n")

    # 4. 生成回答 (Generation)
    response = call_ta_llm_api(final_prompt)
    
    print("Agent 回答：")
    print(response)

# ==========================================
# 測試執行
# ==========================================
if __name__ == "__main__":
    user_input = input("您好，有什麽想詢問的嗎？")
    run_stock_agent(user_input)