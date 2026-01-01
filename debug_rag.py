# debug_rag.py
import os
import glob
from tools import LoveTools

def diagnose():
    print("========== RAG 健康檢查開始 ==========")
    
    # 1. 檢查當前工作目錄
    current_dir = os.getcwd()
    print(f"📂 當前工作目錄 (PWD): {current_dir}")
    
    # 2. 檢查 knowledge 資料夾是否存在
    knowledge_path = os.path.join(current_dir, "knowledge")
    if os.path.exists(knowledge_path):
        print(f"✅ 找到 knowledge 資料夾: {knowledge_path}")
    else:
        print(f"❌ 【嚴重錯誤】找不到 knowledge 資料夾！程式預期它在這裡: {knowledge_path}")
        return

    # 3. 檢查裡面有沒有 .txt 檔案
    files = glob.glob(os.path.join(knowledge_path, "*.txt"))
    if files:
        print(f"✅ 找到 {len(files)} 個 txt 檔案：")
        for f in files:
            print(f"   - {os.path.basename(f)}")
            # 試讀取內容的前 50 個字
            try:
                with open(f, "r", encoding="utf-8") as file:
                    content = file.read(50)
                    print(f"     👀 內容預覽: {content.strip()}...")
            except Exception as e:
                print(f"     ❌ 讀取失敗: {e}")
    else:
        print("❌ 【錯誤】knowledge 資料夾裡面是空的！或者是副檔名不是 .txt")
        return

    # 4. 測試實際搜尋功能
    test_query = "INTJ"
    print(f"\n🔎 正在測試搜尋關鍵字: '{test_query}'")
    
    # 這裡直接呼叫 LoveTools 的內部讀取功能測試
    result = LoveTools.search_love_strategy(test_query)
    
    if "來源：" in result:
        print("✅ 搜尋成功！RAG 運作正常。")
        print("--- 搜尋結果預覽 ---")
        print(result[:100] + "...")
    else:
        print("❌ 搜尋失敗。雖然有檔案，但搜尋邏輯沒有抓到內容。")
        print(f"回傳結果: {result}")

if __name__ == "__main__":
    diagnose()