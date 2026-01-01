import os
import glob
from duckduckgo_search import DDGS

class LoveTools:
    
    # 設定知識庫資料夾路徑
    KNOWLEDGE_DIR = "knowledge"

    @staticmethod
    def _read_all_knowledge_files():
        """內部工具：讀取所有 txt 檔案內容"""
        all_content = {}
        
        # 確保資料夾存在
        if not os.path.exists(LoveTools.KNOWLEDGE_DIR):
            print(f"⚠️ 警告：找不到 {LoveTools.KNOWLEDGE_DIR} 資料夾")
            return {}

        # 抓取所有 .txt 檔案
        files = glob.glob(os.path.join(LoveTools.KNOWLEDGE_DIR, "*.txt"))
        
        for file_path in files:
            try:
                # 使用 utf-8 編碼讀取，忽略錯誤字元
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    filename = os.path.basename(file_path)
                    all_content[filename] = f.read()
            except Exception as e:
                print(f"❌ 讀取檔案 {file_path} 失敗: {e}")
        
        return all_content

    @staticmethod
    def search_web(query):
        """工具：聯網搜尋 (當本地資料庫找不到時使用)"""
        print(f"   [工具執行] 正在搜尋網路: {query}...")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(keywords=query, region='tw-tw', max_results=3))
            
            if not results: 
                return "【系統提示】網路搜尋無結果，請嘗試用你的內建常識回答。"
            
            summary = ""
            for res in results:
                summary += f"- {res['title']}: {res['body']}\n"
            return summary
        except Exception as e:
            return f"搜尋錯誤: {e}"

    @staticmethod
    def search_love_strategy(query):
        """
        工具：RAG 核心 (寬容搜尋版)
        """
        print(f"   [工具執行] 正在檢索 RAG 知識庫: {query}...")
        
        knowledge_base = LoveTools._read_all_knowledge_files()
        results = []
        
        # 1. 轉小寫並斷詞
        query_lower = query.lower()
        keywords = query_lower.split() # 例如 "金牛座 性格" -> ["金牛座", "性格"]
        
        for filename, content in knowledge_base.items():
            content_lower = content.lower()
            
            # A. 絕對匹配 (如果整句都在裡面)
            if query_lower in content_lower:
                results.append(f"【來源：{filename}】\n{content}\n")
                continue

            # B. 模糊匹配 (只要有一半的關鍵字出現就算)
            if not keywords: continue
            
            # 計算命中幾個關鍵字
            match_count = sum(1 for k in keywords if k in content_lower)
            
            # 只要命中 > 0 且關鍵字長度 > 1 (避免命中 'a' 這種無意義字)，就抓進來
            if match_count > 0:
                 # 為了保險，我們可以檢查是否命中主要關鍵字
                 results.append(f"【來源：{filename}】(模糊匹配)\n{content}\n")

        if results:
            final_output = "\n====================\n".join(results)
            # 截斷過長的內容 (Gemma 4b 上限約 2-3k token)
            return final_output[:3000] 
        else:
            print("   [知識庫] 本地無資料，轉為網路搜尋...")
            return LoveTools.search_web(query)

    @staticmethod
    def get_personality_analysis(mbti_type):
        """
        工具：MBTI 專用查詢
        功能：從 mbti.txt 中精準提取特定人格的段落
        """
        print(f"   [工具執行] 查詢 MBTI 檔案: {mbti_type}...")
        
        mbti_type = mbti_type.upper() # 轉大寫
        file_path = os.path.join(LoveTools.KNOWLEDGE_DIR, "mbti.txt")
        
        if not os.path.exists(file_path):
            return "【系統錯誤】找不到 mbti.txt，請確認資料夾。"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 使用我們設定的格式 "【MBTI：XXXX" 進行切割
            target_header = f"MBTI：{mbti_type}"
            
            # 將文本依據 "【" 切割成區塊
            sections = content.split("【")
            
            for section in sections:
                if target_header in section:
                    return f"【MBTI 分析結果】\n{section.strip()}"
            
            return f"查無此人格類型 ({mbti_type})，請確認代碼是否正確。"
            
        except Exception as e:
            return f"讀取 MBTI 檔案錯誤: {e}"

    @staticmethod
    def calculate_interest_score(text):
        """工具：暈船計算機 (權重版)"""
        print(f"   [工具執行] 計算好感度: {text}...")
        score = 60 
        details = []
        
        # 這裡的關鍵字也可以移到 txt，但為了運算速度，保留在程式碼中較佳
        keywords_map = {
            "滾": -50, "不想": -30, "沒感覺": -40, "噁心": -50, "變態": -50,
            "洗澡": -15, "先睡": -10, "呵呵": -15, "嗯嗯": -5, "哈哈": -5, "再說": -10, "閱": -10,
            "你呢": +10, "笑死": +5, "好奇": +10, "想去": +15, "笨蛋": +15,
            "想你": +30, "可愛": +25, "一起": +20, "愛": +40, "❤️": +20, "早安": +10, "晚安": +10
        }

        for word, points in keywords_map.items():
            if word in text:
                score += points
                type_str = "加分" if points > 0 else "扣分"
                details.append(f"{type_str}詞 '{word}'")

        score = max(0, min(100, score))
        
        if score >= 80: status = "😍 穩了！對方想跟你發展"
        elif score >= 50: status = "😐 普通朋友/觀察區"
        else: status = "🥶 沒救了/下一個會更好"

        return f"分數: {score}\n狀態: {status}\n分析細節: {', '.join(details) if details else '無明顯關鍵字'}"

    @staticmethod
    def generate_reply_styles(scenario):
        """工具：風格回覆產生器"""
        return f"""
        【指令執行】
        使用者遇到了這個對話情境：{scenario}
        請立即生成三種不同風格的回覆建議：
        1. 🥶 **高冷版 (High Value)**：簡短、自信、不卑不亢。
        2. 😂 **幽默版 (Funny)**：用開玩笑化解尷尬。
        3. 🐶 **暖男/貼心版 (Warm)**：溫柔體貼，展現關懷。
        """