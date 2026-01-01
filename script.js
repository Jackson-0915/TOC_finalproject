// frontend/script.js

// 1. 網頁載入時，自動呼叫重置 API，清空後端記憶
document.addEventListener("DOMContentLoaded", function() {
    fetch("http://127.0.0.1:8000/api/reset", { 
        method: "POST" 
    }).then(response => {
        console.log("後端記憶已重置，現在是全新的開始！");
    });
});

function setMode(mode) {
    let message = "";
    const inputField = document.getElementById("user-input");
    inputField.value = "";

    if (mode === 'date') {
        showDateOptions(); // 顯示約會選項
        return; 
    } else if (mode === 'analysis') {
        message = "我有一段跟曖昧對象的對話紀錄，請幫我分析對方對我的好感度。（請準備好，我等一下貼給你）";
    } else if (mode === 'horoscope') {
        message = "我想測今天的戀愛運勢，請根據星座或抽牌給我建議！";
    }
    inputField.value = message;
    inputField.focus();
}

function showDateOptions() {
    const chatBox = document.getElementById("chat-box");
    const container = document.createElement("div");
    container.className = "message bot-message";
    container.innerHTML = "<p>你想安排哪種風格的約會呢？</p>";
    
    const options = [
        { title: "🎨 文青看展", prompt: "幫我安排去美術館或文創園區的行程" },
        { title: "🌃 浪漫夜景", prompt: "幫我安排去看夜景吃晚餐的行程" },
        { title: "☕ 悠閒咖啡", prompt: "幫我找一家適合聊天的咖啡廳" },
        { title: "🎢 全日瘋玩", prompt: "幫我安排一整天從早到晚的充實約會行程" } 
    ];

    const optionsDiv = document.createElement("div");
    optionsDiv.className = "date-options-container";

    options.forEach(opt => {
        const btn = document.createElement("button");
        btn.innerText = opt.title;
        btn.className = "date-option-btn";
        btn.onclick = function() {
            container.remove(); 
            document.getElementById("user-input").value = opt.prompt; 
            sendMessage(); 
        };
        optionsDiv.appendChild(btn);
    });

    container.appendChild(optionsDiv);
    chatBox.appendChild(container);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
  const inputField = document.getElementById("user-input");
  const message = inputField.value.trim();

  if (!message) return;

  addMessage(message, "user-message");
  inputField.value = ""; 

  const loadingId = addMessage("軍師思考中...", "bot-message");

  try {
      const response = await fetch("http://127.0.0.1:8000/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: message })
      });

      const data = await response.json();

      const loadingDiv = document.querySelector(`div[data-id='${loadingId}']`);
      if (loadingDiv) {
          loadingDiv.innerHTML = marked.parse(data.reply);
          loadingDiv.className = "message bot-message";
          
          if (data.schedules && data.schedules.length > 0) {
              data.schedules.forEach(item => {
                  addCalendarButton(loadingDiv, item.title, item.time);
              });
          }
      } else {
          addMessage(data.reply, "bot-message");
      }

  } catch (error) {
      console.error("Error:", error);
      const loadingDiv = document.querySelector(`div[data-id='${loadingId}']`);
      if (loadingDiv) {
          loadingDiv.innerText = "⚠️ 伺服器忙碌中，請稍後再試。";
          loadingDiv.className = "message bot-message";
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
  
  if (className === 'bot-message') {
      if (text === "軍師思考中...") {
          div.innerText = text;
      } else {
          div.innerHTML = marked.parse(text); 
      }
  } else {
      div.innerText = text;
  }
  
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
  return id;
}

// 2. 防止 Enter 鍵重整網頁 (關鍵修復！)
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); 
        sendMessage();
    }
});

async function resetChat() {
  if (!confirm("確定要清除所有對話紀錄，重新開始嗎？")) return;
  document.getElementById("chat-box").innerHTML = '<div class="message bot-message">記憶已清除！我是你的戀愛軍師，請重新提問。</div>';
  await fetch("http://127.0.0.1:8000/api/reset", { method: "POST" });
}

function addCalendarButton(parentElement, title, timeStr) {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0].replace(/-/g, '');
    const timeFormatted = timeStr.replace(':', '') + '00';
    const startDateTime = `${dateStr}T${timeFormatted}`;
    const endHour = parseInt(timeStr.split(':')[0]) + 2;
    const endDateTime = `${dateStr}T${endHour.toString().padStart(2, '0')}${timeStr.split(':')[1]}00`;
    
    const googleCalUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(title)}&dates=${startDateTime}/${endDateTime}&details=${encodeURIComponent("戀愛軍師幫你安排的行程！")}`;

    const btn = document.createElement("button");
    btn.innerText = `📅 加入行事曆: ${title}`;
    btn.className = "calendar-btn"; 
    btn.onclick = function() { window.open(googleCalUrl, '_blank'); };

    const container = document.createElement("div");
    container.style.marginTop = "10px";
    container.appendChild(btn);
    parentElement.appendChild(container);
}