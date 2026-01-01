# relationship_manager.py
import json
import os

DB_FILE = "relationships.json"

class RelationshipManager:
  def __init__(self):
      self._ensure_db_exists()

  def _ensure_db_exists(self):
      if not os.path.exists(DB_FILE):
          with open(DB_FILE, "w", encoding="utf-8") as f:
              json.dump({}, f, ensure_ascii=False, indent=4)

  def _load_db(self):
      try:
          with open(DB_FILE, "r", encoding="utf-8") as f:
              return json.load(f)
      except (json.JSONDecodeError, FileNotFoundError):
          return {}

  def _save_db(self, data):
      with open(DB_FILE, "w", encoding="utf-8") as f:
          json.dump(data, f, ensure_ascii=False, indent=4)

  def save_person(self, name, attributes):
      """
      新增或更新人物資料
      ★ 修正邏輯：針對 '喜好' 欄位進行追加，而非覆蓋。
      """
      data = self._load_db()
      
      if name not in data:
          data[name] = {"info": {}}
      
      # 確保 info 存在
      if "info" not in data[name]:
          data[name]["info"] = {}

      current_info = data[name]["info"]
      new_info = attributes

      for key, value in new_info.items():
          # 特殊邏輯：如果是「喜好」或「討厭」，且原本就有資料，則追加
          if key in ["喜好", "討厭", "地雷"] and key in current_info:
              # 避免重複追加一樣的內容
              if value not in current_info[key]:
                  current_info[key] = f"{current_info[key]}、{value}"
          else:
              # 其他欄位 (如星座、MBTI) 直接覆蓋更新
              current_info[key] = value
      
      # 寫回 update 好的資料
      data[name]["info"] = current_info
      
      self._save_db(data)
      return f"已記錄/更新對象【{name}】的資料：{current_info}"

  def get_person(self, name):
      data = self._load_db()
      return data.get(name, None)

  def delete_person(self, name):
      data = self._load_db()
      if name in data:
          del data[name]
          self._save_db(data)
          return f"已將【{name}】從記憶庫中永久刪除！"
      return f"記憶庫中找不到【{name}】。"

  def get_all_names(self):
      data = self._load_db()
      return list(data.keys())