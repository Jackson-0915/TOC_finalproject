# agent_core.py
import requests
import json
from config import API_KEY, API_URL, MODEL_NAME, TIMEOUT
from tools import LoveTools

class LoveAgent:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        # ▼▼▼ 1. 修改 System Prompt：加入 MBTI 與 多重行程 的指令 ▼▼▼
        self.system_prompt = """
        你是一位專業的「戀愛軍師 AI」。你的任務是協助使用者解決戀愛煩惱。
        
        【最高指導原則】
        1. **人設**：自信、幽默的大學生朋友，不要說教。
        2. **知識運用**：
           - 遇到「攻略、理論、星座、怎麼追」的問題，請務必呼叫 `search_strategy` 查詢知識庫。
           - 遇到「人格分析、我是什麼人」的問題，請呼叫 `analyze_mbti`。
        3. **隱藏失誤**：如果工具回傳查無資料，請直接用你自己的常識回答，不要報錯。

        【工具指令表】
        1. 查詢攻略/星座/理論/聊天話題 -> {"tool": "search_strategy", "arg": "關鍵字"}
        2. 分析對話好感度 -> {"tool": "calculate_score", "arg": "對話內容"}
        3. 查詢 MBTI 人格 -> {"tool": "analyze_mbti", "arg": "4個字母代碼"} (如 INFP)
        4. 搜尋地點/餐廳 -> {"tool": "search_web", "arg": "地點關鍵字"}
        5. 生成回覆風格 -> {"tool": "get_reply_styles", "arg": "情境描述"}
        6. **安排約會/行程** -> {"tool": "schedule_itinerary", "itinerary": [{"time": "HH:MM", "title": "行程1"}, {"time": "HH:MM", "title": "行程2"}]}
        
        【回應格式】
        請輸出 JSON 格式呼叫工具。若無需工具，直接回覆文字。
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
            "temperature": 0.3
        }
        try:
            res = requests.post(API_URL, headers=self.headers, json=payload, timeout=TIMEOUT)
            if res.status_code == 200:
                return res.json()['message']['content']
            else:
                return f"Error: {res.status_code} - {res.text}"
        except Exception as e:
            return f"連線失敗: {e}"

    def _extract_json(self, text):
        try:
            cleaned = text.replace("```json", "").replace("```", "").strip()
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start != -1 and end != -1:
                return json.loads(cleaned[start:end+1])
        except: pass
        return None

    def chat(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        response_text = self._call_llm(self.history)
        
        cmd = self._extract_json(response_text)
        
        # ▼▼▼ 2. 準備行程列表 (原本是單一變數，現在改 List) ▼▼▼
        schedules_list = [] 
        
        if cmd and "tool" in cmd:
            tool_name = cmd["tool"]
            arg = cmd.get("arg")
            tool_result = ""
            
            # --- 工具派發中心 ---
            if tool_name == "search_strategy":
                # 這裡會呼叫新版 tools.py 的 RAG 功能
                tool_result = LoveTools.search_love_strategy(arg)
            
            elif tool_name == "analyze_mbti":
                # 這裡呼叫 MBTI 專用分析
                tool_result = LoveTools.get_personality_analysis(arg)
            
            elif tool_name == "calculate_score":
                tool_result = LoveTools.calculate_interest_score(arg)
            
            elif tool_name == "search_web":
                tool_result = LoveTools.search_web(arg)
            
            elif tool_name == "get_reply_styles":
                tool_result = LoveTools.generate_reply_styles(arg)
            
            elif tool_name == "schedule_itinerary":
                # ▼▼▼ 3. 處理多重行程 (升級版邏輯) ▼▼▼
                # 嘗試抓取 itinerary 列表，如果沒有就抓 arg (容錯)
                items = cmd.get("itinerary", [])
                if not items and "arg" in cmd: items = cmd["arg"]

                if isinstance(items, list):
                    schedules_list = items
                    tool_result = "【系統】已生成行事曆連結物件，前端將自動渲染按鈕。請告知用戶行程已安排妥當。"
                else:
                    # 如果 LLM 還是只回傳單一物件，我們把它包成 list
                    if isinstance(items, dict):
                        schedules_list = [items]
                        tool_result = "【系統】已生成單一行程。"
                    else:
                        tool_result = "行程格式錯誤，請檢查 JSON。"
            
            # 把工具結果餵回給 LLM
            self.history.append({"role": "assistant", "content": response_text})
            self.history.append({"role": "user", "content": f"【系統回報】工具結果：\n{tool_result}"})
            
            final_response = self._call_llm(self.history)
            self.history.append({"role": "assistant", "content": final_response})
            
            # ▼▼▼ 4. 回傳字典結構 (注意 key 是 schedules) ▼▼▼
            return {
                "reply": final_response,
                "schedules": schedules_list # 回傳 List 給 server.py -> script.js
            }
        
        else:
            self.history.append({"role": "assistant", "content": response_text})
            return {
                "reply": response_text,
                "schedules": []
            }