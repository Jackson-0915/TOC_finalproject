// script.js (前端邏輯修復版)

function setMode(mode) {
  let message = "";
  if (mode === 'date') {
      message = "請幫我安排一個適合大學生的一日約會行程，風格要青春浪漫。";
  } else if (mode === 'analysis') {
      message = "我有一段跟曖昧對象的對話紀錄，請幫我分析對方對我的好感度，以及我該怎麼回覆。（請準備好，我等一下貼給你）";
  } else if (mode === 'horoscope') {
      message = "我想測今天的戀愛運勢，請給我一些幸運建議！";
  }
  const inputField = document.getElementById("user-input");
  inputField.value = message;
  sendMessage();
}

async function sendMessage() {
  const inputField = document.getElementById("user-input");
  const message = inputField.value.trim();

  if (!message) return;

  // 1. 顯示用戶訊息 (這是你之前消失的部分，這裡確保它會執行)
  addMessage(message, "user-message");
  
  // 清空輸入框
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
          loadingDiv.innerHTML = marked.parse(data.reply); 
          loadingDiv.className = "message bot-message";    
      } else {
          addMessage(data.reply, "bot-message");
      }

  } catch (error) {
      console.error("Error:", error);
      
      // 4. 錯誤處理
      const loadingDiv = document.querySelector(`div[data-id='${loadingId}']`);
      if (loadingDiv) {
          loadingDiv.innerText = "⚠️ 軍師連線逾時，請檢查後端是否開啟 (server.py)。";
          loadingDiv.style.color = "red";
      }
  }
}

function addMessage(text, className) {
  const chatBox = document.getElementById("chat-box");
  const div = document.createElement("div");
  const id = Date.now();
  
  div.className = `message ${className}`;
  div.setAttribute("data-id", id);
  
  // ▼▼▼ 關鍵修復點 ▼▼▼
  if (className === 'bot-message') {
      // 如果是機器人，且不是思考中，就用 Markdown
      if (text === "軍師思考中...") {
          div.innerText = text;
      } else {
          div.innerHTML = marked.parse(text); 
      }
  } else {
      // ★ 如果是使用者 (user-message)，強制用純文字顯示
      // 這行如果漏掉，對話框就會是空的！
      div.innerText = text; 
  }
  // ▲▲▲ 修復結束 ▲▲▲
  
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
  return id;
}

document.getElementById("user-input").addEventListener("keypress", function(event) {
  if (event.key === "Enter") sendMessage();
});

async function resetChat() {
  if (!confirm("確定要清除所有對話紀錄，重新開始嗎？")) return;

  document.getElementById("chat-box").innerHTML = 
      '<div class="message bot-message">記憶已清除！我是你的戀愛軍師，請重新提問。</div>';

  try {
      await fetch("http://127.0.0.1:8000/api/reset", { method: "POST" });
  } catch (error) {
      alert("重置失敗，請檢查後端連線");
  }
}