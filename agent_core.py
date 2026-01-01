# 標準庫：Python 內建的功能
import requests  # 用於發送網路請求，這是跟LLM API溝通的傳聲筒
import json      # 用於處理 JSON 格式, 因為 AI 輸出的結果和我們存的檔案都是 JSON
import ast       # 「抽象語法樹」，這裡用來將字串轉成 Python 字典，當 json.loads 失敗時的備用方案
import time      # 用於處理時間，例如 API 報錯時，讓程式過兩秒再重試
import re        # 「正規表示式」，用於搜尋、過濾字串（檢查是否有 MBTI 的四個英文字母）

# 本地模組，負責處理特定寫好的任務
from config import API_KEY, API_URL, MODEL_NAME, TIMEOUT  # 從設定檔讀取密鑰與 URL，避免密鑰直接寫死在程式碼裡
from tools import LoveTools                              # 工具箱，包含 Google 日曆、網頁搜尋、好感度計算等實作
from relationship_manager import RelationshipManager      # 檔案管理員，負責去讀取和寫入人物資料的 JSON 檔

class LoveAgent:
    def __init__(self):
        # 設定 API Header，用於身分驗證
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        # 初始化關係管理器 (負責存取 JSON 檔案中的人物設定)
        self.rm = RelationshipManager()
        # 紀錄當前正在聊天的對象，結合上下文，避免使用者一直重複名字
        self.current_topic_person = None 
        
        # 階段 1: 工具判斷專用的 System Prompt
        # 這個 Prompt 的目的是讓 AI 變成一個「分類器」
        # 強制 AI 輸出 JSON 格式，決定要呼叫哪個工具
        self.tool_selector_prompt = """
        You are a function calling intent detector. 
        Your ONLY job is to analyze the user's input and output a JSON object to call a tool.
        
        IMPORTANT: Output strictly valid JSON.
        
        Tools & Rules:
        1. **Save Person Info**: {"tool": "save_profile", "arg": {"name": "Name", "info": {...}}}
        2. **Delete Person**: {"tool": "delete_profile", "arg": "Name"}
        3. **Search Strategy**: {"tool": "search_strategy", "arg": "Noun"}
        4. **Analyze Chat**: {"tool": "calculate_score", "arg": "Chat Content"}
        5. **Reply Help**: {"tool": "get_reply_styles", "arg": "Situation"}
        6. **Search Web**: {"tool": "search_web", "arg": "Query"}
        
        7. **Plan Itinerary (Generate Plan)**:
           - User asks to plan a date/schedule.
           - Tool: "schedule_itinerary"
           - Arg: List of dictionary [{"time": "HH:MM", "title": "Activity"}]
           - Example: User "Plan a date at Tamsui" -> {"tool": "schedule_itinerary", "arg": [{"time": "14:00", "title": "Meet at MRT"}, {"time": "16:00", "title": "Sunset watch"}]}

        8. **Save to Calendar (Execute Save)**:
           - User says: "Yes", "Ok", "save it", "幫我存", "加入行事曆", "設定", "記下來", "好啊".
           - **CRITICAL**: You must extract the Date/Time/Title from the **Previous Context** (Assistant's suggestion).
           - Tool: "create_event"
           - Arg: {"title": "Summary", "start": "YYYY-MM-DDTHH:MM", "duration": "xh"}
           - Note: Convert relative time (Next Friday 7pm) to ISO format (e.g., 2026-01-16T19:00). Assume current year is 2026.
           
        9. **No Tool Needed**: {"tool": "none", "arg": ""}
        """

        # 階段 2: 戀愛軍師 System Prompt (Persona / Chatbot)
        # 這是 AI 的主要人格設定，負責產生最終回應
        # 包含了「RAG 檢索指示」和「人設語氣」。
        self.main_system_prompt = """
        你是一位專業、犀利但情商極高的「戀愛軍師 AI」。你的任務是協助使用者解決戀愛煩惱。
        
        【重要：記憶庫使用指示】
        系統會將「目前話題對象」的資料（星座、MBTI、喜好）提供給你。
        1. **不要明知故問**：如果資料庫已經顯示對方是 "ENFP" 或 "雙子座"，請直接根據這些特質進行分析，**絕對不要再反問**使用者「他是什麼星座？」或「有測過MBTI嗎？」。
        2. **喜好整合**：如果資料顯示對方「喜歡看海」或「討厭蟲子」，安排行程時請務必避開地雷並投其所好。

        【最高指導原則】
        1. **絕對不要暴露工具失誤**：如果工具回傳「無結果」，請直接用你的內建知識回答。
        2. **語氣**：保持自信、幽默、像是神秘情場高手的對話。

        【人設指導原則】
        1. **判斷邀約**：如果對話中包含對方主動約，這是極好的訊號。
        2. **處理「拒絕」情境**：教導使用「三明治拒絕法」（感謝 -> 拒絕 -> 替代方案）。
        3. **毒舌但不白目**：對使用者毒舌（罵醒），對曖昧對象尊重。
        
        【回應格式】
        請直接輸出建議內容，不要顯示 JSON 或「工具建議」。
        """
        
        # 初始化對話歷史，讓第一條永遠是 System Prompt
        self.history = [{"role": "system", "content": self.main_system_prompt}]

    def reset(self):
        """清空對話紀錄 (保留 System Prompt)"""
        self.history = [{"role": "system", "content": self.main_system_prompt}]
        self.current_topic_person = None 
        return "🧹 記憶已清除，我們重新開始吧！"
    
    # 控制創意度(temperature)：0.7 (聊天/創作用)
    def _call_api(self, messages, temperature=0.7):
        """
        呼叫 LLM API 的底層函式。
        支援 Retry 機制與多種 API 回傳格式相容性處理。
        """
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
            "temperature": temperature
        }
        
        # 重新嘗試的次數為3
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 設定 Timeout 防止請求卡死
                res = requests.post(API_URL, headers=self.headers, json=payload, timeout=TIMEOUT)
                
                # 200 代表 OK
                if res.status_code == 200:
                    data = res.json()
                    
                    # 相容性處理 (針對不同模型後端)
                    # 情況 1: 標準 OpenAI 格式
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                    # 情況 2: Ollama格式
                    if "message" in data:
                        return data["message"]["content"]
                    if "response" in data:
                        return data["response"]
                    if "content" in data:
                        return data["content"]
                    
                    print(f"⚠️ API 回傳格式不明 (Status 200): {data}")
                    return None
                else:
                    print(f"⚠️ API Error (Status {res.status_code}): {res.text}")
            
            except requests.exceptions.Timeout:
                print(f"⏳ 連線逾時 (嘗試 {attempt+1}/{max_retries})...")
            except Exception as e:
                print(f"❌ 連線例外 (嘗試 {attempt+1}/{max_retries}): {e}")
            
            # 失敗後等待 2 秒再重試
            if attempt < max_retries - 1:
                time.sleep(2)

        print("💀 重試失敗，放棄連線。")
        return None

    def _detect_intent_and_run_tool(self, user_input):
        """
        【大腦核心】意圖偵測與工具執行
        1. 傳送 User Input 給 LLM (使用 Tool Prompt)。
        2. 解析 LLM 回傳的 JSON。
        3. 執行對應的 Python 函式 (tools.py)。
        """
        
        # 輔助函式：防止 LLM 回傳 Markdown 格式導致解析失敗
        def try_parse_json(text):
            cleaned = text.replace("```json", "").replace("```", "").strip()
            # 嘗試用標準 JSON 格式來解析
            try: return json.loads(cleaned)  # 嘗試把字串轉成字典。
            except: pass  # 如果失敗了，直接跳過並執行下一行。
            # 嘗試用 Python 語法格式來解析
            # ast.literal_eval 能處理單引號或是 Python 原生的資料格式
            try: return ast.literal_eval(cleaned) 
            except: pass  # 如果還是失敗了，一樣不報錯。
            # 如果全都失敗了，就直接返回 None
            return None

        # 輔助函式：清理使用者輸入的資料 (標準化 MBTI、星座名稱)
        def sanitize_info(info_dict):
            cleaned_info = {}
            for k, v in info_dict.items():
                value_str = str(v).strip()
                new_key = k 
                if "座" in value_str: new_key = "星座"
                elif re.match(r"^[A-Za-z]{4}$", value_str): new_key = "MBTI"; value_str = value_str.upper()
                if value_str == "蠍座": value_str = "天蠍座"
                cleaned_info[new_key] = value_str
            return cleaned_info

        # 上下文注入
        # 讓Calendar功能生效
        # 使用者只說「好，幫我存」，AI 必須看到「上一句」才知道要存什麼行程。
        recent_context = ""
        if len(self.history) > 1:
            last_msg = self.history[-1]
            if last_msg['role'] == 'assistant':
                recent_context = f"Context (Assistant's Proposal): {last_msg['content']}"

        selector_messages = [
            {"role": "system", "content": self.tool_selector_prompt},
            {"role": "user", "content": f"{recent_context}\nUser Current Input: {user_input}"}
        ]
        
        print("🕵️ [系統] 正在判斷意圖...")
        # 控制創意度(temperature) ：0.1 (精準/工具用)
        response = self._call_api(selector_messages, temperature=0.1)
        if not response: return None
        
        cmd = try_parse_json(response)
        if not cmd: return None

        try:
            tool_name = cmd.get("tool")
            arg = cmd.get("arg")

            if tool_name and tool_name != "none":
                
                # 工具 1: 儲存人物資料
                if tool_name == "save_profile":
                    data = arg
                    # 1. 檢查 arg 是不是一個「字串」？
                    # AI 有時候會把 JSON 內容包在引號裡面變成一長串文字，而不是直接給我們結構化資料
                    if isinstance(arg, str): 
                        
                        # 2. 如果是字串，就呼叫我們之前寫好的「防禦性解析」功能 (try_parse_json)
                        # 試圖把這串「長得像 JSON 的文字」轉成真正的「Python 字典」
                        parsed = try_parse_json(arg)
                        
                        # 3. 如果解析成功了（parsed 不是 None）
                        if parsed: 
                            # 4. 就把解析後的成果 (字典) 覆蓋掉原本的字串資料
                            # 這樣後面的程式碼就能開心地用 data["name"] 這種方式來讀取資料了
                            data = parsed
                    
                    if isinstance(data, dict) and "name" in data:
                        raw_name = data["name"]
                        raw_info = data.get("info", {})
                        
                        # 代名詞解析
                        # 「她喜歡吃蘋果」，系統要把「她」替換成「MuQ醬」
                        pronouns = ["他", "她", "它", "你", "我", "祂", "He", "She", "It", "You"]
                        if raw_name in pronouns:
                            if self.current_topic_person:
                                print(f"🔄 [代名詞修正] '{raw_name}' -> '{self.current_topic_person}'")
                                raw_name = self.current_topic_person
                            else:
                                return "系統提示：請先告知對象名字，我才能存檔喔。"
                        else:
                            self.current_topic_person = raw_name # 更新話題焦點
                            print(f"📌 [鎖定對象] {self.current_topic_person}")

                        final_info = sanitize_info(raw_info)
                        print(f"🔧 [觸發工具] save_profile | {raw_name} : {final_info}")
                        return self.rm.save_person(raw_name, final_info)
                    
                # 工具 2: 刪除資料
                elif tool_name == "delete_profile":
                    if arg == self.current_topic_person: self.current_topic_person = None
                    return self.rm.delete_person(arg)
                
                # 工具 3-6: 查詢與計算
                elif tool_name == "search_strategy": return LoveTools.search_love_strategy(arg)
                elif tool_name == "calculate_score": return LoveTools.calculate_interest_score(arg)
                elif tool_name == "get_reply_styles": return LoveTools.generate_reply_styles(arg)
                elif tool_name == "search_web": return LoveTools.search_web(arg)

                # 工具 7: 行程規劃 (生成建議)
                elif tool_name == "schedule_itinerary":
                    items = arg
                    plan_text = ""
                    if isinstance(items, list):
                        for i in items:
                            plan_text += f"- {i.get('time', '時間未定')}: {i.get('title', '活動')}\n"
                    # 回傳系統提示，讓 Main LLM 主動去問使用者要不要存檔
                    return f"【行程規劃建議】\n{plan_text}\n(系統提示：請軍師根據此行程給予建議，並主動詢問使用者『是否要將此行程同步到 Google Calendar？』)"

                # 工具 8: Google Calendar (執行存檔)
                elif tool_name == "create_event":
                    # arg 預期格式: {"title": "...", "start": "...", "duration": "..."}
                    if isinstance(arg, dict):
                        title = arg.get("title", "約會行程")
                        start = arg.get("start", "2026-01-01T00:00") 
                        duration = arg.get("duration", "2h")
                        # 呼叫 tools.py 裡的真實 API
                        return LoveTools.sync_to_google_calendar(title, start, duration)
                    else:
                        return "系統錯誤：Calendar 參數格式不正確。"
            
            return None 
        except Exception as e:
            return f"系統錯誤: {e}"

    def _check_and_load_profile(self, user_input):
        """
        RAG 檢索邏輯：主動載入話題人物資料。
        如果使用者提到「MuQ醬」，就去 JSON 讀取她的 MBTI 和星座。
        """
        known_names = self.rm.get_all_names()
        found_data = ""
        
        # 檢查 Input 裡有沒有出現已知的名字
        for name in known_names:
            if name in user_input:
                self.current_topic_person = name
                break
        
        # 如果有鎖定對象，就載入資料
        if self.current_topic_person:
            profile = self.rm.get_person(self.current_topic_person)
            if profile:
                found_data = f"【當前話題對象：{self.current_topic_person}】\n{json.dumps(profile, ensure_ascii=False)}\n"
                print(f"📖 [記憶載入] {self.current_topic_person}")
        
        return found_data

    def chat(self, user_input):
        """主對話迴圈"""
        
        # 步驟 1. 先執行工具
        # 如果工具執行了 (例如查詢星座攻略)，結果會存在 tool_result
        tool_result = self._detect_intent_and_run_tool(user_input)

        # 步驟 2. 載入人物記憶
        profile_context = self._check_and_load_profile(user_input)

        # 步驟 3. 組合 Prompt
        self.history.append({"role": "user", "content": user_input})
        current_messages = self.history.copy()
        
        # 準備要喂給 AI 的系統提示
        system_hint = ""
        
        if tool_result: 
            # 把工具查到的結果餵給 AI
            system_hint += f"【系統背景執行報告】{tool_result}\n(請忽略回報訊息，直接針對使用者的 Input 回答)\n"
        
        if profile_context: 
            # 把人物設定餵給 AI
            system_hint += f"【資料庫人物檔案】(請依此個性與喜好分析)\n{profile_context}\n"
            
        if system_hint:
            # 將這些背景資訊插入在倒數第二句 (在 User Input 之前)
            current_messages.insert(-1, {"role": "system", "content": system_hint})

        print("🤖 [軍師思考中]...")
        # 步驟 4. 產生最終回覆 (使用 temperature=0.7 讓回答生動有趣)
        ai_reply = self._call_api(current_messages, temperature=0.7)
        
        if ai_reply:
            self.history.append({"role": "assistant", "content": ai_reply})
            return ai_reply
        else:
            return "軍師斷線中..."