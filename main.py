# main.py (更新版)
from agent_core import LoveAgent

def main():
  agent = LoveAgent()
  
  print("\n" + "="*50)
  print("💘 戀愛軍師 AI v2.1 (記憶增強版)")
  print("--------------------------------------------------")
  print("💡 指令說明：")
  print(" - 輸入一般文字：與軍師對話")
  print(" - 輸入「reset」：清除對話記憶")
  print(" - 輸入「exit」 ：離開程式")
  print("="*50)

  while True:
      try:
          user_input = input("\n[你] > ")
          
          # ▼▼▼ 處理指令 ▼▼▼
          if user_input.lower() in ["exit", "quit", "88"]:
              print("👋 祝你戀愛順利！")
              break
          
          if user_input.lower() == "reset":
              msg = agent.reset()
              print(f"🤖 {msg}")
              continue
          # ▲▲▲ 處理結束 ▲▲▲

          if not user_input.strip(): continue
          
          print("🤖 軍師思考中...", end="\r")
          reply = agent.chat(user_input)
          
          print(f"\n[軍師]：\n{reply}")
          print("-" * 30)
          
      except KeyboardInterrupt:
          break
      except Exception as e:
          print(f"發生錯誤: {e}")

if __name__ == "__main__":
  main()