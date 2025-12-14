import requests
import json
import datetime
import yfinance as yf
import twstock
import time

# ================= 1. 設定區 =================
API_KEY = "b2756e656fb26fd9e42017c159087853f35416014d0be4f4ed94a09bb751ca9f"
API_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/chat"
MODEL_NAME = "gemma3:4b"

# ================= 2. 全球股市地圖 (Knowledge Base) =================
MARKET_DB = {
    "Asia": {
        "Taiwan": {"suffix": ".TW", "name": "台灣證交所", "tool": "twstock", "examples": "2330(台積電), 2603(長榮)"},
        "Japan": {"suffix": ".T", "name": "東京證交所", "tool": "yfinance", "examples": "7203(Toyota), 6758(Sony)"},
        "Hong Kong": {"suffix": ".HK", "name": "香港證交所", "tool": "yfinance", "examples": "0700(騰訊), 9988(阿里)"},
    },
    "Americas": {
        "USA": {"suffix": "", "name": "美股 (NYSE/NASDAQ)", "tool": "yfinance", "examples": "NVDA(輝達), AAPL(蘋果), TSLA(特斯拉)"},
    },
    "Europe": {
        "Germany": {"suffix": ".DE", "name": "法蘭克福", "tool": "yfinance", "examples": "BMW, VOW3(福斯)"},
    }
}

# ================= 3. 工具區 (Tools) =================

def search_market_info(query):
    """[工具] 查詢股市資訊 (增強版: 支援列出所有)"""
    query = query.lower()
    
    # 如果用戶問 "有哪些"、"全部"、"國家"，直接列出總表
    if any(k in query for k in ["哪些", "all", "list", "有什麼", "國家"]):
        report = "🌍 目前系統支援的全球股市地圖：\n"
        for continent, countries in MARKET_DB.items():
            report += f"\n【{continent}】\n"
            for c, info in countries.items():
                report += f"  - {c}: {info['name']} (範例: {info['examples']})\n"
        return report

    # 搜尋特定大洲或國家
    for continent, countries in MARKET_DB.items():
        if query in continent.lower():
            report = f"【{continent}】包含以下市場：\n"
            for c, info in countries.items():
                report += f"- {c}: {info['examples']}\n"
            return report
            
        for country, info in countries.items():
            if query in country.lower():
                return f"【{country}】\n交易所: {info['name']}\n代碼規則: {info['suffix'] if info['suffix'] else '直接輸入代號'}\n熱門股範例: {info['examples']}"

    return "抱歉，目前資料庫尚未收錄該地區，請試著問「有哪些國家」。"

def get_stock_price(symbol, country_key=None):
    """[工具] 抓股價 (含指數模式)"""
    # 1. 處理大盤指數查詢 (若 symbol 是 index)
    if symbol == "TAIEX": # 台股大盤
        real_symbol = "^TWII" 
        tool_type = "yfinance"
    else:
        # 一般股票邏輯
        suffix = ""
        tool_type = "yfinance"
        if country_key:
            for cont, countries in MARKET_DB.items():
                for c_name, info in countries.items():
                    if country_key.lower() in c_name.lower():
                        suffix = info['suffix']
                        tool_type = info['tool']
                        break
        
        real_symbol = f"{symbol}{suffix}" if suffix and not symbol.endswith(suffix) else symbol

    print(f"   [系統] 搜尋: {real_symbol} (來源: {tool_type})...")

    try:
        # 台股個股特化處理
        if tool_type == "twstock" and "TWII" not in real_symbol:
            clean_symbol = real_symbol.replace(".TW", "")
            stock = twstock.realtime.get(clean_symbol)
            if stock['success']:
                price = stock['realtime'].get('latest_trade_price', "-")
                if price == "-": price = stock['realtime'].get('best_bid_price', [None])[0]
                if price: return float(price), f"【台股即時】{real_symbol} 現價: {price}"
            tool_type = "yfinance" 
            real_symbol = f"{clean_symbol}.TW"

        # yfinance 通用
        stock = yf.Ticker(real_symbol)
        price = stock.fast_info.get('last_price', None)
        if not price:
            hist = stock.history(period='1d')
            if not hist.empty: price = hist['Close'].iloc[-1]
        
        if price: return price, f"【報價】{real_symbol} 現價: {price:.2f}"
        return None, f"查無資料 ({real_symbol})"
    except Exception as e:
        return None, f"錯誤: {e}"

def analyze_strategy(symbol, country, quantity, tp, sl):
    """[工具] 計算策略 (新增防呆：沒給止盈止損就不算)"""
    
    # 防呆：如果代號是 "Trend" 或空值，代表 LLM 沒抓到股票，改查大盤
    if symbol in ["Trend", "Unknown", "None"] or not symbol:
        if country and "Taiwan" in country:
            return get_stock_price("TAIEX")[1] + "\n(由於您未指定個股代號，以上為台股大盤指數)"
        return "請提供具體的股票代號 (例如: 2330, NVDA) 我才能分析喔！"

    # 防呆：如果沒有設定止盈止損 (tp=0, sl=0)，只查報價
    if tp == 0 and sl == 0:
        price, msg = get_stock_price(symbol, country)
        return msg + "\n(因為您未提供止盈止損價，僅提供報價。若需分析請說：買XXX 止盈OO 止損XX)"

    price, msg = get_stock_price(symbol, country)
    if price is None: return msg

    # 開始計算
    unit = "張" if country and "Taiwan" in country else "股"
    shares = quantity * 1000 if unit == "張" else quantity
    cost = price * shares
    
    # 避免除以零
    if cost == 0: return "錯誤：股價為 0"

    profit = (tp - price) * shares
    loss = (price - sl) * shares
    roi_win = (profit / cost) * 100
    roi_loss = (loss / cost) * 100 * -1
    ev = (profit * 0.5) - (loss * 0.5)

    return f"""
    📊 分析報告 ({symbol})
    -----------------------
    現價: {price:.2f} | 成本: {int(cost):,}
    🎯 止盈 ({tp}): 預期賺 {int(profit):,} ({roi_win:.1f}%)
    🛑 止損 ({sl}): 預期賠 {int(loss):,} ({roi_loss:.1f}%)
    🎲 期望值: {int(ev):,}
    """

# ================= 4. Agent 核心 =================
def chat_with_llm(messages):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL_NAME, "messages": messages, "stream": False, "temperature": 0.1}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        return response.json()['message']['content']
    except: return "連線逾時"

def run_agent(user_input):
    system_prompt = """
    你是一個聰明的股市助理。
    
    【工具使用規則】
    1. 用戶問「有哪些國家/市場/美股/範例」 -> 回傳 {"tool": "search_market", "query": "關鍵字"}
       (例如問"美股有哪些"，query填"USA")
    
    2. 用戶問「趨勢/分析/價格/怎麼買」 -> 回傳 {"tool": "analyze", "symbol": "代號", "country": "國家英文", "qty": 數量, "tp": 止盈, "sl": 止損}
       * 若用戶沒給止盈止損，tp 和 sl 請填 0。
       * 若用戶沒說股票 (如只問"台股趨勢")，symbol 請填 "Trend"。
       * 若用戶只說中文名 (如台積電)，請轉成 2330；輝達轉 NVDA。
    """

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}]
    llm_response = chat_with_llm(messages)
    
    if '{"tool":' in llm_response:
        try:
            json_str = llm_response[llm_response.find("{"):llm_response.rfind("}")+1]
            cmd = json.loads(json_str)
            tool = cmd["tool"]
            
            print(f"   [系統] 呼叫工具: {tool} | 參數: {cmd}")

            if tool == "search_market":
                res = search_market_info(cmd["query"])
                final_msg = f"資料庫回傳：\n{res}"

            elif tool == "analyze":
                res = analyze_strategy(cmd.get("symbol"), cmd.get("country"), cmd.get("qty",1), cmd.get("tp",0), cmd.get("sl",0))
                final_msg = f"計算結果：\n{res}"
            
            final_msgs = [{"role": "system", "content": "請根據結果回答用戶，語氣要專業且友善。"}, {"role": "user", "content": final_msg}]
            print(f"Agent: {chat_with_llm(final_msgs)}")

        except Exception as e:
            print(f"Agent Error: {e}")
    else:
        print(f"Agent: {llm_response}")

if __name__ == "__main__":
    print("=== 全球股市 Agent (修正版) ===")
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["exit", "quit"]: break
            run_agent(user_input)
        except KeyboardInterrupt: break