# 要在Terminal輸入輸出時，才會使用
from agent_core import LoveAgent

def main():
    """
    這是主程式的執行區塊。
    想像這是一個「無限循環」的聊天視窗，直到你說要離開為止。
    """
    # 初始化
    agent = LoveAgent()
    
    # 輸出漂亮的標題與功能說明
    print("\n" + "="*50)
    print("💘 戀愛軍師 AI v2.1 (記憶增強版)")
    print("--------------------------------------------------")
    print("💡 指令說明：")
    print(" - 輸入一般文字：與軍師對話")
    print(" - 輸入「reset」：清除對話記憶（如果聊壞了就重來）")
    print(" - 輸入「exit」 ：離開程式")
    print("="*50)

    # 進入「無限迴圈」，讓程式一直停留在這裡
    while True:
        try:
            # input() 會停下來，等待使用者在鍵盤輸入內容並按 Enter
            user_input = input("\n[你] > ")
            # 判斷區：檢查使用者是不是輸入了特殊指令
            # 1. 如果輸入 exit, quit 或 88，就跳出迴圈並結束程式
            if user_input.lower() in ["exit", "quit", "88"]:
                print("👋 祝你戀愛順利！掰掰！")
                break
            
            # 2. 如果輸入 reset，就把之前的聊天紀錄清除
            if user_input.lower() == "reset":
                msg = agent.reset() # 呼叫大腦裡的 reset 功能
                print(f"🤖 {msg}")
                continue # 結束這輪對話，直接回到迴圈開頭等待新的輸入

            # 如果使用者什麼都沒打就按 Enter，就略過這次，重新詢問
            if not user_input.strip(): 
                continue
            
            # 顯示一個提示，讓使用者知道程式沒當機，正在算答案
            # \r 的作用是讓文字留在同一行更新
            print("🤖 軍師思考中...", end="\r")
            
            # 把文字傳給 AI 進行分析與處理
            # reply 是 AI 算完後回傳給你的建議文字
            reply = agent.chat(user_input)
            
            # 把 AI 的建議輸出出來
            print(f"\n[軍師]：\n{reply}")
            print("-" * 30)
            
        # 捕捉特定的例外：按下 Ctrl+C，程式會優雅地關閉而不是崩潰
        except KeyboardInterrupt:
            print("\n程式強制關閉。")
            break
        # 捕捉所有其他的錯誤，避免程式因為網路斷線或小 Bug 直接消失
        except Exception as e:
            print(f"發生錯誤了 (╥﹏╥): {e}")

# 如果這個檔案是被直接執行的（不是被別人引用），那就執行 main() 函式
if __name__ == "__main__":
    main()