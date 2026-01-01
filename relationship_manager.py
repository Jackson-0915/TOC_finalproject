import json  # 用於處理 JSON 格式的資料
import os    # 用於檢查檔案是否存在於電腦中

# 定義檔名，資料會存在這個 JSON 檔案
DB_FILE = "relationships.json"

class RelationshipManager:
    def __init__(self):
        """
        初始化：當這個管理器被啟動時，先確認筆記本是否存在。
        """
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        """
        【檢查機制】確保資料庫檔案存在。
        如果電腦裡還沒有這個檔案，就自動建立一個空的筆記本（內容是空的 {}）。
        """
        if not os.path.exists(DB_FILE):
            # 'w' 代表寫入模式，encoding="utf-8" 確保中文不會變成亂碼
            with open(DB_FILE, "w", encoding="utf-8") as f:
                # indent=4 是為了讓存出來的檔案排版漂亮，方便人類閱讀
                json.dump({}, f, ensure_ascii=False, indent=4)

    def _load_db(self):
        """
        【讀取功能】把硬碟裡的 JSON 檔案讀取進來，轉成 Python 的「字典 (Dictionary)」。
        """
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # 如果檔案壞掉了或找不到，就回傳一個空的字典
            return {}

    def _save_db(self, data):
        """
        【存檔功能】把記憶寫入硬碟。
        每當 AI 更新了某人的資料，我們就呼叫這個函式。
        """
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_person(self, name, attributes):
        """
        【核心功能】新增或更新某人的資料。
        name: 名字 (例如: MuQ醬)
        attributes: 特徵字典 (例如: {"MBTI": "ENFP", "喜好": "看海"})
        """
        # 1. 先把舊的記憶通通讀取出來
        data = self._load_db()
        
        # 2. 如果這個人是第一次出現，先幫他在字典裡開一個位子
        if name not in data:
            data[name] = {"info": {}}
        
        # 確保 info 層級存在
        if "info" not in data[name]:
            data[name]["info"] = {}

        # 3. 準備開始更新資料
        current_info = data[name]["info"] # 目前已有的資料
        new_info = attributes             # AI 這次想存的新資料

        # 4. 遍歷新資料的每一個項目 (Key)
        for key, value in new_info.items():
            # 【特殊邏輯】針對「喜好、討厭、地雷」進行「追加」
            # 例如：本來喜歡「看海」，新資料是「吃蘋果」，我們希望變成「看海、吃蘋果」
            if key in ["喜好", "討厭", "地雷"] and key in current_info:
                # 檢查這項喜好是不是已經記過了，沒記過才加進去
                if value not in current_info[key]:
                    current_info[key] = f"{current_info[key]}、{value}"
            else:
                # 其他欄位 (如星座、MBTI) 如果有變動，直接「覆蓋」成最新的
                current_info[key] = value
        
        # 5. 把更新完的個人檔案塞回總資料中
        data[name]["info"] = current_info
        
        # 6. 最後把整份總資料存進硬碟
        self._save_db(data)
        return f"已記錄/更新對象【{name}】的資料：{current_info}"

    def get_person(self, name):
        """
        【查詢功能】根據名字從記憶中撈出資料。
        """
        data = self._load_db()
        return data.get(name, None) # 如果找不到，回傳 None

    def delete_person(self, name):
        """
        【刪除功能】當你跟這個人分手了，或者想重來時使用。
        """
        data = self._load_db()
        if name in data:
            del data[name] # 從字典中刪除
            self._save_db(data) # 存檔
            return f"已將【{name}】從記憶庫中永久刪除！"
        return f"記憶庫中找不到【{name}】。"

    def get_all_names(self):
        """
        【清單功能】看看目前記憶庫裡總共記住了哪些人。
        """
        data = self._load_db()
        # 回傳所有的 Key，也就是所有人的名字
        return list(data.keys())