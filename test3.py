import yfinance as yf
import requests
import json
import re

# ==========================================
# 設定區 (Configuration)
# ==========================================
# 請在此填入助教提供的真實資訊
API_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/chat" 
API_KEY = "b2756e656fb26fd9e42017c159087853f35416014d0be4f4ed94a09bb751ca9f"  # <--- 請務必換回你的 Key
MODEL_NAME = "gemma3:4b"            # <--- 請確認模型名稱正確

# ==========================================
# 核心功能：呼叫 LLM (共用的發送器)
# ==========================================
def call_llm_core(prompt):
    """
    負責與 API 進行實際溝通的底層函式
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    try:
        # 這裡必須是真的發送請求，否則無法動態判斷股票
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status() # 檢查是否有連線錯誤
        
        # 解析回傳的 JSON (根據助教 API 格式可能需要微調)
        # 假設格式是標準 OpenAI/Ollama 格式
        result = response.json()
        if 'choices' in result:
             return result['choices'][0]['message']['content']
        elif 'message' in result:
             return result['message']['content']
        else:
             # 若格式不同，直接回傳全文以便除錯
             return str(result)
             
    except Exception as e:
        print(f"[Error] API 呼叫失敗: {e}")
        return None

# ==========================================
# 步驟 1：代號轉換器 (The Extractor)
# 這就是讓你能查「任何股票」的關鍵
# ==========================================
def extract_stock_symbol(user_query):
    """
    使用 LLM 判斷使用者想要查的是台股還是美股代號
    """
    print("[System] 正在分析股票代號與市場偏好...")
    
    # 修改後的 Prompt，增加了針對 ADR/美股 的邏輯
    extraction_prompt = (
        f"User Query: '{user_query}'\n\n"
        "Task: Identify the stock symbol based on the user's intent.\n"
        "Rules:\n"
        "1. **Distinguish Markets for TSMC (台積電):**\n"
        "   - If the user explicitly mentions 'US stock', 'ADR', '美股', or uses English 'TSMC', return 'TSM'.\n"
        "   - If the user just says '台積電' or 'TSMC' without specifying US/ADR, default to Taiwan stock '2330.TW'.\n"
        "2. **General Logic:**\n"
        "   - Taiwan stocks: Append '.TW' (e.g., 鴻海 -> 2317.TW).\n"
        "   - US stocks: Return the ticker directly (e.g., NVDA, AAPL).\n"
        "3. Output ONLY the symbol string. No other text.\n"
        "Answer:"
    )
    
    response = call_llm_core(extraction_prompt)
    
    if response:
        # 清理回應
        symbol = re.sub(r'[^a-zA-Z0-9.]', '', response.strip())
        return symbol
    return None

# ==========================================
# 步驟 2：資料檢索 (The Tool)
# ==========================================
def get_stock_data(symbol):
    print(f"[System] 正在檢索 {symbol} 的資料 (yfinance)...")
    try:
        stock = yf.Ticker(symbol)
        history = stock.history(period="1d")
        
        if history.empty:
            return None
            
        current_price = history['Close'].iloc[-1]
        info = stock.info
        
        # 處理台灣股票貨幣單位
        # 重點
        currency = info.get('currency', 'USD')
        
        stock_context = (
            f"Stock Symbol: {symbol}\n"
            f"Company Name: {info.get('longName', symbol)}\n"
            f"Current Price: {current_price:.2f} {currency}\n"
            f"52 Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}\n"
            f"52 Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}\n"
        )
        return stock_context
    except Exception as e:
        print(f"[Error] yfinance 錯誤: {e}")
        return None

# ==========================================
# 步驟 3：主邏輯 (The Agent)
# ==========================================
def run_stock_agent(user_query):
    
    # 1. 先問 LLM：這是在問哪支股票？
    target_symbol = extract_stock_symbol(user_query)
    
    context_data = ""
    
    # 2. 如果有找到代號，就去查資料
    if target_symbol:
        print(f"[System] 識別出股票代號：{target_symbol}")
        context_data = get_stock_data(target_symbol)
        
        if not context_data:
            print(f"[System] 雖然找到了代號 {target_symbol}，但在 Yahoo Finance 抓不到資料 (可能代號錯誤或下市)。")
    else:
        print("[System] 未偵測到具體股票名稱，進入閒聊模式。")

    # 3. 組合最終 Prompt
    if context_data:
        final_prompt = (
            f"你是專業的投資顧問。請根據以下真實市場數據回答使用者的問題。\n"
            f"若數據顯示價格上漲，語氣請樂觀；若下跌，請語帶保留。\n"
            f"---------------------\n"
            f"{context_data}\n"
            f"---------------------\n"
            f"使用者問題：{user_query}"
        )
    else:
        # 沒查到股票資料，就直接把使用者的話丟給 LLM
        final_prompt = user_query

    print(f"[System] 生成最終回答中...")
    
    # 4. 最終回答
    response = call_llm_core(final_prompt)
    print("\n" + "="*20 + " Agent 回答 " + "="*20)
    print(response)
    print("="*50)

# ==========================================
# 執行
# ==========================================
if __name__ == "__main__":
    while True:
        user_input = input("\n請輸入關於股票的問題 (輸入 q 離開):")
        if user_input.lower() == 'q':
            break
        run_stock_agent(user_input)