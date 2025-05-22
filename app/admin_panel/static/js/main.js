function createMessageHtml(data) {
  const userClass = data.user ? "user-message-justify" : "";
  const bubbleClass = data.user ? "bg-primary text-white" : "bg-light border";
  let html = `
            <div class="mb-3 d-flex ${userClass}">
                <div class="message d-flex flex-column p-2 px-3 rounded-3 ${bubbleClass}">
        `;
  if (data.user) {
    html += `
                <a href="/users?user_uid=${data.user.uid}" 
                   class="bg-secondary p-1 rounded text-white text-decoration-none align-self-center mb-2 small text-break">
                    <i class="bi bi-person-fill"></i> ${data.user.email}
                </a>
            `;
  }
  if (data.text) {
    html += `<div class="mb-1 text-break">${data.text}</div>`;
  }
  if (data.files && data.files.length > 0) {
    data.files.reverse().forEach((file) => {
      if (["image/jpeg", "image/png"].includes(file.mime_type)) {
        html += `
                        <img src="${window.apiPrefix || ""}/admin/api/chats/${window.selectedChatUID}/files/${file.uid}/" 
                             alt="image" class="img-fluid rounded mt-2">
                    `;
      } else {
        html += `
                        <div class="mt-2 small">
                            📎 <a href="${window.apiPrefix || ""}/admin/api/chats/${window.selectedChatUID}/files/${file.uid}/" 
                                  class="text-decoration-underline text-reset" download>${file.name}</a>
                        </div>
                    `;
      }
    });
  }
  html += `</div></div>`;
  const div = document.createElement("div");
  div.innerHTML = html;
  return div.firstElementChild;
}

function createChatListItemHtml(data) {
  let html = `
        <a href="${window.apiPrefix || ""}/admin/chats/?chat_uid=${data.chat_uid}"
            class="list-group-item list-group-item-action">
            Chat ${data.chat_uid}
        </a>
        `;
  const div = document.createElement("div");
  div.innerHTML = html;
  return div.firstElementChild;
}
