const socket = new WebSocket(`ws://${window.location.host}/admin/ws/`);

// Событие при успешном подключении
socket.onopen = function () {};

// Событие при получении сообщения
socket.onmessage = function (event) {
  try {
    const data = JSON.parse(event.data);

    // Пример обработки разных типов сообщений
    if (window.location.href.includes("admin/chats")) {
      if (data.type === "message") {
        if (window.selectedChatUID && window.selectedChatUID === data.chat_uid) {
          fetch(`${window.apiPrefix || ""}/admin/api/chats/${window.selectedChatUID}/messages/${data.message_uid}/`, {
            method: "GET",
          })
            .then((response) => {
              if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
              }
              return response.json();
            })
            .then((msg_data) => {
              const fragment = document.createDocumentFragment();
              fragment.appendChild(createMessageHtml(msg_data));
              document.querySelector("#messages").prepend(fragment);
            });
        } else {
          const chatElement = document.getElementById(`chat-${data.chat_uid}`);
          const parent = chatElement?.parentElement;
          if (chatElement) {
            parent.prepend(chatElement);
          } else {
            const fragment = document.createDocumentFragment();
            fragment.appendChild(createChatListItemHtml(data));
            document.querySelector("#sidebar").children[0].prepend(fragment);
          }
        }
      }
    }
  } catch (err) {
    console.error("Error parsing WebSocket message:", err);
  }
};

// Событие при ошибке
socket.onerror = function (error) {
  console.error("WebSocket error:", error);
};

// Событие при закрытии соединения
socket.onclose = function (event) {
  console.warn("WebSocket closed:", event.reason);
};
