# tools.py
import os
import datetime
from duckduckgo_search import DDGS  # 免費的搜尋引擎工具，不用 API Key 就能上網

# ▼▼▼ 這裡是用來跟 Google 溝通的專業零件 ▼▼▼
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class LoveTools:
    """
    這是一個工具箱類別，裡面裝著各式各樣 AI 可以使用的法寶。
    """
    
    # 這是「快取記憶體」：讀過一次的檔案就記在這裡，不用每次都重新打開檔案，速度會變快
    _knowledge_cache = {}

    @classmethod
    def load_knowledge_base(cls):
        """
        【法寶 1：本地知識庫】
        作用：讀取資料夾 knowledge 裡的所有文字檔，就像是 AI 的「私房攻略本」。
        """
        if cls._knowledge_cache: return cls._knowledge_cache # 如果讀過了，直接拿舊的資料

        knowledge_dir = "knowledge"
        data = {}
        print(f"   [系統] 正在載入本地知識庫 ({knowledge_dir})...")
        
        # 檢查資料夾是否存在，不存在就報錯
        if not os.path.exists(knowledge_dir):
            print(f"   [警告] 找不到 {knowledge_dir} 資料夾！")
            return {}

        try:
            # 一個一個檢查資料夾裡的檔案
            for filename in os.listdir(knowledge_dir):
                if filename.endswith(".txt"): # 只讀文字檔
                    filepath = os.path.join(knowledge_dir, filename)
                    # 打開檔案並讀取內容
                    with open(filepath, "r", encoding="utf-8") as f:
                        key = filename.replace(".txt", "") # 用檔名當關鍵字 (例如: 穿搭)
                        data[key] = f.read()
                        print(f"   -> 已載入: {filename}")
            cls._knowledge_cache = data # 存入快取
            return data
        except Exception as e:
            print(f"   [錯誤] 讀取失敗: {e}")
            return {}

    @staticmethod
    def search_web(query):
        """
        【法寶 2：聯網搜尋】
        作用：如果攻略本裡查不到，就上網 Google (這裡用 DuckDuckGo)。
        """
        print(f"   [工具] 搜尋網路: {query}...")
        try:
            with DDGS() as ddgs:
                # 只抓前 3 筆結果，避免資訊量爆炸
                results = list(ddgs.text(keywords=query, region='tw-tw', max_results=3))
            if not results: return "【系統提示】搜尋無結果。"
            # 把搜尋結果組合成一段文字
            return "\n".join([f"- {res['title']}: {res['body']}" for res in results])
        except Exception as e:
            return f"【系統提示】搜尋故障: {e}"

    @staticmethod
    def search_love_strategy(query):
        """
        【法寶 3：複合式查詢】
        作用：先看「攻略本」，攻略本沒有再去「上網搜尋」。
        """
        try:
            print(f"   [工具] 查詢攻略: {query}...")
            kb = LoveTools.load_knowledge_base()
            
            if not kb: return LoveTools.search_web(query)

            results = []
            for category, content in kb.items():
                # 如果關鍵字出現在攻略本的分類或內容中
                if category in query.lower() or query in content:
                    results.append(f"【{category} 檔案】\n{content[:800]}...")

            if results:
                return "\n\n".join(results)
            else:
                # 本地沒資料，自動轉為聯網搜尋
                print("   [提示] 本地無資料，轉聯網搜尋...")
                return LoveTools.search_web(query)
        except Exception as e:
            return f"工具執行錯誤: {e}"

    @staticmethod
    def calculate_interest_score(text):
        """
        【法寶 4：好感度心跳計】
        作用：分析一段對話，判斷對方對你的好感度。
        """
        try:
            print(f"   [工具] 計算分數: {text}...")
            score = 60 # 基礎分：路人等級
            details = []
            
            # 特殊判斷：鏡像行為（例如：對方說「我也要去洗澡了」，可能代表同步感）
            is_mirroring = "洗澡" in text and any(x in text for x in ["我也", "一起", "都"])
            
            # 判斷有沒有「邀約」關鍵字
            if any(x in text for x in ["要不要", "有空", "約"]) and any(y in text for y in ["出去", "吃飯", "走走"]):
                score += 40
                details.append("🔥🔥 明確邀約訊號 (+40)")

            # 扣分關鍵字：冷淡的代名詞
            negative_keywords = {"嗯嗯": -15, "哈哈": -5, "是喔": -15, "先忙": -20, "沒空": -20, "洗澡": -15}
            # 加分關鍵字：積極的代名詞
            positive_keywords = {"你呢": 15, "下次": 20, "想去": 20, "好奇": 15, "好啊": 10, "我也": 15}

            # 遍歷文字進行打分
            for w, point in negative_keywords.items():
                if w in text:
                    if "洗澡" in w and is_mirroring: continue # 如果是鏡像行為，不扣洗澡分
                    score += point 
                    details.append(f"扣分詞 '{w}'")

            for w, point in positive_keywords.items():
                if w in text:
                    score += point
                    details.append(f"加分詞 '{w}'")
            
            if is_mirroring:
                score += 20
                details.append("🛁 鏡像行為 (+20)")

            # 限制分數在 0~100 之間
            score = max(0, min(100, score))
            return f"分數: {score} (細節: {', '.join(details)})"
        except Exception as e:
            return f"計算錯誤: {e}"

    @staticmethod
    def sync_to_google_calendar(title, start_time, duration="1h"):
        """
        【法寶 5：行事曆同步 (地表最強工具)】
        作用：這是真的！它會連到你的 Google 帳號，幫你把約會日期填上去。
        """
        print(f"📅 [工具執行] 正在連接 Google Calendar API...")
        
        # 1. SCOPES 是權限範圍：告訴 Google 我們要「管理」行事曆
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        
        # 2. Token 是「免死金牌」：如果你以前登入過，會存在 token.json，就不用每次都重新掃 QR Code
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # 3. 如果「金牌」無效或沒拿過，就啟動瀏覽器讓你點選 Google 登入
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request()) # 舊金牌過期了，換一個新的
            else:
                # 這裡需要你有一個 credentials.json (從 Google Cloud 控制台下載的)
                if not os.path.exists('credentials.json'):
                    return "❌ 錯誤：找不到 credentials.json 檔案！"
                
                # 開啟一個小型的伺服器讓你在瀏覽器點擊「允許授權」
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 把拿到的金牌存起來，下次就不用再登入了
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # 建立與 Google 行事曆服務的連線
            service = build('calendar', 'v3', credentials=creds)

            # 4. 時間處理：把 AI 給的亂糟糟時間，轉成標準格式
            try:
                # 嘗試將 ISO 格式轉成電腦認識的時間物件
                start_dt = datetime.datetime.fromisoformat(start_time)
            except ValueError:
                # 如果格式不對 (例如少個 T)，手動修復它
                formatted_time = start_time.replace(" ", "T")
                if len(formatted_time.split(":")) == 2: formatted_time += ":00"
                start_dt = datetime.datetime.fromisoformat(formatted_time)

            # 計算這場約會要多久（預設 1 小時）
            hours_to_add = 1
            if "h" in duration:
                try: hours_to_add = int(duration.replace("h", ""))
                except: pass
            
            end_dt = start_dt + datetime.timedelta(hours=hours_to_add)

            # 5. 定義要傳給 Google 的「包裹」內容
            event = {
                'summary': title, # 行程標題 (如：跟 MuQ醬去吃拉麵)
                'description': '由戀愛軍師 AI 自動安排 ❤️',
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Asia/Taipei', # 設定為台灣時區
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Asia/Taipei',
                },
            }

            # 6. 把包裹送出去！
            event_result = service.events().insert(calendarId='primary', body=event).execute()
            link = event_result.get('htmlLink') # 拿到 Google 回傳的該行程連結
            
            return f"✅ 行程已同步！\n【{title}】已加入您的 Google Calendar。\n檢視連結: {link}"

        except Exception as e:
            return f"寫入行事曆失敗: {e}"