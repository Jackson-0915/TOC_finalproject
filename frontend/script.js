// 特製按鈕，點下去就會自動填寫已經寫好的一段話，不需要自己慢慢打
function setMode(mode) {
    let message = "";
    if (mode === 'date') {
        message = "請幫我安排一個適合大學生的一日約會行程，風格要青春浪漫。";
    } else if (mode === 'analysis') {
        message = "我有一段跟曖昧對象的對話紀錄，請幫我分析對方對我的好感度，以及我該怎麼回覆。（請準備好，我等一下貼給你）";
    } else if (mode === 'horoscope') {
        message = "我想測今天的戀愛運勢，請給我一些幸運建議！";
    }

    // 找到網頁上的輸入框，把文字輸入進去
    const inputField = document.getElementById("user-input");
    inputField.value = message;

    // 自動按下送出按鈕
    sendMessage();
}

// 負責把訊息送往後端 Python 伺服器，並把回覆拿回來
async function sendMessage() {
    const inputField = document.getElementById("user-input");
    const message = inputField.value.trim(); // 讀取你打了什麼，並去掉前後多餘的空格

    // 如果輸入框是空的，就什麼都不做 (return)
    if (!message) return;

    // addMessage 負責把對話框畫出來
    addMessage(message, "user-message");
    
    // 傳送後把輸入框清空，方便下次輸入
    inputField.value = ""; 

    // 顯示「軍師思考中...」 
    // 先畫出一個空的對話框，讓使用者知道 AI 有在運行
    // 記住這個對話框的 ID，之後會換掉裡面的字
    const loadingId = addMessage("軍師思考中...", "bot-message");

    // 透過網路把訊息傳給後端
    try {
        // 使用 fetch 來呼叫 API
        const response = await fetch("http://127.0.0.1:8000/api/chat", {
            method: "POST", // 使用 POST 方式傳送大量資料
            headers: { "Content-Type": "application/json" }, // 告訴傳送格式
            body: JSON.stringify({ message: message }) // 把文字包裝成 JSON 包裹
        });

        // 等待回傳資料，並解析成 JSON
        const data = await response.json();

        // 找到剛剛記住的對話框
        const loadingDiv = document.querySelector(`div[data-id='${loadingId}']`);
        if (loadingDiv) {
            // AI 常會回傳 Markdown 語法
            // 使用marked.parse(text)把 Markdown 轉成網頁看得懂的 HTML 代碼
            loadingDiv.innerHTML = marked.parse(data.reply); 
            loadingDiv.className = "message bot-message"; // 確保樣式正確   
        } else {
            // 如果找不到剛才那個框，就重新畫一個
            addMessage(data.reply, "bot-message");
        }

    } catch (error) {
        // 如果網路不通、或後端 Python 沒開，就會跑到這裡
        console.error(" Error:", error);
        
        const loadingDiv = document.querySelector(`div[data-id='${loadingId}']`);
        if (loadingDiv) {
            loadingDiv.innerText = "⚠️ 軍師連線逾時，請檢查後端是否開啟 (server.py)。";
            loadingDiv.style.color = "red"; // 顯示紅色的警告字體
        }
    }
}

// 專門在 HTML 畫面上畫出新的對話氣泡
function addMessage(text, className) {
    const chatBox = document.getElementById("chat-box"); // 找到對話容器
    const div = document.createElement("div"); // 建立一個新的區塊
    const id = Date.now(); // 產生一個獨一無二的ID (用時間當 ID)
    
    div.className = `message ${className}`; // 加入 CSS 樣式，決定它是在左邊(bot)還是右邊(user)
    div.setAttribute("data-id", id); // 幫這個區塊貼上身分標籤
    
    // 修復邏輯
    if (className === 'bot-message') {
        // 機器人的話可能包含 Markdown，所以用 innerHTML 解析
        if (text === "軍師思考中...") {
            div.innerText = text;
        } else {
            div.innerHTML = marked.parse(text); 
        }
    } else {
        // 輸入的文字當作純文字處理會比較安全，也能防止 HTML 注入攻擊
        // 讓訊息出現在畫面上
        div.innerText = text; 
    }
    
    chatBox.appendChild(div); // 把做好的氣泡放進聊天室裡
    
    // 自動滾動到底部，確保能看到最新的一句話
    chatBox.scrollTop = chatBox.scrollHeight;
    
    return id; // 把ID傳回去，以方便後續更新內容
}

// 使用 Enter 發送訊息
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});


// 重置對話
async function resetChat() {
    // 彈出一個確認視窗，防止按錯
    if (!confirm("確定要清除所有對話紀錄，重新開始嗎？")) return;

    // 清空網頁上的對話畫面，只留下一句歡迎詞
    document.getElementById("chat-box").innerHTML = 
        '<div class="message bot-message">記憶已清除！我是你的戀愛軍師，請重新提問。</div>';

    try {
        // 通知後端 Python 也把資料庫清空
        await fetch("http://127.0.0.1:8000/api/reset", { method: "POST" });
    } catch (error) {
        alert("重置失敗，請檢查後端連線");
    }
}