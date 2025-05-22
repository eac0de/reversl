document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("file-input");
  const fileButton = document.getElementById("file-button");
  const sendButton = document.getElementById("send-button");
  const fileList = document.getElementById("file-list");
  const fileModal = new bootstrap.Modal(document.getElementById("fileModal"));
  const maxHeight = 150;
  let storedFiles = [];

  const textarea = document.getElementById("message-input");
  function resizeTextarea() {
    textarea.style.height = "auto";
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = `${newHeight}px`;
    textarea.style.overflowY = textarea.scrollHeight > maxHeight ? "auto" : "hidden";
  }
  textarea.addEventListener("input", resizeTextarea);

  function updateFileList() {
    fileList.innerHTML = "";

    storedFiles.forEach((file, index) => {
      const fileItem = document.createElement("div");
      fileItem.className = "d-flex justify-content-between align-items-center border rounded p-2";

      const left = document.createElement("div");
      left.className = "d-flex align-items-center";

      if (file.type.startsWith("image/")) {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.className = "rounded border me-2";
        img.style.maxWidth = "70px";
        img.style.maxHeight = "70px";
        left.appendChild(img);
      }

      const name = document.createElement("div");
      name.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
      left.appendChild(name);

      const deleteBtn = document.createElement("button");
      deleteBtn.className = "btn btn-sm btn-outline-danger ms-2";
      deleteBtn.textContent = "Delete";
      deleteBtn.addEventListener("click", () => {
        storedFiles.splice(index, 1);
        updateFileList();
        if (storedFiles.length === 0) {
          fileModal.hide();
          fileButton.textContent = "Add files";
        }
      });

      fileItem.appendChild(left);
      fileItem.appendChild(deleteBtn);
      fileList.appendChild(fileItem);
    });

    fileButton.textContent = storedFiles.length > 0 ? "View files: " + storedFiles.length : "Add files";
  }

  fileInput.addEventListener("change", () => {
    const newFiles = Array.from(fileInput.files);
    if (newFiles.length + storedFiles.length > 10) {
      alert("You can upload a maximum of 10 files.");
      return;
    }
    storedFiles = [...storedFiles, ...newFiles];
    updateFileList();
    fileInput.value = "";
  });

  fileButton.addEventListener("click", () => {
    if (storedFiles.length === 0) {
      fileInput.click(); // открыть файловый диалог
    } else {
      updateFileList();
      fileModal.show(); // открыть модальное окно
    }
  });
  document.getElementById("add-more-files-btn").addEventListener("click", () => {
    fileInput.click();
  });

  document.getElementById("clear-all-files-btn").addEventListener("click", () => {
    if (confirm("Delete all selected files?")) {
      storedFiles = [];
      updateFileList();
      fileModal.hide();
    }
  });

  const messagesContainer = document.querySelector("#messages");
  let isLoading = false; // Флаг для предотвращения множественных запросов

  // Функция для создания HTML сообщения

  sendButton.addEventListener("click", () => {
    if (!textarea.value.trim() && storedFiles.length === 0) {
      return;
    }
    const formData = new FormData();
    formData.append("csrf_token", window.csrfToken);
    formData.append("text", textarea.value);
    storedFiles.forEach((file) => formData.append("files", file));

    fetch(window.sendMessageURL, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }
      })
      .then(() => {
        textarea.value = "";
        storedFiles = [];
        updateFileList();
        resizeTextarea();
        fileModal.hide();
      })
      .catch(console.error);
  });

  // Функция для загрузки сообщений
  async function loadMoreMessages() {
    if (isLoading) return;
    isLoading = true;
    try {
      const response = await fetch(window.getMessagesListURL + `?offset=${window.messagesOffset}&limit=${window.messagesBatchSize}`);
      if (!response.ok) throw new Error("Failed to fetch messages");
      const messages = await response.json();

      if (messages.length === 0) {
        // Больше сообщений нет
        messagesContainer.removeEventListener("scroll", handleScroll);
        return;
      }

      // Сохраняем высоту контейнера и текущую позицию скролла
      const oldHeight = messagesContainer.scrollHeight;
      const oldScrollTop = messagesContainer.scrollTop;

      // Добавляем сообщения в начало (вверху, из-за flex-column-reverse)
      const fragment = document.createDocumentFragment();
      messages.forEach((data) => {
        fragment.appendChild(createMessageHtml(data));
      });
      messagesContainer.append(fragment);

      // Обновляем смещение
      window.messagesOffset = window.messagesOffset + messages.length;

      // Восстанавливаем позицию скролла
      const newHeight = messagesContainer.scrollHeight;
      messagesContainer.scrollTop = oldScrollTop + (newHeight - oldHeight);
    } catch (error) {
      console.error("Error loading messages:", error);
      alert("Error loading messages:", error);
    } finally {
      isLoading = false;
    }
  }

  // Обработчик прокрутки
  let scrollTimeout;
  function handleScroll() {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      // Проверяем, достигли ли верхнего края контейнера
      const isAtTop = messagesContainer.scrollTop <= 0 && messagesContainer.scrollHeight - messagesContainer.clientHeight <= Math.abs(messagesContainer.scrollTop) + 10;
      if (isAtTop && !window.dataEnd) {
        loadMoreMessages();
      }
    }, 100); // Задержка 100 мс для debounce
  }

  if (window.messagesBatchSize === window.messagesOffset) {
    messagesContainer.addEventListener("scroll", handleScroll);
  }
});
