// frontend/script.js

function setMode(mode) {
    let message = "";
    
    // 清除舊的輸入
    const inputField = document.getElementById("user-input");
    inputField.value = "";

    if (mode === 'date') {
        // 模式 1: 顯示約會地點圖卡
        showDateOptions();
        return; 
    } else if (mode === 'analysis') {
        // 模式 2: 對話分析
        message = "我有一段跟曖昧對象的對話紀錄，請幫我分析對方對我的好感度。（請準備好，我等一下貼給你）";
    } else if (mode === 'horoscope') {
        // 模式 3: 運勢
        message = "我想測今天的戀愛運勢，請根據星座或抽牌給我建議！";
    }
    inputField.value = message;
    inputField.focus();
}

async function sendMessage() {
  const inputField = document.getElementById("user-input");
  const message = inputField.value.trim();

  if (!message) return;

  // 1. 顯示用戶訊息 (右邊, 不用 Markdown)
  addMessage(message, "user-message");
  inputField.value = ""; 

  // 2. 顯示 "思考中..." (左邊)
  const loadingId = addMessage("軍師思考中...", "bot-message");

  try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: message })
      });

      const data = await response.json();

      // 3. 更新機器人回覆 (使用 Markdown 解析)
      const loadingDiv = document.querySelector(`div[data-id='${loadingId}']`);
      if (loadingDiv) {
          loadingDiv.innerHTML = marked.parse(data.reply); // ▼ 關鍵：解析 Markdown
          loadingDiv.className = "message bot-message";    // 確保樣式正確
          
          // 如果有行程資料，顯示加入行事曆按鈕
          if (data.schedule) {
            addCalendarButton(loadingDiv, data.schedule.title, data.schedule.time);
          }
      } else {
          addMessage(data.reply, "bot-message");
      }

  } catch (error) {
      console.error("Error:", error);
      
      // 4. 錯誤處理：直接修改原本的思考氣泡
      const loadingDiv = document.querySelector(`div[data-id='${loadingId}']`);
      
      if (loadingDiv) {
          loadingDiv.innerText = "⚠️ 軍師連線逾時 (NCKU 伺服器忙碌)，請再試一次或是按右上角重置。";
          loadingDiv.className = "message bot-message"; // 保持在左邊
          loadingDiv.style.color = "red";               // 變紅字
          loadingDiv.style.fontWeight = "bold";
      } else {
          const errorId = addMessage("⚠️ 伺服器連線錯誤", "bot-message");
          document.querySelector(`div[data-id='${errorId}']`).style.color = "red";
      }
  }
}

function addMessage(text, className) {
  const chatBox = document.getElementById("chat-box");
  const div = document.createElement("div");
  const id = Date.now();
  
  div.className = `message ${className}`;
  div.setAttribute("data-id", id);
  
  // ▼ 關鍵：如果是機器人回覆，就開啟 Markdown 解析
  if (className === 'bot-message') {
      // 為了避免一開始 "軍師思考中..." 被當成 Markdown 解析出錯，加個判斷
      if (text === "軍師思考中...") {
          div.innerText = text;
      } else {
          div.innerHTML = marked.parse(text); 
      }
  } else {
      div.innerText = text; // 使用者訊息維持純文字，避免 XSS 攻擊
  }
  
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
  return id;
}

document.getElementById("user-input").addEventListener("keypress", function(event) {
  if (event.key === "Enter") sendMessage();
});

async function resetChat() {
  if (!confirm("確定要清除所有對話紀錄，重新開始嗎？")) return;

  // 清空畫面
  document.getElementById("chat-box").innerHTML = 
      '<div class="message bot-message">記憶已清除！我是你的戀愛軍師，請重新提問。</div>';

  try {
      await fetch("http://127.0.0.1:8000/api/reset", { method: "POST" });
  } catch (error) {
      alert("重置失敗，請檢查後端連線");
  }
}

function addCalendarButton(parentElement, title, timeStr) {
    // 1. 計算時間 (預設明天)
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    
    const dateStr = tomorrow.toISOString().split('T')[0].replace(/-/g, '');
    const timeFormatted = timeStr.replace(':', '') + '00';
    
    // Google Calendar 格式: YYYYMMDDTHHMMSS
    const startDateTime = `${dateStr}T${timeFormatted}`;
    // 預設活動 2 小時
    const endHour = parseInt(timeStr.split(':')[0]) + 2;
    const endDateTime = `${dateStr}T${endHour.toString().padStart(2, '0')}${timeStr.split(':')[1]}00`;
    
    const googleCalUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(title)}&dates=${startDateTime}/${endDateTime}&details=${encodeURIComponent("戀愛軍師幫你安排的行程！")}`;

    // 2. 建立按鈕
    const btn = document.createElement("button");
    btn.innerText = "📅 加入 Google 行事曆";
    btn.className = "calendar-btn"; 
    btn.onclick = function() {
        window.open(googleCalUrl, '_blank');
    };

    const container = document.createElement("div");
    container.style.marginTop = "10px";
    container.appendChild(btn);
    parentElement.appendChild(container);
}