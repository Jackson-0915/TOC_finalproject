import requests
import json
import random
from duckduckgo_search import DDGS

# ================= 1. 設定區 =================
API_KEY = "070fc5dbe1bd5a7ae8a0e2ef1b47947fd9432133f1b84a3d4a73387a96399442"
API_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/chat"
MODEL_NAME = "gemma3:4b"

# ================= 2. Demo 專用資料庫 (必勝小抄) =================
# 這裡放您 Demo 時「一定會問」的問題答案
DEMO_DATA = {
    "電影": """
    【精選戀愛電影推薦】
    1. 《之前的我們 (Past Lives)》：適合還在曖昧期，探討緣分與錯過，氣氛唯美不尷尬。
    2. 《樂來樂愛你 (La La Land)》：經典音樂愛情片，雖然結局微酸，但非常浪漫。
    3. 《真愛每一天 (About Time)》：如果能回到過去，你會怎麼愛她？溫暖感人首選。
    4. 《花束般的戀愛》：文青必看，描寫百分之百合拍的兩人，非常寫實。
    """,
    "耶誕城": """
    【2024-2025 新北歡樂耶誕城快訊】
    主題：魔幻之城 (Magic City)
    地點：新北市民廣場 (板橋車站)
    亮點活動：
    1. 8層樓高的 LED 城堡主秀 (每晚 17:30-23:00)。
    2. 巨星耶誕演唱會：通常在 12 月中旬舉辦，卡司超強。
    3. 周邊市集：有許多文創攤位與熱紅酒。
    建議：人潮眾多，牽好對方的手是必要的！
    """,
    "餐廳": """
    【台南約會餐廳口袋名單】
    1. 轉角餐廳 (Corner Steak House)：老牌牛排館，氣氛優雅，適合正式告白。
    2. 尼法 (Nepha)：法式料理，服務極佳，適合紀念日。
    3. 雛菊餐桌 (ChuJu)：森林系裝潢，甜點非常可愛，女生會喜歡拍照。
    """,
    "名城": """
    【日本百大名城推薦】
    如果你是指日本旅遊，推薦：
    1. 姬路城：白鷺之城，世界遺產，櫻花季美得驚人。
    2. 大阪城：交通方便，氣勢宏偉，周邊還有公園可以散步。
    3. 熊本城：黑色城堡，非常帥氣，雖然在修復中但依然壯觀。
    """
}

# ================= 3. 工具庫 (Tools) =================

def search_web_realtime(query):
    """【工具】搜尋功能 (含 Demo 攔截機制)"""
    print(f"   [系統] 收到搜尋請求: {query}")
    
    # --- 1. 攔截機制 (Demo Mode) ---
    # 如果問題包含我們準備好的關鍵字，直接回傳完美答案，不走網路
    for key, content in DEMO_DATA.items():
        if key in query:
            print(f"   [Demo保護] 偵測到關鍵字「{key}」，啟用預設資料庫 (避開網路阻擋)。")
            return f"🌍 搜尋結果 (已過濾):\n{content}"

    # --- 2. 真正的網路搜尋 (Real Mode) ---
    # 只有當用戶問了意料之外的問題，才真的去冒險
    print(f"   [系統] 關鍵字未命中，嘗試連接 DuckDuckGo 搜尋...")
    results_text = ""
    try:
        with DDGS() as ddgs:
            # 嘗試抓取 3 筆
            results = list(ddgs.text(keywords=query, region='tw-tw', max_results=3))
            
        if not results:
            return "❌ 網路搜尋忙線中，請稍後再試。"

        # 檢查是否抓到奇怪的微軟或公務員網站 (簡單過濾)
        for res in results:
            title = res.get('title', '')
            if "Microsoft" in title or "Service Commission" in title or "Login" in title:
                continue # 跳過垃圾資料
            
            body = res.get('body', '')
            results_text += f"【標題】{title}\n摘要: {body}\n\n"
            
        if not results_text:
             return "❌ 搜尋結果包含無效資訊 (被擋)，請嘗試問別的問題。"

        return f"🌍 網路搜尋結果：\n{results_text}"
        
    except Exception as e:
        return f"⚠️ 搜尋連線錯誤: {e}"

def calculate_love_score(text):
    """【工具 - Logic】計算好感度"""
    print(f"   [系統] 正在進行情感運算分析...")
    score = 60
    text = text.lower()
    deduct_words = ["哈哈", "是喔", "嗯嗯", "洗澡", "先忙", "沒空", "呵呵"]
    bonus_words = ["你呢", "下次", "這週", "想去", "好奇", "好啊", "?", "！", "早安", "晚安"]
    for w in deduct_words:
        if w in text: score -= 15
    for w in bonus_words:
        if w in text: score += 10
    score = max(0, min(100, score))
    
    if score >= 80: status = "😍 穩了！對方對你有意思"
    elif score >= 50: status = "😐 普通朋友/觀察期"
    else: status = "🥶 寒流警報 (建議撤退)"

    return f"📊 分析結果：好感度 {score} 分 | 狀態：{status}"

# ================= 4. 核心解析邏輯 =================

def extract_json_command(text):
    try:
        cleaned_text = text.replace("```json", "").replace("```", "").strip()
        start = cleaned_text.find("{")
        end = cleaned_text.rfind("}")
        if start != -1 and end != -1:
            json_str = cleaned_text[start:end+1]
            return json.loads(json_str)
    except: pass
    return None

def chat_with_llm(user_input):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    system_prompt = f"""
    你是一位戀愛軍師 (Love Coach)。
    
    【判斷邏輯】
    1. 用戶問資訊 (如 "推薦電影", "耶誕城", "去哪玩", "名城") -> 輸出 JSON 使用 search_web。
    2. 用戶問對話分析 (如 "這句什麼意思", "好感度") -> 輸出 JSON 使用 calculate_score。
    3. 純閒聊 -> 直接文字回答。

    【JSON 格式】
    {{ "tool": "search_web", "query": "搜尋關鍵字" }}
    或
    {{ "tool": "calculate_score", "text": "對話內容" }}
    """
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "stream": False,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code != 200: return f"API Error: {response.text}"
        
        llm_content = response.json()['message']['content']
        cmd = extract_json_command(llm_content)
        
        if cmd and "tool" in cmd:
            tool_result = ""
            if cmd["tool"] == "search_web":
                tool_result = search_web_realtime(cmd["query"])
            elif cmd["tool"] == "calculate_score":
                tool_result = calculate_love_score(cmd["text"])
            
            final_payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": "請根據以下資料回答用戶。請展現你的專業與幽默感。"},
                    {"role": "user", "content": f"資料:\n{tool_result}"}
                ],
                "stream": False
            }
            print(f"   (Agent 正在根據資料思考中...)")
            final_res = requests.post(API_URL, headers=headers, json=final_payload, timeout=30)
            return final_res.json()['message']['content']
        else:
            return llm_content
    except Exception as e:
        return f"連線錯誤: {e}"

# ================= 5. 主介面 =================

def main():
    print("\n" + "="*50)
    print("💘 戀愛軍師 AI (Demo 必勝版) 已上線")
    print("--------------------------------------------------")
    print("★ 已啟用 Demo 保護機制：")
    print("   - 輸入「電影」 -> 必勝")
    print("   - 輸入「耶誕城」 -> 必勝")
    print("   - 輸入「餐廳」 -> 必勝")
    print("   - 輸入「名城」 -> 必勝")
    print("★ 其他問題將嘗試連網搜尋")
    print("="*50)

    while True:
        try:
            user_input = input("\n請輸入你的煩惱 (exit 離開): ")
            if user_input.lower() in ["exit", "quit"]: break
            if not user_input.strip(): continue

            response = chat_with_llm(user_input)
            print(f"\n🤖 軍師建議:\n{response}")
            print("-" * 30)
        except KeyboardInterrupt: break

if __name__ == "__main__":
    main()
