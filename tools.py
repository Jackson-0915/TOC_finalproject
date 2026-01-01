# tools.py
import os
import datetime
from duckduckgo_search import DDGS

# ▼▼▼ 新增：Google Calendar 專用模組 ▼▼▼
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class LoveTools:
    # 靜態變數 (Cache)
    _knowledge_cache = {}

    @classmethod
    def load_knowledge_base(cls):
        """讀取 knowledge 資料夾下的所有 .txt 檔案"""
        if cls._knowledge_cache: return cls._knowledge_cache

        knowledge_dir = "knowledge"
        data = {}
        print(f"   [系統] 正在載入本地知識庫 ({knowledge_dir})...")
        
        if not os.path.exists(knowledge_dir):
            print(f"   [警告] 找不到 {knowledge_dir} 資料夾！")
            return {}

        try:
            for filename in os.listdir(knowledge_dir):
                if filename.endswith(".txt"):
                    filepath = os.path.join(knowledge_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        key = filename.replace(".txt", "")
                        data[key] = f.read()
                        print(f"   -> 已載入: {filename}")
            cls._knowledge_cache = data
            return data
        except Exception as e:
            print(f"   [錯誤] 讀取失敗: {e}")
            return {}

    @staticmethod
    def search_web(query):
        """工具：聯網搜尋 (備用)"""
        print(f"   [工具] 搜尋網路: {query}...")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(keywords=query, region='tw-tw', max_results=3))
            if not results: return "【系統提示】搜尋無結果。"
            return "\n".join([f"- {res['title']}: {res['body']}" for res in results])
        except Exception as e:
            return f"【系統提示】搜尋故障: {e}"

    @staticmethod
    def search_love_strategy(query):
        """工具：檢索本地 txt + 聯網備案"""
        try:
            print(f"   [工具] 查詢攻略: {query}...")
            kb = LoveTools.load_knowledge_base()
            
            if not kb: return LoveTools.search_web(query)

            results = []
            for category, content in kb.items():
                if category in query.lower() or query in content:
                    results.append(f"【{category} 檔案】\n{content[:800]}...")

            if results:
                return "\n\n".join(results)
            else:
                print("   [提示] 本地無資料，轉聯網搜尋...")
                return LoveTools.search_web(query)
        except Exception as e:
            return f"工具執行錯誤: {e}"

    @staticmethod
    def calculate_interest_score(text):
        """工具：好感度計算"""
        try:
            print(f"   [工具] 計算分數: {text}...")
            score = 60 
            details = []
            is_mirroring = "洗澡" in text and any(x in text for x in ["我也", "一起", "都"])
            
            if any(x in text for x in ["要不要", "有空", "約"]) and any(y in text for y in ["出去", "吃飯", "走走", "玩", "看"]):
                score += 40
                details.append("🔥🔥 明確邀約訊號 (+40)")

            negative_keywords = {"嗯嗯": -15, "哈哈": -5, "是喔": -15, "先忙": -20, "沒空": -20, "洗澡": -15}
            positive_keywords = {"你呢": 15, "下次": 20, "想去": 20, "好奇": 15, "好啊": 10, "我也": 15}

            for w, point in negative_keywords.items():
                if w in text:
                    if "洗澡" in w and is_mirroring: continue 
                    score += point 
                    details.append(f"扣分詞 '{w}'")

            for w, point in positive_keywords.items():
                if w in text:
                    score += point
                    details.append(f"加分詞 '{w}'")
            
            if is_mirroring:
                score += 20
                details.append("🛁 鏡像行為 (+20)")

            score = max(0, min(100, score))
            return f"分數: {score} (細節: {', '.join(details)})"
        except Exception as e:
            return f"計算錯誤: {e}"

    @staticmethod
    def generate_reply_styles(scenario):
        return f"情境：{scenario}。請提供：1.高冷回覆 2.幽默回覆 3.真誠回覆"

    # ▼▼▼ 修改：真實版 Google Calendar 工具 ▼▼▼
    @staticmethod
    def sync_to_google_calendar(title, start_time, duration="1h"):
        """
        將行程寫入 Google Calendar (真實 API)
        :param title: 行程標題
        :param start_time: ISO 格式時間字串 (e.g. '2026-01-02T19:00')
        :param duration: 持續時間字串 (e.g. '1h', '2h')
        """
        print(f"📅 [工具執行] 正在連接 Google Calendar API...")
        
        # 1. 定義權限範圍 (讀寫權限)
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        
        # 2. 檢查是否有已儲存的 Token (token.json)
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # 3. 如果沒有憑證或憑證過期，進行登入流程
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    return "❌ 錯誤：找不到 credentials.json，請確認檔案是否在資料夾中！"
                
                # 啟動本地伺服器進行 OAuth 登入
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 儲存新的 token 供下次使用
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('calendar', 'v3', credentials=creds)

            # 4. 時間計算邏輯
            # 解析 ISO 時間 (例如: 2026-01-02T19:00)
            try:
                # 嘗試標準 ISO 格式
                start_dt = datetime.datetime.fromisoformat(start_time)
            except ValueError:
                # 容錯處理：如果 AI 給的時間格式不標準，嘗試手動修正或拋錯
                # 這裡假設 AI 有時候會少給秒數，或者用空格分隔
                formatted_time = start_time.replace(" ", "T")
                if len(formatted_time.split(":")) == 2: formatted_time += ":00"
                start_dt = datetime.datetime.fromisoformat(formatted_time)

            # 計算結束時間 (預設 duration 格式為 "Xh")
            hours_to_add = 1
            if "h" in duration:
                try:
                    hours_to_add = int(duration.replace("h", ""))
                except: pass
            
            end_dt = start_dt + datetime.timedelta(hours=hours_to_add)

            # 5. 建立事件物件
            event = {
                'summary': title,
                'description': '由戀愛軍師 AI 自動安排 ❤️',
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Asia/Taipei',
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Asia/Taipei',
                },
            }

            # 6. 送出請求
            event_result = service.events().insert(calendarId='primary', body=event).execute()
            link = event_result.get('htmlLink')
            
            print(f"✅ Google API 回傳成功: {link}")
            return f"✅ 行程已同步！\n【{title}】已加入您的 Google Calendar。\n檢視連結: {link}"

        except Exception as e:
            print(f"❌ Google API 錯誤: {e}")
            return f"寫入行事曆失敗: {e}"