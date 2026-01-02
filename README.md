# 大學生戀愛AIng
## 動機介紹
大學三學分：學業、社團、愛情。我們深知，愛情是其中最難修的一門，因為它沒有標準答案。這款工具專為在情感中迷航的你設計，結合 數據分析 與 心理學策略，為直男直女提供約會排程、好感診斷與行動建議，也能幫你把約會排程放進Google Calendar裏。我們不保證百分之百的勝率，但我們保證能讓你在猶豫不決時，擁有最理性的大腦，談一場最不留遺憾的戀愛。

## 🚀 專案技術核心亮點

1. **雙階層 LLM 決策鏈 (Two-Stage Reasoning)：**

第一層：意圖偵測模型 (Temperature: 0.1)。嚴格解析使用者指令，決定是否啟動外部工具 (Tool Calling)。

第二層：人格化回覆模型 (Temperature: 0.7)。結合工具回傳數據與人設 Prompt，生成具備共情能力的建議。

2. **自主性人物檔案管理系統 (Persistence Identity Memory)：**

實作一個 Persistent Data Layer，系統會自動辨識對話中的名字與特徵（MBTI、星座、地雷），並將其儲存於本地 JSON 知識庫。

Context Injection：對話時自動檢索 (Retrieval) 相關對象檔案並注入 Prompt，解決 LLM 長期記憶不足的痛點。

3. **異質工具整合 (Heterogeneous Tooling)：**

Heuristic Algorithm：內建「鏡像行為行為」檢測算法，量化對話好感度。

OAuth 2.0 整合：完整實作 Google API 授權流程，實現自動化行程同步。

Hybrid Search：優先檢索本地專家知識庫 (Local KB)，無果後自動切換至 DuckDuckGo 聯網搜尋。

Google Calendar API：自動同步約會行程。

## 🛠️ 工具箱實現 (LoveTools.py)
本專案開發了五大核心工具，賦予軍師 Agent 行動能力：

1. 知識庫載入器：支援 .txt 格式的本地攻略本，實作緩存機制 (Cache) 減少硬碟讀取次數。

2. 聯網搜尋器：整合 DuckDuckGo Search，讓軍師能回答當前最新的流行話題或地點。

3. 情感演算法：自定義關鍵字權重表，並引入「鏡像行為檢測」邏輯，量化曖昧對話的好感度。

4. 時間標準化引擎：使用 datetime 模組解決 LLM 回傳時間格式不一的問題。

5. Google 行事曆同步：透過 google-api-python-client 實現自動化約會排程，將虛擬建議轉化為真實行動。

## 專案架構
```text
.
Love_Agent_Project/
├── backend_logic/              # [後端邏輯區] 存放所有 Python 核心功能
│   ├── agent_core.py           # 決策核心
│   ├── relationship_manager.py # 記憶管理
│   ├── tools.py                # 功能工具包
│   └── config.py               # 系統設定
│
├── frontend/                   # [前端介面區] 存放網頁相關檔案
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── knowledge/                  # [本地資料庫] 存放 RAG 用的文字檔
│   ├── mbti.txt
│   ├── 溝通技巧和戀愛術語.txt
│   ├── 心理學.txt
│   ├── 星座.txt
│   └── 其他.txt
│
├── assets/                     # [圖表與文檔] 存放作業要求的圖示
│   ├── StateMachineDiagram.png
│   └── FlowChart.png
│
├── server.py                   # [伺服器啟動點] 主程式入口
├── main.py                     # [測試腳本] Terminal 測試用
├── credentials.json            # [金鑰] Google API 密鑰
└── .gitignore                  # [Git 忽略清單] (保護隱私)
```

## 技術架構

- 前端：HTML, CSS, JavaScript, Marked.js
- 後端: Python, FastAPI, Uvicorn, Pydantic
- LLM服務: RAG, Function Calling, Ollama API
- 外部服務整合: Google Calendar API, DuckDuckGo Search
- 資料儲存: JSON File Storage

## 安裝與設定
1.環境
  - Python 3.9+
  - 主要套件（fastapi, uvicorn, requests, duckduckgo-search, google-api-python-client)
  - 網絡環境（用於DuckDuckGo搜索與Google Calendar)

2. 安裝



複製指令粘貼在Terminal上就會安裝

```
pip install fastapi uvicorn requests duckduckgo-search google-api-python-client google-auth-httplib2 google-auth-oauthlib pydantic
```



3. Clone 專案

```
git clone https://github.com/Jackson-0915/TOC_finalproject.git
```



4. 自行設定



自行填入api的key及url和想要的模型

```
API_KEY = ""
API_URL = ""
MODEL_NAME = ""
```



5. 運行檔案

- 在Terminal上輸入

```
python -m uvicorn server:app --reload
```

- 打開index.html<br>

## 如何自行生成credentials.json
打開瀏覽器，前往 [Google 雲端控制臺](https://console.cloud.google.com/)， 登錄Google賬號
### 第一階段：建立專案
1. 進入首頁後，點擊左上角的 「選取專案」（或你現有的專案名稱）
2. 在跳出的視窗右上角，點擊 「建立專案 (NEW PROJECT)」
3. 專案名稱：隨便取
4. 位置：選「無機構」即可
5. 點擊 「建立 (CREATE)」
6. 等待幾秒鐘，右上角會跳出通知說建立了，點擊 「選取專案」 確保你現在是在這個新專案裡面

### 第二階段：啟用 Google Calendar API
1. 點擊左上角的 漢堡選單 (≡) -> 「API 和服務」 -> 「已啟用的 API 和服務」
2. 點擊上方中間的 「+ 啟用 API 和服務 (+ ENABLE APIS AND SERVICES)」
3. 在搜尋框輸入：Google Calendar API
4. 點擊搜尋結果中的 Google Calendar API 卡片
5. 點擊藍色的 「啟用 (ENABLE)」 按鈕，等畫面跳轉可能需要一點時間

### 第三階段：設定 OAuth 同意畫面
<img width="3839" height="1918" alt="Screenshot 2026-01-01 222243" src="https://github.com/user-attachments/assets/1421dbc2-5a64-4abd-9c86-74e40f012038" />

1. 點擊藍色的「開始 (Start)」
2. User Type (使用者類型)選擇 「外部 (External)」
3. 填寫應用程式資訊：
    - 應用程式名稱：填 AiAgent(隨便填也可以)
    - 使用者支援電子郵件：自己的 Email
    - 開發人員聯絡資訊：自己的 Email
    - 其他欄位留空
    - 按「儲存並繼續」
4. 加入測試使用者 (Add Users)：

<img width="3839" height="1918" alt="Screenshot 2026-01-01 222455" src="https://github.com/user-attachments/assets/3ab1e758-46fb-4be9-b9ad-4a3ddc1d4001" />

- 點擊左側選單的「目標對象 (Audience)」
- 在右邊的畫面往下滑，你會看到一個區塊叫做 「測試用户 (Test users)」
- 點擊 「+ ADD USERS (添加用户)」
- 輸入 Google Email，然後儲存

### 第四階段：建立憑證
1. 點擊左側選單的 「憑證 (Credentials)」
2. 點擊上方 「+ 建立憑證 (+ CREATE CREDENTIALS)」 -> 選擇 「OAuth 用戶端 ID (OAuth client ID)」
3. 請選擇「電腦版應用程式 (Desktop app)」
4. 名稱：保持預設 (Desktop client 1) 或隨便取名
5. 點擊 「建立 (CREATE)」
6. 看到下載的圖示就點下去
7. 改名credentials.json

## 流程圖
<img width="2321" height="5532" alt="FlowChart" src="https://github.com/user-attachments/assets/ff56d372-1eeb-4785-8a87-d7643743868c" />

## 狀態圖
<img width="15415" height="4800" alt="StateMachineDiagram" src="https://github.com/user-attachments/assets/5b64029a-66a3-4b96-b1aa-4e1e2974981a" />

## 問題挑戰
1. Q : 多輪對話中的上下文遺失<br>
   A : 上下文指針：在 LoveAgent 類別中實作 self.current_topic_person 變數，用來記憶「當前正在討論的對象」<br>
動態指代修正：在存檔邏輯中加入攔截層，若偵測到 name 為代名詞（他/她），程式自動將其替換為記憶中的 current_topic_person，確保資料寫入正確的對象檔案<br>
2. Q : 資料幻覺與結構化資料清洗<br>
   A : 後處理清洗管道：實作 sanitize_info 函式。在寫入 DB 前，透過 RegEx 和關鍵字邏輯（如：強制 4 字母為 MBTI、含「座」字為星座）強制修正 Key-Value<br>
智能追加邏輯：重寫資料庫管理層 (RelationshipManager)，針對「喜好/地雷」等列表型欄位採用 Append 模式（用逗號串接），確保新舊資訊並存<br>
3. Q : LLM 無法直接在對話中同時完成「聊天」和「存檔/搜尋」<br>
   A : 實作「雙階段推理架構 (Two-Stage Inference Pipeline)」：<br>
階段一 (Intent Detection)：設計一個專門的 tool_selector_prompt，強迫模型只輸出 JSON 格式的指令（如 {"tool": "save_profile", ...}），完全禁止閒聊<br>
階段二 (Response Generation)：接收工具執行的結果（如「存檔成功」），將其作為 System Message 注入給第二個 Prompt（軍師人格），讓軍師根據系統回報來生成最終回覆<br>
4. Q : 意圖優先級衝突與指令遵循<br>
   A : Prompt 工程優化：在 System Prompt 中加入 CRITICAL PRIORITY 區塊，明確定義規則：「只要出現新資訊，必須優先執行 save_profile，即使有問句也要先存檔」<br>系統提示注入：工具執行完畢後，不直接結束，而是將「存檔成功」的結果作為 System Message 插入對話歷史，強迫 LLM 在「已知資料已更新」的前提下，繼續回答使用者的問題<br>

## 未來擴充
1. 網路爬蟲：RAG可以擴充資料來源

2. 包裝客自化：環境外觀可自訂義

3. 多模態分析：未來可整合電腦視覺，分析曖昧對象的照片表情或穿搭。

4. LINE/Telegram Bot 整合：將此 Agent 封裝至通訊軟體，達成 24 小時即時軍師提醒。

5. AP (人工性格)：有助於為理解或是開發提供靈感

## 參考資料
1. [如何下prompt]https://raymondhouch.com/lifehacker/digital-workflow/chatgpt-prompt-engineering/

2. [新手入門指南：一步步打造你的 AI 智能代理]https://thunderbit.com/zh-Hant/blog/how-to-build-ai-agent

3. [如何設計自己的 AI Agent 框架]https://blog.aotoki.me/posts/2025/01/15/design-your-ai-agent-framework/

4. [打造超级AI Agent自动化]https://zhuanlan.zhihu.com/p/1987718068210787107

5. [从零开始：用Python和Gemini四步搭建你自己的AI Agent]https://cloud.tencent.cn/developer/article/2607772
