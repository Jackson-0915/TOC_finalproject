# tools.py
import os           # 用來處理電腦檔案系統（例如：檢查資料夾、讀取檔案）
import datetime     # 用來處理時間（例如：計算約會什麼時候結束）
from duckduckgo_search import DDGS  # 網路搜索工具，就像幫 AI 裝上瀏覽器

# ▼▼▼ Google Calendar 專用零件：這些是用來跟 Google 伺服器進行安全握手的 ▼▼▼
from google.auth.transport.requests import Request # 發送請求給 Google
from google.oauth2.credentials import Credentials  # 存放登入後的「通行證」
from google_auth_oauthlib.flow import InstalledAppFlow # 處理「點擊允許登入」的流程
from googleapiclient.discovery import build       # 真正用來操作行事曆的工人

class LoveTools:
    """
    這是一個『靜態工具箱』。我們不需要真的『買』一個箱子 (實例化)，
    直接從 LoveTools 裡面拿工具出來用就可以了。
    """
    
    # 【快取記憶體】
    # 就像你的大腦會記住住家地址，不用每次都翻地圖。
    # 如果讀過一次檔案，我們就把內容存在這裡，下次秒讀。
    _knowledge_cache = {}

    @classmethod
    def load_knowledge_base(cls):
        """
        工具 1：【私房攻略本載入器】
        目的：把知識庫資料夾 (knowledge) 裡面的所有攻略（如：MBTI分析.txt）讀進來。
        """
        # 如果快取裡有資料，直接回傳，不要浪費力氣讀硬碟
        if cls._knowledge_cache: return cls._knowledge_cache

        knowledge_dir = "knowledge" # 規定攻略本要放在這個資料夾
        data = {}
        print(f"   [系統] 正在載入本地知識庫...")
        
        # 安全檢查：萬一你忘了建立資料夾，程式才不會直接崩潰
        if not os.path.exists(knowledge_dir):
            print(f"   [警告] 找不到資料夾，請建立名為 {knowledge_dir} 的資料夾！")
            return {}

        try:
            # os.listdir：列出資料夾內所有的檔案名稱
            for filename in os.listdir(knowledge_dir):
                if filename.endswith(".txt"): # 我們只要文字檔
                    filepath = os.path.join(knowledge_dir, filename) # 組合路徑
                    # encoding="utf-8"：這是中文字才不會變亂碼的關鍵！
                    with open(filepath, "r", encoding="utf-8") as f:
                        key = filename.replace(".txt", "") # 用「檔名」當作查詢關鍵字
                        data[key] = f.read() # 把整本書的內容讀進來
                        print(f"   -> 已載入攻略: {filename}")
            
            cls._knowledge_cache = data # 存入大腦快取
            return data
        except Exception as e:
            # 這是「安全網」：萬一檔案壞了，印出原因，不要讓整個 AI 停掉
            print(f"   [錯誤] 讀取攻略本失敗: {e}")
            return {}

    @staticmethod
    def search_web(query):
        """
        工具 2：【聯網搜尋器】
        目的：當本地攻略本沒寫時，直接上網抓最新的資訊。
        """
        print(f"   [工具] 搜尋網路: {query}...")
        try:
            with DDGS() as ddgs:
                # 抓取前 3 筆，因為 AI 一次讀太多會「分心」
                results = list(ddgs.text(keywords=query, region='tw-tw', max_results=3))
            if not results: return "【系統提示】網路上也查不到相關資料。"
            
            # 使用「列表推導式」把標題跟內容結合成漂亮的一段話
            return "\n".join([f"- {res['title']}: {res['body']}" for res in results])
        except Exception as e:
            return f"【系統提示】網路連線故障: {e}"

    @staticmethod
    def search_love_strategy(query):
        """
        工具 3：【智慧檢索邏輯】
        策略：本地有資料就用本地的（比較準且省錢），本地沒有才上網搜尋。
        """
        try:
            kb = LoveTools.load_knowledge_base()
            
            # 如果連資料夾都沒有，直接去搜尋
            if not kb: return LoveTools.search_web(query)

            results = []
            for category, content in kb.items():
                # 簡單的關鍵字比對：如果 query 是「天蠍座」，而攻略本裡有這三個字
                if category in query.lower() or query in content:
                    results.append(f"【{category} 檔案】\n{content[:800]}...")

            if results:
                return "\n\n".join(results)
            else:
                # 本地搜不到，觸發聯網搜尋
                return LoveTools.search_web(query)
        except Exception as e:
            return f"查詢過程中發生錯誤: {e}"

    @staticmethod
    def calculate_interest_score(text):
        """
        工具 4：【情感演算法 (打分機制)】
        邏輯：透過關鍵字加減分，模擬人類的判斷。
        """
        try:
            score = 60 # 初始印象分：及格
            details = []
            
            # 心理學概念：鏡像行為 (Mirroring)
            # 如果對方說要去洗澡，你也說我也要，這是一種同步感，加分！
            is_mirroring = "洗澡" in text and any(x in text for x in ["我也", "一起", "都"])
            
            # 【大加分項】
            if any(x in text for x in ["要不要", "有空", "約"]) and any(y in text for y in ["出去", "吃飯"]):
                score += 40
                details.append("🔥🔥 偵測到約會邀請 (+40)")

            # 【負向情緒詞庫】
            negative_keywords = {"嗯嗯": -15, "哈哈": -5, "是喔": -15, "先忙": -20, "洗澡": -15}
            # 【正向情緒詞庫】
            positive_keywords = {"你呢": 15, "下次": 20, "想去": 20, "好奇": 15, "好啊": 10}

            # 開始逐詞檢查
            for w, point in negative_keywords.items():
                if w in text:
                    if "洗澡" in w and is_mirroring: continue # 鏡像行為時，洗澡不扣分
                    score += point 
                    details.append(f"扣分詞 '{w}'")

            for w, point in positive_keywords.items():
                if w in text:
                    score += point
                    details.append(f"加分詞 '{w}'")
            
            if is_mirroring:
                score += 20
                details.append("🛁 鏡像行為同步中 (+20)")

            # 用 max/min 確保分數不會超過 100 或是低於 0
            score = max(0, min(100, score))
            return f"好感度分數: {score} (原因: {', '.join(details)})"
        except Exception as e:
            return f"評分系統出錯: {e}"

    @staticmethod
    def sync_to_google_calendar(title, start_time, duration="1h"):
        """
        工具 5：【自動行程管理】
        這是一個『真實』的連線流程，會用到 OAuth 2.0 協議。
        """
        # 1. 定義權限：我們需要「讀取與寫入」行事曆的權限
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = None
        
        # 2. 尋找鑰匙：
        # token.json 就像是你的「長期識別證」，有了它就不用每次都重新登入
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # 3. 處理過期或沒登入的情況：
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request()) # 識別證過期了，拿舊的去換新的
            else:
                # 第一次使用，必須要有 credentials.json (就像是公司的授權書)
                if not os.path.exists('credentials.json'):
                    return "❌ 請先去 Google Cloud 控制台下載 credentials.json 並放到程式資料夾中。"
                
                # 彈出瀏覽器視窗，讓你點擊「授權」
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 把拿到的識別證存起來，下次就不用再開瀏覽器了
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # 召喚工人 (service)，準備開始工作
            service = build('calendar', 'v3', credentials=creds)

            # 4. 時間處理 (新手最常卡關的地方)：
            # 電腦只認識標準格式 (ISO Format)，AI 給的通常不標準，我們要修復它。
            try:
                start_dt = datetime.datetime.fromisoformat(start_time)
            except ValueError:
                # 補上缺少的資訊（例如：AI 忘了加秒數，或者中間是空格不是 T）
                formatted_time = start_time.replace(" ", "T")
                if len(formatted_time.split(":")) == 2: formatted_time += ":00"
                start_dt = datetime.datetime.fromisoformat(formatted_time)

            # 加上持續時間（預設一小時）
            hours_to_add = int(duration.replace("h", "")) if "h" in duration else 1
            end_dt = start_dt + datetime.timedelta(hours=hours_to_add)

            # 5. 填寫包裹 (Event 物件)：
            # 這是 Google 規定的固定格式，不能亂改
            event = {
                'summary': title,
                'description': '💖 您的戀愛軍師為您精心安排的行程 💖',
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Asia/Taipei', # 時區一定要設對，不然會差 8 小時！
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Asia/Taipei',
                },
            }

            # 6. 送出包裹到 Google：
            # .execute() 才是真正發送請求的那一刻
            event_result = service.events().insert(calendarId='primary', body=event).execute()
            
            # 回傳生成的行事曆連結給使用者
            return f"✅ 行程安排成功！\n名稱：{title}\n連結：{event_result.get('htmlLink')}"

        except Exception as e:
            return f"Google Calendar 同步失敗，請確認 API 權限: {e}"