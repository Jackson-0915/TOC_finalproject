import requests
import json
import datetime

# ================= 1. 設定區 (Configuration) =================
# 請將您的 API Key 填入下方引號中
API_KEY = "b2756e656fb26fd9e42017c159087853f35416014d0be4f4ed94a09bb751ca9f"

# 學校 Gateway 的正確路徑
API_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/chat"

# 剛才查到的正確模型名稱 (請勿修改)
MODEL_NAME = "gemma3:4b"

# ================= 2. 工具區 (Tools) =================
def get_current_weather(location):
    """
    模擬天氣查詢工具。
    (如果要拿高分，之後可以把這裡改成呼叫 OpenWeatherMap API)
    """
    print(f"   [系統] 正在查詢 {location} 的天氣資料...")
    
    # 模擬資料庫
    weather_db = {
        "Taipei": "陰天, 22°C, 降雨機率 30%",
        "Tainan": "晴天, 28°C, 降雨機率 0%",
        "New York": "下雪, -2°C, 需穿著厚外套",
        "Tokyo": "多雲, 15°C",
        "Kaohsiung": "雨天, 9°C"
    }
    
    # 搜尋 (忽略大小寫)
    for city, info in weather_db.items():
        if city.lower() in location.lower():
            return info
            
    return f"找不到 {location} 的氣象資料 (目前僅支援: Taipei, Tainan, New York, Tokyo)"

def get_current_time():
    """取得現在時間"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ================= 3. Agent 核心邏輯 (Core) =================
def chat_with_llm(messages):
    """傳送訊息給 LLM 的通用函數"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "temperature": 0.1 # 降低隨機性，讓它更聽話
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status() # 檢查是否有 404/500 錯誤
        return response.json()['message']['content']
    except Exception as e:
        return f"連線錯誤: {e}"

def run_agent(user_input):
    print(f"\nUser: {user_input}")
    
    # --- 步驟 A: 定義大腦規則 (System Prompt) ---
    # 教導 LLM: 如果需要查資料，請給我 JSON；否則直接回話
    system_prompt = f"""
    你是一個智慧助理。目前時間是 {get_current_time()}。
    
    【工具使用規則】
    如果你需要查詢天氣，請務必 **只回傳** JSON 格式指令，不要說廢話：
    {{"tool": "get_weather", "location": "城市英文名"}}
    
    【範例】
    用戶: "台南天氣如何?" -> 回答: {{"tool": "get_weather", "location": "Tainan"}}
    用戶: "你好" -> 回答: 你好！有什麼我可以幫你的嗎？
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    # --- 步驟 B: 第一次呼叫 (思考與決策) ---
    llm_response = chat_with_llm(messages)
    
    # --- 步驟 C: 解析回應 ---
    # 檢查 LLM 是否回傳了 JSON 格式的工具指令
    if '{"tool":' in llm_response:
        try:
            # 擷取 JSON 字串 (防止 LLM 多話)
            json_str = llm_response[llm_response.find("{"):llm_response.rfind("}")+1]
            cmd = json.loads(json_str)
            
            if cmd["tool"] == "get_weather":
                # 1. 執行工具
                location = cmd["location"]
                weather_info = get_current_weather(location)
                
                # 2. 把結果告訴 LLM，請它做最後總結
                print(f"   [系統] 工具回傳結果: {weather_info}")
                
                final_messages = [
                    {"role": "system", "content": "你是一個親切的氣象主播，請根據提供的數據回答用戶。"},
                    {"role": "user", "content": f"用戶問 {location} 天氣，資料庫回傳：'{weather_info}'。請用中文回答用戶。"}
                ]
                final_response = chat_with_llm(final_messages)
                print(f"Agent: {final_response}")
                
        except Exception as e:
            print(f"Agent: 發生錯誤 (解析失敗): {e}")
            print(f"原始回應: {llm_response}")
    else:
        # 不需要工具，直接印出回應
        print(f"Agent: {llm_response}")

# ================= 4. 主程式入口 =================
if __name__ == "__main__":
    print("=== Weather Agent 啟動中 (Model: gemma3:4b) ===")
    
    # 測試 1: 閒聊
    run_agent("你好，你是誰？")
    
    # 測試 2: 查詢天氣 (觸發工具)
    run_agent("請問現在 Tainan 的天氣好嗎？")
    
    # 測試 3: 查詢未知地區
    run_agent("我想知道 Kaohsiung 的天氣")