import streamlit as st
import requests
import json
from snownlp import SnowNLP

# ================= 1. 設定區 =================
API_KEY = "b2756e656fb26fd9e42017c159087853f35416014d0be4f4ed94a09bb751ca9f"
API_URL = "https://api-gateway.netdb.csie.ncku.edu.tw/api/chat"
MODEL_NAME = "gemma3:4b"

# ================= 2. 工具區 (保持不變) =================

def analyze_sentiment(text):
    """[工具] 情感分析溫度計"""
    try:
        s = SnowNLP(text)
        score = s.sentiments * 100
        if score < 20: evaluation = "極度冷淡 (甚至有點生氣)"
        elif score < 40: evaluation = "敷衍/沒興趣 (軟釘子)"
        elif score < 60: evaluation = "普通/客套 (安全區)"
        elif score < 80: evaluation = "友善/有好感 (曖昧前兆)"
        else: evaluation = "非常熱情 (暈船了)"
        return f"{score:.1f}分 - {evaluation}"
    except:
        return "無法分析 (文字太短或含有非中文)"

def zodiac_compatibility(user_sign, target_sign):
    """[工具] 星座配對查詢"""
    match_db = {
        "火象": ["牡羊", "獅子", "射手"],
        "水象": ["巨蟹", "天蠍", "雙魚"],
        "風象": ["雙子", "天秤", "水瓶"],
        "土象": ["金牛", "處女", "摩羯"]
    }
    def get_element(sign):
        for ele, signs in match_db.items():
            if any(s in sign for s in signs): return ele
        return "未知"

    user_ele = get_element(user_sign)
    target_ele = get_element(target_sign)
    
    if user_ele == "未知" or target_ele == "未知":
        return "無法判斷星座屬性"

    if user_ele == target_ele:
        return f"你們都是 {user_ele}星座，頻率很合！但也容易硬碰硬。"
    elif (user_ele, target_ele) in [("火","風"), ("風","火"), ("水","土"), ("土","水")]:
        return f"{user_ele}與{target_ele}是絕配！互補性很高。"
    else:
        return f"{user_ele}與{target_ele}需要磨合，一個是理性一個是感性。"

# ================= 3. API 溝通核心 (保持不變) =================

def chat_with_llm(messages):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL_NAME, "messages": messages, "stream": False}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        if response.status_code != 200: return f"Error: {response.text}"
        data = response.json()
        if 'message' in data: return data['message']['content']
        elif 'choices' in data: return data['choices'][0]['message']['content']
        return str(data)
    except Exception as e: return f"連線錯誤: {e}"

# ================= 4. Streamlit 網頁主程式 (這裡改動最大) =================

# 設定網頁標題與圖示
st.set_page_config(page_title="戀愛軍師 Agent", page_icon="💘")
st.title("💘 戀愛軍師 (AI Dating Coach)")
st.caption("專治：已讀不回、句點王、直男癌 | Powered by LLM + Sentiment Analysis")

# --- 初始化記憶 (Session State) ---
# 網頁重新整理時，這個變數會幫你記住聊過什麼
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """
         你是一位幽默、毒舌但專業的「戀愛軍師 (Dating Coach)」。
         你的目標是幫助使用者分析曖昧對象的訊息，並提供建議。
         
         【工具使用規則】
         1. 當使用者提供「對方說的話」或詢問「對方語氣」時：
            回傳 {"tool": "sentiment", "text": "對方說的內容"}
         
         2. 當使用者提到「星座」、「配對」或提供雙方星座時：
            回傳 {"tool": "zodiac", "user": "使用者星座", "target": "對方星座"}
            
         3. 如果不需要工具，請直接給出建議或幽默的回覆。
         
         【回答風格】
         請用像 PTT 鄉民或 Dcard 網友的語氣，有點好笑、一針見血，不要太像機器人。
         """}
    ]

# --- 顯示歷史對話 ---
# 把存在記憶裡的每一句話印在畫面上
for msg in st.session_state.messages:
    if msg["role"] != "system": # 系統指令不要印給使用者看
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# --- 接收使用者輸入 ---
if user_input := st.chat_input("請輸入你的煩惱... (例如: 她回我呵呵怎麼辦?)"):
    
    # 1. 顯示並儲存使用者訊息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Agent 思考中...
    with st.chat_message("assistant"):
        with st.spinner("軍師正在掐指一算..."):
            
            # 發送給 LLM
            llm_response = chat_with_llm(st.session_state.messages)
            
            # --- 處理工具呼叫 (Tool Calling) ---
            if '{"tool":' in llm_response:
                try:
                    # 解析 JSON
                    json_str = llm_response[llm_response.find("{"):llm_response.rfind("}")+1]
                    cmd = json.loads(json_str)
                    tool_name = cmd.get("tool")
                    
                    # 執行工具
                    tool_result = ""
                    tool_display_msg = "" # 用來顯示在網頁上的提示
                    
                    if tool_name == "sentiment":
                        tool_result = analyze_sentiment(cmd.get("text"))
                        tool_display_msg = f"🔍 [工具分析] 語氣偵測：{tool_result}"
                    elif tool_name == "zodiac":
                        tool_result = zodiac_compatibility(cmd.get("user"), cmd.get("target"))
                        tool_display_msg = f"✨ [工具分析] 星座配對：{tool_result}"
                    
                    # 在網頁上顯示工具執行結果 (讓使用者知道 Agent 有在做事)
                    st.info(tool_display_msg)
                    
                    # 將工具結果加入記憶
                    st.session_state.messages.append({"role": "assistant", "content": llm_response})
                    st.session_state.messages.append({"role": "system", "content": f"工具回傳：{tool_result}。請根據此結果回答。"})
                    
                    # 拿著工具結果再問一次 LLM
                    final_response = chat_with_llm(st.session_state.messages)
                    st.write(final_response)
                    
                    # 儲存最終回答
                    st.session_state.messages.append({"role": "assistant", "content": final_response})
                    
                except Exception as e:
                    st.error(f"工具執行失敗: {e}")
            else:
                # 一般回答
                st.write(llm_response)
                st.session_state.messages.append({"role": "assistant", "content": llm_response})