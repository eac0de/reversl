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

    fileButton.textContent = storedFiles.length > 0 ? "View files" : "Add files";
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

  sendButton.addEventListener("click", () => {
    const formData = new FormData();
    formData.append("csrf_token", window.csrfToken);
    formData.append("text", textarea.value);
    storedFiles.forEach((file) => formData.append("files", file));

    fetch(window.sendMessageURL, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then(() => {
        textarea.value = "";
        storedFiles = [];
        updateFileList();
        resizeTextarea();
        fileModal.hide();
      })
      .catch(console.error);
  });
});
