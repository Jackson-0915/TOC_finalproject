# 大學生戀愛AIng
## 系統介紹
大學三學分：學業、社團、愛情。我們深知，愛情是其中最難修的一門，因為它沒有標準答案。這款工具專為在情感中迷航的你設計，結合 數據分析 與 心理學策略，為直男直女提供約會排程、好感診斷與行動建議。我們不保證百分之百的勝率，但我們保證能讓你在猶豫不決時，擁有最理性的大腦，談一場最不留遺憾的戀愛。\
它還能幫你把約會排程放進Google Calendar裏。
## 專案架構
```text
.
├── index.html                # 網頁介面
├── style.css                 # 網頁樣式表
├── script.js                 # 前端邏輯
├── agent_core.py             # 程式碼核心
├── config.py                 # 設定檔
├── relationship_manager.py   # 記憶管理
├── tools.py                  # 功能包
├── server.py                 # 後端伺服器
├── main.py                   # Terminal測試用
├── credentials.json          # Google Calendar的密鑰（自行生成）
├── StateMachineDiagram.png   # 狀態圖
├── FlowChart.png             # 流程圖
└── knowledge/                # 本地資料庫
    ├── mbti.txt
    ├── 溝通技巧和戀愛術語.txt
    ├── 心理學.txt
    ├── 星座.txt
    └── 其他.txt
```
## 安裝與設定
1.環境
  - Python 3.9+
  - 主要套件（fastapi, uvicorn, requests, duckduckgo-search, google-api-python-client)
  - 網絡環境（用於DuckDuckGo搜索與Google Calendar)

2.安裝

複製指令粘貼在Terminal上就會安裝
```
pip install fastapi uvicorn requests duckduckgo-search google-api-python-client google-auth-httplib2 google-auth-oauthlib pydantic
```

3.自行設定

自行填入api的key及url和想要的模型
```
API_KEY = ""
API_URL = ""
MODEL_NAME = ""
```

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

- 點擊左側選單的「目标对象 (Audience)」
- 在右邊的畫面往下滑，你會看到一個區塊叫做 「测试用户 (Test users)」
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
<img width="2058" height="6162" alt="FlowChart" src="https://github.com/user-attachments/assets/7abbbaf0-18cf-4f4a-9c72-908a0aeb1754" />

## 狀態圖
<img width="15415" height="4800" alt="StateMachineDiagram" src="https://github.com/user-attachments/assets/51373fe3-1caa-4202-bfce-9b5a6e6a0a44" />

## 
