# agent_core.py
import requests
import json
import re # 新增 re 模組來增強 JSON 提取能力
from config import API_KEY, API_URL, MODEL_NAME, TIMEOUT
from tools import LoveTools

class LoveAgent:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # ▼▼▼ 修改 System Prompt：加入範例 (Few-Shot) 與 禁止事項 ▼▼▼
        self.system_prompt = """
        你是一個「工具調度員」。你的唯一工作是判斷使用者的需求，並回傳對應的 JSON 工具指令。

        【嚴格規則】
        1. **禁止回答問題**：在取得工具結果前，不要嘗試回答使用者。
        2. **禁止包裹 JSON**：不要把 JSON 放在 "response" 或其他欄位裡。直接回傳工具 JSON。
        3. **星座名稱**：必須使用全名 (如「天蠍座」)，禁止簡稱。

        【正確範例 (Correct Example)】
        User: 怎麼追天蠍座？
        Assistant: {"tool": "search_strategy", "arg": "天蠍座 追求攻略"}

        User: 我是 INFP
        Assistant: {"tool": "analyze_mbti", "arg": "INFP"}

        【錯誤範例 (Wrong Example)】
        User: 怎麼追天蠍座？
        Assistant: { "response": "天蠍座很難追...可以使用這個工具 {"tool":...} " }  <-- ❌ 絕對禁止這種格式

        【工具清單】
        1. 查攻略/星座/術語 -> {"tool": "search_strategy", "arg": "關鍵字"}
        2. 查 MBTI (限英文代碼) -> {"tool": "analyze_mbti", "arg": "MBTI代碼"}
        3. 分析好感度 -> {"tool": "calculate_score", "arg": "對話內容"}
        4. 搜尋地點 -> {"tool": "search_web", "arg": "地點"}
        5. 生成風格 -> {"tool": "get_reply_styles", "arg": "情境"}
        6. 安排行程 -> {"tool": "schedule_itinerary", "itinerary": [{"time": "HH:MM", "title": "行程"}]}
        """
        self.history = [{"role": "system", "content": self.system_prompt}]

    def reset(self):
        self.history = [{"role": "system", "content": self.system_prompt}]
        return "🧹 記憶已清除，我們重新開始吧！"

    def _call_llm(self, messages):
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
            "temperature": 0.1 # 保持極低溫，確保格式正確
        }
        try:
            res = requests.post(API_URL, headers=self.headers, json=payload, timeout=TIMEOUT)
            if res.status_code == 200:
                return res.json()['message']['content']
            else:
                return f"Error: {res.status_code} - {res.text}"
        except Exception as e:
            return f"連線失敗: {e}"

    # ▼▼▼ 增強版 JSON 提取器：即使 AI 亂包也能抓出來 ▼▼▼
    def _extract_json(self, text):
        try:
            # 1. 先嘗試標準清洗
            cleaned = text.replace("```json", "").replace("```", "").strip()
            
            # 2. 如果整串就是一個 JSON (最理想情況)
            try:
                return json.loads(cleaned)
            except:
                pass
            
            # 3. 如果失敗，使用正規表達式 (Regex) 去抓取 "tool": "..." 這種結構
            # 這能解決 AI 把 JSON 藏在文字海裡的問題
            match = re.search(r'\{.*"tool"\s*:\s*".*?".*\}', cleaned, re.DOTALL)
            if match:
                potential_json = match.group(0)
                return json.loads(potential_json)
                
        except: pass
        return None

    def chat(self, user_input):
        # 人工干預層 (Hard Trigger)
        # 如果使用者問了關鍵字，我們直接「洗腦」LLM，叫它閉嘴只准出工具
        force_tool_prompt = ""
        rag_keywords = ["星座", "怎麼追", "合不來", "效應", "理論", "麵包屑", "人類圖", "分析"]
        
        if any(k in user_input for k in rag_keywords):
            force_tool_prompt = "\n(系統提示：偵測到專業術語，請務必使用 search_strategy，嚴禁直接回答！)"
        
        self.history.append({"role": "user", "content": user_input + force_tool_prompt})
        
        # 第一階段：思考工具
        response_text = self._call_llm(self.history)
        print(f"🧐 [Debug] LLM 原始回覆: {response_text}") 
        
        cmd = self._extract_json(response_text)
        schedules_list = [] 
        
        # 檢查是否成功抓到 tool 指令
        if cmd and "tool" in cmd:
            tool_name = cmd["tool"]
            arg = cmd.get("arg")
            print(f"🔧 [Debug] 捕捉到工具: {tool_name}, 參數: {arg}")

            tool_result = ""
            
            if tool_name == "search_strategy":
                # ▼▼▼ 新增：搜尋關鍵字自動清洗邏輯 ▼▼▼
                # 如果 arg 包含多個字，我們只抓取核心關鍵字來提高 RAG 命中率
                keywords_map = ["麵包屑", "富蘭克林", "依附理論", "人類圖", "星座", "天蠍", "處女", "射手"]
                clean_arg = arg
                
                # 檢查 arg 裡面有沒有包含我們知識庫裡的重點詞彙
                for key in keywords_map:
                    if key in arg:
                        clean_arg = key # 強制將搜尋詞縮小為核心詞
                        break
                print(f"🔎 [RAG 優化] 原參數: {arg} -> 清洗後: {clean_arg}")
                tool_result = LoveTools.search_love_strategy(clean_arg)
            elif tool_name == "analyze_mbti":
                tool_result = LoveTools.get_personality_analysis(arg)
            elif tool_name == "calculate_score":
                tool_result = LoveTools.calculate_interest_score(arg)
            elif tool_name == "search_web":
                tool_result = LoveTools.search_web(arg)
            elif tool_name == "get_reply_styles":
                tool_result = LoveTools.generate_reply_styles(arg)
            elif tool_name == "schedule_itinerary":
                items = cmd.get("itinerary", [])
                if not items and "arg" in cmd: items = cmd["arg"]
                if isinstance(items, list):
                    schedules_list = items
                    tool_result = "【系統】行程物件已生成。"
                else:
                    if isinstance(items, dict): schedules_list = [items]
                    tool_result = "【系統】單一行程已生成。"

            # 記錄第一階段 (雖然可能格式不完美，但為了讓對話連貫還是記下來)
            self.history.append({"role": "assistant", "content": response_text})
            
            # ▼▼▼ 第二階段：強制轉回中文回答模式 ▼▼▼
            follow_up_prompt = f"""
            【系統回報】工具搜尋結果如下：
            {tool_result}
            
            ⚠️ 指令：
            1. 請根據搜尋結果，整理成通順的「繁體中文」回答。
            2. 星座請使用全名 (如天蠍座)。
            3. **禁止再輸出 JSON！現在請像個真人戀愛軍師一樣說話。**
            """
            self.history.append({"role": "user", "content": follow_up_prompt})
            
            final_response = self._call_llm(self.history)
            self.history.append({"role": "assistant", "content": final_response})
            
            return { "reply": final_response, "schedules": schedules_list }
        
        else:
            # 如果還是失敗，嘗試最後一次挽救 (假設 AI 已經在 response_text 裡回答了)
            # 但通常我們會希望它用工具。
            print("⚠️ [Debug] 未偵測到工具指令，直接回覆。")
            self.history.append({"role": "assistant", "content": response_text})
            
            # 如果 response_text 是一大串 JSON 字串，我們試著只回傳裡面的文字內容給使用者看
            # 避免使用者看到赤裸裸的 JSON
            if response_text.strip().startswith("{") and "response" in response_text:
                 try:
                     fallback_json = json.loads(response_text)
                     if "response" in fallback_json:
                         return { "reply": fallback_json["response"], "schedules": [] }
                 except: pass

            return { "reply": response_text, "schedules": [] }